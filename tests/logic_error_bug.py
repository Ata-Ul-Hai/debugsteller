def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total += num
        # BUG: count is not incremented, so we divide by zero logic or wrong count
        # Actually, let's make it a logic bug: dividing by hardcoded number instead of length
    
    # Logic Bug: Always dividing by 2 instead of the actual list length
    return total / 2

if __name__ == "__main__":
    scores = [10, 20, 30, 40, 50]
    result = calculate_average(scores)
    
    expected = 30.0
    if result != expected:
        # We manually raise an error so Antigravity has something to catch
        raise ValueError(f"Logic Error! Expected {expected}, but got {result}")
    
    print("Success!")
