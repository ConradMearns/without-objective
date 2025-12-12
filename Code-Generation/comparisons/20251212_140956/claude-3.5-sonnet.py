def fibonacci(n: int) -> int:
    """
    Calculate the nth number in the Fibonacci sequence.
    
    The Fibonacci sequence starts with 0, 1, and each subsequent number
    is the sum of the previous two numbers.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-based index)
    
    Returns:
        int: The nth Fibonacci number. Returns 0 for n <= 0
    
    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(6)
        8
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
        
    prev, current = 0, 1
    for _ in range(2, n + 1):
        prev, current = current, prev + current
    
    return current