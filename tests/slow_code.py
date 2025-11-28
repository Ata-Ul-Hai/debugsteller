def find_duplicates(items):
    # O(n^2) implementation
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

if __name__ == "__main__":
    data = [1, 2, 3, 2, 4, 5, 5, 6]
    print(f"Duplicates: {find_duplicates(data)}")
