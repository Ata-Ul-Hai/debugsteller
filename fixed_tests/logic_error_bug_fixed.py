def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1  # Fix: Increment the count to avoid division by zero
    
    return total / count  # Corrected: Divide by the actual count instead of a hardcoded number

if __name__ == "__main__":
    scores = [10, 20, 30, 40, 50]
    result = calculate_average(scores)
    
    expected = 30.0
    if result != expected:
        raise ValueError(f"Logic Error! Expected {expected}, but got {result}")
    
    print("Success!")