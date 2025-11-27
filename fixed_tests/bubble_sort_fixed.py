def bubble_sort(arr):
    n = len(arr)
    # Corrected range to ensure all elements are compared
    for i in range(n):
        # Corrected inner loop range to include the last element and prevent out-of-range errors
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

if __name__ == "__main__":
    data = [2, 1]
    sorted_data = bubble_sort(data.copy())
    expected = sorted(data)
    
    print(f"Result: {sorted_data}")
    print(f"Expect: {expected}")
    
    assert sorted_data == expected, "Bubble sort failed to sort correctly"
    print("All tests passed!")