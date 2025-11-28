import time

def create_big_string(n):
    # INEFFICIENT: Creating a string with += in a loop creates a new object every iteration.
    result = ""
    for i in range(n):
        result += str(i) + ","
    return result

if __name__ == "__main__":
    start_time = time.time()
    
    # Create a string with 50,000 numbers
    n = 50000
    data = create_big_string(n)
    
    end_time = time.time()
    print(f"String created. Length: {len(data)}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Verification: Check first few characters and length
    # Expected: "0,1,2,3,..."
    assert data.startswith("0,1,2,3,"), f"Output format incorrect: {data[:20]}..."
    # Length check is tricky if n is large, but let's check a small sample or just format.
    # Actually, let's run a small n for correctness check first.
    
    small_data = create_big_string(5)
    assert small_data == "0,1,2,3,4,", f"Logic error! Expected '0,1,2,3,4,', got '{small_data}'"
    print("Assertions passed.")