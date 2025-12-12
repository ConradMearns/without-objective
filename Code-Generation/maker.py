#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dspy-ai",
#     "rich",
#     "python-dotenv",
# ]
# ///

import dspy
from typing import List, Tuple, Optional, Callable
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

console = Console()

# 1. SIGNATURE for single-step agent
class SingleStepTask(dspy.Signature):
    """Execute one step of a multi-step task given current context."""
    strategy = dspy.InputField(desc="Overall strategy/rules")
    current_state = dspy.InputField(desc="Current state")
    previous_action = dspy.InputField(desc="Previous action taken")

    next_action = dspy.OutputField(desc="Next action to take")
    next_state = dspy.OutputField(desc="Resulting state")

# 2. RED-FLAGGING validator
def is_valid_response(response, max_tokens=750):
    """Check if response should be red-flagged."""
    try:
        # Validate structure - response is a Prediction object
        if not hasattr(response, 'next_action') or not hasattr(response, 'next_state'):
            return False

        if not response.next_action or not response.next_state:
            return False

        # Length check on the actual string fields
        action_tokens = len(str(response.next_action).split())
        state_tokens = len(str(response.next_state).split())

        if action_tokens + state_tokens > max_tokens:
            return False

        return True
    except Exception:
        return False

# 3. VOTING MODULE with first-to-ahead-by-k
class VotingPredictor(dspy.Module):
    def __init__(self, k=3, temperature=0.1):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SingleStepTask)
        self.k = k
        self.temperature = temperature

    def forward(self, strategy, current_state, previous_action):
        votes = {}  # Maps candidate -> count

        while True:
            # Sample with temperature (first call at temp=0)
            temp = 0 if len(votes) == 0 else self.temperature

            with dspy.settings.context(temperature=temp):
                response = self.predictor(
                    strategy=strategy,
                    current_state=current_state,
                    previous_action=previous_action
                )

            # Red-flag check
            if not is_valid_response(response):
                continue  # Resample

            # Create candidate key (action + state tuple)
            candidate = (response.next_action, response.next_state)
            votes[candidate] = votes.get(candidate, 0) + 1

            # Check if any candidate is ahead by k
            max_votes = max(votes.values())
            second_max = sorted(votes.values(), reverse=True)[1] if len(votes) > 1 else 0

            if max_votes >= self.k + second_max:
                # Winner found
                winner = max(votes.keys(), key=lambda c: votes[c])
                return dspy.Prediction(
                    next_action=winner[0],
                    next_state=winner[1]
                )

# 4. MAIN COORDINATOR - chains steps together
class MAKERSystem(dspy.Module):
    def __init__(self, k=3, max_steps=None):
        super().__init__()
        self.voting_predictor = VotingPredictor(k=k)
        self.max_steps = max_steps

    def forward(self, initial_state, strategy, goal_check_fn):
        """
        Execute task until goal is reached.

        Args:
            initial_state: Starting state
            strategy: Task-specific strategy/rules
            goal_check_fn: Function to check if goal reached
        """
        current_state = initial_state
        previous_action = None
        actions = []
        step_count = 0

        while not goal_check_fn(current_state):
            if self.max_steps and step_count >= self.max_steps:
                break

            # Get next step via voting
            result = self.voting_predictor(
                strategy=strategy,
                current_state=current_state,
                previous_action=previous_action
            )

            # Update state
            actions.append(result.next_action)
            current_state = result.next_state
            previous_action = result.next_action
            step_count += 1

        return dspy.Prediction(
            actions=actions,
            final_state=current_state,
            steps=step_count
        )


# Helper functions for Tower of Hanoi
def make_initial_state(n_disks: int) -> str:
    """Create initial state string for N disks"""
    peg0 = list(range(n_disks, 0, -1))  # [N, N-1, ..., 2, 1]
    return str([peg0, [], []])

def make_goal_state(n_disks: int) -> str:
    """Create goal state string for N disks"""
    peg2 = list(range(n_disks, 0, -1))  # [N, N-1, ..., 2, 1]
    return str([[], [], peg2])

def is_goal_reached(current_state: str, goal_state: str) -> bool:
    """Check if we've reached the goal"""
    # Parse string states and compare
    import ast
    current = ast.literal_eval(current_state)
    goal = ast.literal_eval(goal_state)
    return current == goal


if __name__ == "__main__":
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="MAKER System - Tower of Hanoi Solver")
    parser.add_argument(
        "--model",
        type=str,
        default="openrouter/mistralai/mistral-7b-instruct",
        help="Model to use (default: llama-3.1-8b-instruct)"
    )
    parser.add_argument(
        "--disks",
        type=int,
        default=5,
        help="Number of disks to solve (default: 5)"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=3,
        help="Voting threshold k (default: 3)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="Maximum steps before stopping (default: 100)"
    )
    args = parser.parse_args()

    # Configure DSPy with OpenRouter
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] OPENROUTER_API_KEY not found in environment.")
        console.print("Create a .env file with: OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)

    console.print(f"[cyan]Model:[/cyan] {args.model}")
    console.print(f"[cyan]Disks:[/cyan] {args.disks} (expected steps: {2**args.disks - 1})")
    console.print(f"[cyan]Voting k:[/cyan] {args.k}")
    console.print()

    lm = dspy.LM(
        model=args.model,
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
        temperature=0.1
    )
    dspy.configure(lm=lm)

    # Initialize system
    maker = MAKERSystem(k=args.k, max_steps=args.max_steps)

    # Define strategy
    strategy = f"""
You are solving Towers of Hanoi with {args.disks} disks.

Rules:
- Only move one disk at a time
- Only move the top disk from a stack
- Never place a larger disk on a smaller disk
- Pegs are numbered 0, 1, 2

Strategy for EVEN number of disks:
1. If previous move was NOT disk 1: move disk 1 clockwise (0→1→2→0)
2. If previous move WAS disk 1: make the only legal move that doesn't involve disk 1

State format: [[peg0 disks], [peg1 disks], [peg2 disks]]
Each peg lists disks from BOTTOM to TOP.
Example: [[3,2,1], [], []] means disk 3 at bottom, disk 1 on top of peg 0.

Move format: [disk_number, from_peg, to_peg]
"""

    # Setup states
    initial = make_initial_state(args.disks)
    goal = make_goal_state(args.disks)

    console.print(f"[bold]Initial state:[/bold] {initial}")
    console.print(f"[bold]Goal state:[/bold] {goal}")
    console.print("\n[dim]Starting solution...[/dim]\n")

    # Run
    result = maker(
        initial_state=initial,
        strategy=strategy,
        goal_check_fn=lambda s: is_goal_reached(s, goal)
    )

    console.print(f"\n{'='*60}")
    console.print(f"[green]✓ Solution found![/green]")
    console.print(f"[bold]Steps taken:[/bold] {result.steps}")
    console.print(f"[bold]Expected:[/bold] {2**args.disks - 1}")
    console.print(f"[bold]Final state:[/bold] {result.final_state}")
    console.print(f"\n[bold]Actions:[/bold]")
    for i, action in enumerate(result.actions, 1):
        console.print(f"  {i}. {action}")
