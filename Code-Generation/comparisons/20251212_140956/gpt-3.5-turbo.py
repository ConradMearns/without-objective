```python
def fibonacci(n: int) -> int:
    """
    Calculate the n-th Fibonacci number in the sequence.

    Parameters:
    n (int): The position of the Fibonacci number to find.

    Returns:
    int: The n-th Fibonacci number.

    Examples:
    >>> fibonacci(0)
    0
    >>> fibonacci(1)
    1
    >>> fibonacci(5)
    5
    >>> fibonacci(10)
    55
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
```