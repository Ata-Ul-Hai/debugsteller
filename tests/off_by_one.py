my_list = [1, 2, 3, 4, 5]

# Intent: Print all elements
# Bug: range goes to len(my_list) + 1, causing IndexError
for i in range(len(my_list) + 1):
    print(my_list[i])
