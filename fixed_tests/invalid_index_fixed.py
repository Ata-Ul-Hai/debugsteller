data = {"a": 1, "b": 2}

# Bug: Accessing non-existent index in a list (simulated)
items = [10, 20]
if len(items) > 5:
    print(items[5])
else:
    print("Index out of range")