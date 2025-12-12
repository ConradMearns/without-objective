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
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml
import time
from datetime import datetime

console = Console()


class FunctionGenerator(dspy.Signature):
    """Generate a Python function implementation based on a type signature."""

    type_signature = dspy.InputField(desc="The function type signature (e.g., 'def add(x: int, y: int) -> int')")
    implementation = dspy.OutputField(desc="Complete Python function implementation with docstring")


class ModelComparison:
    """Compare function generation across multiple models."""

    # Define models to test - mix of sizes and providers
    MODELS = [
        # Large models
        {"name": "claude-3.5-sonnet", "id": "openrouter/anthropic/claude-3.5-sonnet", "tier": "large"},
        {"name": "gpt-4", "id": "openrouter/openai/gpt-4", "tier": "large"},

        # Medium models
        {"name": "claude-3-haiku", "id": "openrouter/anthropic/claude-3-haiku", "tier": "medium"},
        {"name": "gpt-3.5-turbo", "id": "openrouter/openai/gpt-3.5-turbo", "tier": "medium"},

        # Small/fast models
        {"name": "llama-3.1-8b", "id": "openrouter/meta-llama/llama-3.1-8b-instruct", "tier": "small"},
        {"name": "mistral-7b", "id": "openrouter/mistralai/mistral-7b-instruct", "tier": "small"},
        {"name": "qwen-7b", "id": "openrouter/qwen/qwen-2-7b-instruct", "tier": "small"},
    ]

    def __init__(self):
        """Initialize with API key from environment."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Check your .env file.")

    def generate_with_model(self, model_info: dict, type_signature: str) -> dict:
        """Generate function with a specific model and collect metrics."""
        start_time = time.time()

        try:
            # Initialize DSPy with this model
            lm = dspy.LM(
                model=model_info["id"],
                api_key=self.api_key,
                api_base="https://openrouter.ai/api/v1"
            )
            dspy.configure(lm=lm)
            generator = dspy.ChainOfThought(FunctionGenerator)

            # Generate the function
            result = generator(type_signature=type_signature)
            implementation = result.implementation

            elapsed_time = time.time() - start_time

            # Try to get usage info from the LM history
            usage_info = {}
            if hasattr(lm, 'history') and lm.history:
                last_call = lm.history[-1]
                if 'response' in last_call and hasattr(last_call['response'], 'usage'):
                    usage = last_call['response'].usage
                    usage_info = {
                        'prompt_tokens': getattr(usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(usage, 'completion_tokens', 0),
                        'total_tokens': getattr(usage, 'total_tokens', 0),
                    }

            return {
                'success': True,
                'implementation': implementation,
                'time': elapsed_time,
                'usage': usage_info,
                'error': None
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'success': False,
                'implementation': None,
                'time': elapsed_time,
                'usage': {},
                'error': str(e)
            }

    def compare_models(self, type_signature: str, output_dir: Path):
        """Compare all models and save results."""
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for model_info in self.MODELS:
                task = progress.add_task(
                    f"Testing {model_info['name']}...",
                    total=None
                )

                result = self.generate_with_model(model_info, type_signature)
                result['model'] = model_info
                results.append(result)

                progress.remove_task(task)

        # Save results
        self._save_results(results, type_signature, output_dir)
        self._display_summary(results)

        return results

    def _save_results(self, results: list, type_signature: str, output_dir: Path):
        """Save generated code and metrics to files."""
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = output_dir / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'type_signature': type_signature,
            'models_tested': len(results),
        }

        # Save individual implementations
        metrics = []
        for result in results:
            model_name = result['model']['name']

            if result['success']:
                # Save implementation
                impl_file = run_dir / f"{model_name}.py"
                impl_file.write_text(result['implementation'])

                # Collect metrics
                metric = {
                    'model': model_name,
                    'model_id': result['model']['id'],
                    'tier': result['model']['tier'],
                    'success': True,
                    'time_seconds': round(result['time'], 3),
                    'usage': result['usage'],
                    'output_file': str(impl_file.relative_to(output_dir))
                }
            else:
                metric = {
                    'model': model_name,
                    'model_id': result['model']['id'],
                    'tier': result['model']['tier'],
                    'success': False,
                    'time_seconds': round(result['time'], 3),
                    'error': result['error']
                }

            metrics.append(metric)

        # Save metrics YAML
        metrics_data = {
            'metadata': metadata,
            'results': metrics
        }

        metrics_file = run_dir / 'metrics.yaml'
        with open(metrics_file, 'w') as f:
            yaml.dump(metrics_data, f, default_flow_style=False, sort_keys=False)

        console.print(f"\n[green]Results saved to:[/green] {run_dir}")
        console.print(f"[green]Metrics file:[/green] {metrics_file}")

    def _display_summary(self, results: list):
        """Display a summary table of results."""
        table = Table(title="Model Comparison Results")

        table.add_column("Model", style="cyan")
        table.add_column("Tier", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Time (s)", justify="right", style="yellow")
        table.add_column("Tokens", justify="right", style="blue")

        for result in results:
            model_name = result['model']['name']
            tier = result['model']['tier']

            if result['success']:
                status = "OK"
                time_str = f"{result['time']:.3f}"
                tokens = result['usage'].get('total_tokens', 'N/A')
                tokens_str = str(tokens) if tokens != 'N/A' else 'N/A'
            else:
                status = "FAIL"
                time_str = f"{result['time']:.3f}"
                tokens_str = "Error"

            table.add_row(model_name, tier, status, time_str, tokens_str)

        console.print("\n")
        console.print(table)


def main():
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] compare_functions.py '<type_signature>'")
        console.print("\n[yellow]Example:[/yellow]")
        console.print("  compare_functions.py 'def fibonacci(n: int) -> int'")
        sys.exit(1)

    type_signature = sys.argv[1]

    # Setup output directory
    output_dir = Path(__file__).parent / "comparisons"
    output_dir.mkdir(exist_ok=True)

    console.print(f"\n[bold cyan]Comparing models for:[/bold cyan] {type_signature}\n")

    # Run comparison
    comparison = ModelComparison()
    comparison.compare_models(type_signature, output_dir)


if __name__ == "__main__":
    main()
