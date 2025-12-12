# Test code generation with fibonacci example
test-codegen:
    ./Code-Generation/generate_function.py "def fibonacci(n: int) -> int"

# Compare multiple models on a function signature
compare-models sig="def fibonacci(n: int) -> int":
    ./Code-Generation/compare_functions.py "{{sig}}"
