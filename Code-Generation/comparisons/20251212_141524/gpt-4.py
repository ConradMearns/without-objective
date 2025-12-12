def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    The Fibonacci sequence is defined as:
        F(0) = 0, F(1) = 1
        F(n) = F(n-1) + F(n-2) for n > 1

    Args:
        n (int): The index (n >= 0) of the Fibonacci sequence to calculate.

    Returns:
        int: The nth Fibonacci number.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1

    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current