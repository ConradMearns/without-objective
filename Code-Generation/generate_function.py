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
from rich.console import Console
from rich.syntax import Syntax
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

console = Console()


class FunctionGenerator(dspy.Signature):
    """Generate a Python function implementation based on a type signature."""

    type_signature = dspy.InputField(desc="The function type signature (e.g., 'def add(x: int, y: int) -> int')")
    implementation = dspy.OutputField(desc="Complete Python function implementation with docstring")


class CodeGenerator:
    def __init__(self, model="openrouter/anthropic/claude-3.5-sonnet"):
        """Initialize the code generator with a language model."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Check your .env file.")

        self.lm = dspy.LM(
            model=model,
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1"
        )
        dspy.configure(lm=self.lm)
        self.generator = dspy.ChainOfThought(FunctionGenerator)

    def generate(self, type_signature: str) -> str:
        """Generate a function implementation from a type signature."""
        result = self.generator(type_signature=type_signature)
        return result.implementation


def main():
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] generate_function.py '<type_signature>'")
        console.print("\n[yellow]Example:[/yellow]")
        console.print("  generate_function.py 'def fibonacci(n: int) -> int'")
        sys.exit(1)

    type_signature = sys.argv[1]

    console.print(f"\n[bold cyan]Type Signature:[/bold cyan] {type_signature}\n")
    console.print("[dim]Generating function implementation...[/dim]\n")

    # Initialize generator with OpenRouter
    generator = CodeGenerator()

    # Generate the function
    implementation = generator.generate(type_signature)

    # Display the generated code
    console.print("[bold green]Generated Implementation:[/bold green]\n")
    syntax = Syntax(implementation, "python", theme="monokai", line_numbers=True)
    console.print(syntax)


if __name__ == "__main__":
    main()
