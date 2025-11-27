import sys
sys.setrecursionlimit(5000)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print("Calculating Fibonacci for 10...")
    result = fibonacci(10)
    print(f"Result: {result}")