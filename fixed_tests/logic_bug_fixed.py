def calculate_average(numbers):
    total = 0
    count = len(numbers)  # Corrected: increment count based on the length of numbers
    for num in numbers:
        total += num
    
    # Corrected: divide by the actual list length instead of a hardcoded number
    return total / count

if __name__ == "__main__":
    scores = [10, 20, 30, 40, 50]
    result = calculate_average(scores)
    
    expected = 30.0
    if result != expected:
        # We manually raise an error so Antigravity has something to catch
        raise ValueError(f"Logic Error! Expected {expected}, but got {result}")
    
    print("Success!")