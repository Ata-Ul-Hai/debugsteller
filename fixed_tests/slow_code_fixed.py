def find_duplicates(items):
    # Create a set to store unique items
    seen = set()
    # Create a set to store duplicates
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

if __name__ == "__main__":
    data = [1, 2, 3, 2, 4, 5, 5, 6]
    print(f"Duplicates: {find_duplicates(data)}")