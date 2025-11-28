def fib(n, memo={}):
    """
    Calculates the nth Fibonacci number using memoization.

    Args:
        n (int): The position in the Fibonacci sequence.
        memo (dict, optional): A dictionary to store previously computed values. Defaults to an empty dictionary.

    Returns:
        int: The nth Fibonacci number.
    """
    if n <= 1:
        return n

    if n not in memo:
        memo[n] = fib(n-1, memo) + fib(n-2, memo)

    return memo[n]

print(fib(10))