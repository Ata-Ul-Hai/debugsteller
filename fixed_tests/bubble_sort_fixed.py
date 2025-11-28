def bubble_sort(arr):
    n = len(arr)
    # ## EDUCATIONAL: The original code had an off-by-one error in the inner loop range, which has been corrected to ensure the entire array is sorted properly.
    for i in range(n):
        for j in range(0, n - i - 1):  # Corrected from range(0, n - i - 2)
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