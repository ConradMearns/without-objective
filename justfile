# Test code generation with fibonacci example
test-codegen:
    ./Code-Generation/generate_function.py "def fibonacci(n: int) -> int"

# Compare multiple models on a function signature
compare-models sig="def fibonacci(n: int) -> int":
    ./Code-Generation/compare_functions.py "{{sig}}"

# Refine a function iteratively with a single model using type checking
refine-function model="meta-llama/llama-3.1-8b-instruct" sig="def fibonacci(n: int) -> int" iterations="3":
    ./Code-Generation/refine_function.py "{{model}}" "{{sig}}" {{iterations}}
