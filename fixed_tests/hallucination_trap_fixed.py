def get_user_data(user_id):
    database = {
        1: "Alice",
        2: "Bob"
    }
    return database.get(user_id, "User not found")

if __name__ == "__main__":
    user = get_user_data(3)
    print(f"User found: {user}")