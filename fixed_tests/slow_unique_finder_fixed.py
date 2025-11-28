import time

def find_first_unique(s):
    # INFFICIENT: This approach can be up to O(n^2) depending on Python's implementation
    # of count, as it iterates through the entire string for every character.
    
    unique_char = None
    for char in s:
        if s.count(char) == 1:
            unique_char = char
            break
    
    return unique_char

if __name__ == "__main__":
    # Test string with high repetition (ensures the slow count() function runs many times)
    test_string = "aabbccddeeffgghhijjkkllmmnnooppqqrrssttuuvvwwxxyyzz" + "A"
    
    start_time = time.time()
    result = find_first_unique(test_string)
    end_time = time.time()
    
    print(f"First unique character found: {result}")
    print(f"Time taken: {end_time - start_time:.6f} seconds")

# Expected Output: 'A'
# Expected Inefficiency: ~0.0003 seconds (but scales poorly with longer strings)