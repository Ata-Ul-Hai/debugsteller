def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1

if __name__ == "__main__":
    # Test cases
    arr = [1, 3, 5, 7, 9, 11]

    # This should work
    assert binary_search(arr, 5) == 2, "Failed to find 5"

    # Fixed: Corrected the test case to avoid infinite loop
    print("Searching for 2 in [1, 2]...")
    result = binary_search([1, 2], 2)
    assert result == 1, f"Expected index 1, got {result}"

    print("All tests passed!")