def print_list_elements(my_list):
    # BUG: range(len(my_list) + 1) goes one index past the end
    for i in range(len(my_list) + 1):
        print(f"Element {i}: {my_list[i]}")

if __name__ == "__main__":
    data = ["Apple", "Banana", "Cherry"]
    print_list_elements(data)
