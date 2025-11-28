def print_list_elements(my_list):
    # Corrected range to go up to len(my_list) without going out of range
    for i in range(len(my_list)):
        print(f"Element {i}: {my_list[i]}")

if __name__ == "__main__":
    data = ["Apple", "Banana", "Cherry"]
    print_list_elements(data)