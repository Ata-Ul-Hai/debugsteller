import sys
sys.setrecursionlimit(5000)
def recursive_function(n):
    print(f"Recursion depth: {n}")
    if n >= 1000:
        return
    recursive_function(n + 1)

if __name__ == "__main__":
    recursive_function(1)