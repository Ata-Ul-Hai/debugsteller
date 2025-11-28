def fibonacci(n):
    # BUG: No base case (if n <= 1: return n)
    # This will run forever until Python crashes
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print("Calculating Fibonacci for 10...")
    result = fibonacci(10)
    print(f"Result: {result}")
