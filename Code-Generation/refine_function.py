#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dspy-ai",
#     "rich",
#     "python-dotenv",
#     "pyyaml",
# ]
# ///

import dspy
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml
import time
import subprocess
from datetime import datetime

console = Console()


def strip_markdown_fences(code: str) -> str:
    """Remove markdown code fences if present."""
    lines = code.strip().split('\n')

    # Check if wrapped in markdown fences
    if lines[0].startswith('```'):
        lines = lines[1:]  # Remove opening fence
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]  # Remove closing fence

    return '\n'.join(lines)


class FunctionGenerator(dspy.Signature):
    """Generate a Python function implementation based on a type signature."""

    type_signature = dspy.InputField(desc="The function type signature (e.g., 'def add(x: int, y: int) -> int')")
    implementation = dspy.OutputField(desc="Complete Python function implementation with docstring")


class FunctionRefiner(dspy.Signature):
    """Refine a Python function implementation based on type checking feedback."""

    original_code = dspy.InputField(desc="The original Python function implementation")
    type_errors = dspy.InputField(desc="Type checking errors and warnings from the type checker")
    refined_implementation = dspy.OutputField(desc="Refined Python function implementation that fixes the type errors")


class IterativeRefiner:
    """Generate and iteratively refine a function using type checking."""

    def __init__(self, model: str):
        """Initialize with a specific model."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Check your .env file.")

        self.model = model
        self.lm = dspy.LM(
            model=f"openrouter/{model}",
            api_key=self.api_key,
            api_base="https://openrouter.ai/api/v1"
        )
        dspy.configure(lm=self.lm)

        self.generator = dspy.ChainOfThought(FunctionGenerator)
        self.refiner = dspy.ChainOfThought(FunctionRefiner)

    def generate_initial(self, type_signature: str) -> tuple[str, float]:
        """Generate initial function implementation."""
        console.print(f"[cyan]Generating initial implementation with {self.model}...[/cyan]")

        start_time = time.time()
        result = self.generator(type_signature=type_signature)
        elapsed = time.time() - start_time

        # Strip markdown fences if present
        code = strip_markdown_fences(result.implementation)

        return code, elapsed

    def run_type_checker(self, code: str, temp_file: Path) -> tuple[bool, str]:
        """Run uvx ty check on the code and return success status and output."""
        # Write code to temp file
        temp_file.write_text(code)

        try:
            # Run uvx ty check
            result = subprocess.run(
                ["uvx", "ty", "check", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            return success, output
        except subprocess.TimeoutExpired:
            return False, "Type checker timed out"
        except FileNotFoundError:
            return False, "uvx or ty not found. Install with: uv tool install ty"
        except Exception as e:
            return False, f"Error running type checker: {str(e)}"

    def refine_with_feedback(self, code: str, type_errors: str) -> tuple[str, float]:
        """Refine the code based on type checking feedback."""
        start_time = time.time()
        result = self.refiner(original_code=code, type_errors=type_errors)
        elapsed = time.time() - start_time

        # Strip markdown fences if present
        refined = strip_markdown_fences(result.refined_implementation)

        return refined, elapsed

    def refine_iteratively(
        self,
        type_signature: str,
        output_dir: Path,
        max_iterations: int = 3
    ) -> dict:
        """Generate and iteratively refine a function."""

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = output_dir / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)

        temp_file = run_dir / "temp_check.py"

        # Generate initial implementation
        code, gen_time = self.generate_initial(type_signature)

        # Save initial version
        initial_file = run_dir / "iteration_0_initial.py"
        initial_file.write_text(code)

        console.print(f"[green]Initial implementation saved:[/green] {initial_file.name}")

        # Display initial code
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Initial Implementation"))

        iterations = []
        current_code = code

        # Iteration 0 - initial generation
        type_ok, type_output = self.run_type_checker(current_code, temp_file)
        iterations.append({
            'iteration': 0,
            'type': 'initial_generation',
            'time_seconds': round(gen_time, 3),
            'type_check_passed': type_ok,
            'type_checker_output': type_output,
            'file': str(initial_file.relative_to(output_dir))
        })

        console.print(f"[yellow]Type check:[/yellow] {'PASS' if type_ok else 'FAIL'}")
        if not type_ok:
            console.print(f"[red]Type errors:[/red]\n{type_output}")

        # Iterative refinement
        for i in range(1, max_iterations + 1):
            if type_ok:
                console.print(f"[green]Type checking passed! No refinement needed.[/green]")
                break

            console.print(f"\n[cyan]Iteration {i}: Refining based on type errors...[/cyan]")

            # Refine based on type errors
            refined_code, refine_time = self.refine_with_feedback(current_code, type_output)

            # Save refined version
            refined_file = run_dir / f"iteration_{i}_refined.py"
            refined_file.write_text(refined_code)

            console.print(f"[green]Refined version saved:[/green] {refined_file.name}")

            # Display refined code
            syntax = Syntax(refined_code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Iteration {i} - Refined"))

            # Type check refined version
            type_ok, type_output = self.run_type_checker(refined_code, temp_file)

            iterations.append({
                'iteration': i,
                'type': 'refinement',
                'time_seconds': round(refine_time, 3),
                'type_check_passed': type_ok,
                'type_checker_output': type_output,
                'file': str(refined_file.relative_to(output_dir))
            })

            console.print(f"[yellow]Type check:[/yellow] {'PASS' if type_ok else 'FAIL'}")
            if not type_ok:
                console.print(f"[red]Type errors:[/red]\n{type_output}")

            current_code = refined_code

        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()

        # Save metrics
        total_time = sum(iter['time_seconds'] for iter in iterations)
        metrics = {
            'metadata': {
                'timestamp': timestamp,
                'model': self.model,
                'type_signature': type_signature,
                'max_iterations': max_iterations,
                'total_time_seconds': round(total_time, 3),
                'final_type_check_passed': type_ok
            },
            'iterations': iterations
        }

        metrics_file = run_dir / 'metrics.yaml'
        with open(metrics_file, 'w') as f:
            yaml.dump(metrics, f, default_flow_style=False, sort_keys=False)

        console.print(f"\n[green]Metrics saved:[/green] {metrics_file}")

        return metrics


def main():
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    if len(sys.argv) < 3:
        console.print("[red]Usage:[/red] refine_function.py <model> '<type_signature>' [max_iterations]")
        console.print("\n[yellow]Examples:[/yellow]")
        console.print("  refine_function.py 'meta-llama/llama-3.1-8b-instruct' 'def fibonacci(n: int) -> int'")
        console.print("  refine_function.py 'mistralai/mistral-7b-instruct' 'def sort(items: list[int]) -> list[int]' 5")
        console.print("\n[yellow]Available small models:[/yellow]")
        console.print("  - meta-llama/llama-3.1-8b-instruct")
        console.print("  - mistralai/mistral-7b-instruct")
        console.print("  - anthropic/claude-3-haiku")
        console.print("  - openai/gpt-3.5-turbo")
        sys.exit(1)

    model = sys.argv[1]
    type_signature = sys.argv[2]
    max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    # Setup output directory
    output_dir = Path(__file__).parent / "refinements"
    output_dir.mkdir(exist_ok=True)

    console.print(f"\n[bold cyan]Model:[/bold cyan] {model}")
    console.print(f"[bold cyan]Type Signature:[/bold cyan] {type_signature}")
    console.print(f"[bold cyan]Max Iterations:[/bold cyan] {max_iterations}\n")

    # Run refinement process
    refiner = IterativeRefiner(model)
    metrics = refiner.refine_iteratively(type_signature, output_dir, max_iterations)

    # Display summary
    console.print("\n[bold green]Refinement Complete![/bold green]")
    console.print(f"Total time: {metrics['metadata']['total_time_seconds']}s")
    console.print(f"Final result: {'PASS' if metrics['metadata']['final_type_check_passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()
