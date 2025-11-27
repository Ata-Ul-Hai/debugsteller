def recursive_function(n):
    print(f"Recursion depth: {n}")
    return recursive_function(n + 1)

if __name__ == "__main__":
    recursive_function(1)
