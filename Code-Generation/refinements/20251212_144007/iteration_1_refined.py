```python
def fibonacci(n: int) -> int:
    """
    Calculate the nth number in the Fibonacci sequence.

    Args:
    n (int): The position of the number in the Fibonacci sequence.

    Returns:
    int: The nth number in the Fibonacci sequence.
    """
    if n <= 0:
        return 0  # Return 0 instead of a string
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        fib_prev = 0
        fib_curr = 1
        for i in range(3, n + 1):
            fib_next = fib_prev + fib_curr
            fib_prev = fib_curr
            fib_curr = fib_next
        return fib_curr
```