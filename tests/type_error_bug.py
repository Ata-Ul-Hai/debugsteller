def calculate_total(price, tax):
    # BUG: 'price' is a string, 'tax' is a float. You cannot add them.
    return price + tax

if __name__ == "__main__":
    item_price = "100"  # Input comes as string
    sales_tax = 5.0
    total = calculate_total(item_price, sales_tax)
    print(f"Total: {total}")
