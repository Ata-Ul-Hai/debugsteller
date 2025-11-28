import sys
sys.setrecursionlimit(5000)

def fibonacci(n):
    if n <= 1:
        return n
    fib_values = [0] * (n + 1)
    fib_values[0], fib_values[1] = 0, 1
    for i in range(2, n + 1):
        fib_values[i] = fib_values[i - 1] + fib_values[i - 2]
    return fib_values[n]

if __name__ == "__main__":
    print("Calculating Fibonacci for 10...")
    result = fibonacci(10)
    print(f"Result: {result}")