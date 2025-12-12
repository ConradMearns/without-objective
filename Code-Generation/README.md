# Code Generation with DSPy

Scripts that use DSPy to generate Python function implementations from type signatures.

## Scripts

- **`generate_function.py`** - Generate a function with a single model
- **`compare_functions.py`** - Compare multiple models (large, medium, small) and collect metrics
- **`refine_function.py`** - Generate with a single model, then iteratively refine using `uvx ty` type checker

## Usage

```bash
./generate_function.py 'def function_name(param: type) -> return_type'
```

## Examples

### Single Model Generation

```bash
# Generate a fibonacci function
./generate_function.py 'def fibonacci(n: int) -> int'

# Generate a list sorting function
./generate_function.py 'def sort_by_length(words: list[str]) -> list[str]'

# Generate a data processing function
./generate_function.py 'def filter_even_numbers(numbers: list[int]) -> list[int]'
```

### Model Comparison

```bash
# Compare 7 different models (large/medium/small) on the same signature
./compare_functions.py 'def fibonacci(n: int) -> int'

# Results saved to comparisons/<timestamp>/
# - Each model's output saved as <model_name>.py
# - Metrics saved to metrics.yaml (timing, tokens, costs)
```

**Models tested:**
- Large: Claude 3.5 Sonnet, GPT-4
- Medium: Claude 3 Haiku, GPT-3.5 Turbo
- Small: Llama 3.1 8B, Mistral 7B, Qwen 7B

### Iterative Refinement

```bash
# Generate and refine with a small model (default 3 iterations)
./refine_function.py 'meta-llama/llama-3.1-8b-instruct' 'def fibonacci(n: int) -> int'

# Specify max iterations
./refine_function.py 'mistralai/mistral-7b-instruct' 'def sort(items: list[int]) -> list[int]' 5

# Results saved to refinements/<timestamp>/
# - iteration_0_initial.py - Initial generation
# - iteration_N_refined.py - Each refinement iteration
# - metrics.yaml - Timing and type check results for each iteration
```

**How it works:**
1. Generate initial implementation with specified model
2. Run `uvx ty` type checker on the result
3. If type errors exist, use DSPy to refine based on feedback
4. Repeat up to max_iterations or until type checking passes
5. Save all iterations and metrics

## Setup

The script uses DSPy with OpenRouter (defaults to Claude 3.5 Sonnet).

1. Add your OpenRouter API key to `.env`:
   ```bash
   OPENROUTER_API_KEY=your-api-key-here
   ```

2. (Optional) Change the model by modifying the `model` parameter in `CodeGenerator.__init__()`.
   Examples: `openrouter/anthropic/claude-3.5-sonnet`, `openrouter/openai/gpt-4`, etc.

## How it Works

- Loads API key from `.env` file using python-dotenv
- Uses DSPy's `ChainOfThought` module to reason about the type signature
- Generates complete function implementations with docstrings via OpenRouter
- Displays the result with syntax highlighting using Rich


---

# Further Reading

https://arxiv.org/abs/2511.09030

uv run Code-Generation/maker.py --model openrouter/qwen/qwen3-8b

Qwen2.5-0.5B
Gemma 270M
Qwen3-0.6B
phi-3.5-mini
tinyllama
openelm
smollm
mobilellama