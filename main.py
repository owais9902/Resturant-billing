"""
main.py
--------
Command-line interface for the Restaurant Billing System.
Run with: python3 main.py
"""

from billing import BillingSystem

MENU = """
============ LAZEEZ-E-HYDERABADI — BILLING SYSTEM ============
 1. Add menu item
 2. View menu
 3. Search / filter / sort menu
 4. Create new order (table)
 5. Add item to order
 6. Remove item from order
 7. Apply discount to order
 8. View order (running total)
 9. Generate bill / receipt
10. Cancel order
11. View all orders (filter/sort)
12. Sales summary
13. Export orders to CSV
 0. Exit
=============================================================
"""


def prompt_int(label):
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("  Please enter a whole number.")


def print_menu_items(items):
    if not items:
        print("  (no items to show)")
        return
    for m in items:
        print(f"  {m}")


def add_menu_item_flow(bs):
    print("\n-- Add Menu Item --")
    name = input("Item name: ").strip()
    price = input("Price: ").strip()
    category = input("Category (Starter/Main/Dessert/Beverage/Other): ").strip()
    try:
        item = bs.add_menu_item(name, price, category)
        print(f"  Added: {item}")
    except ValueError as e:
        print(f"  Error: {e}")


def view_menu_flow(bs):
    print("\n-- Menu --")
    print_menu_items(bs.menu)


def search_filter_sort_menu_flow(bs):
    print("\n-- Search / Filter / Sort Menu --")
    print("  1. Search by name")
    print("  2. Filter by category")
    print("  3. Sort by price")
    choice = input("  Choose an option: ").strip()
    if choice == "1":
        keyword = input("  Keyword: ").strip()
        print_menu_items(bs.search_menu(keyword))
    elif choice == "2":
        category = input("  Category: ").strip()
        try:
            print_menu_items(bs.filter_menu_by_category(category))
        except ValueError as e:
            print(f"  Error: {e}")
    elif choice == "3":
        order = input("  Order (asc/desc) [asc]: ").strip().lower() or "asc"
        print_menu_items(bs.sort_menu(key="price", reverse=(order == "desc")))
    else:
        print("  Invalid option.")


def create_order_flow(bs):
    print("\n-- Create New Order --")
    table = input("Table number (e.g. T04): ").strip()
    tax = input("Tax percent [5.0]: ").strip() or "5.0"
    try:
        order = bs.create_order(table, tax_percent=tax)
        print(f"  Created: {order}")
    except ValueError as e:
        print(f"  Error: {e}")


def add_item_to_order_flow(bs):
    print("\n-- Add Item to Order --")
    order_id = prompt_int("Order ID: ")
    view_menu_flow(bs)
    item_id = prompt_int("Item ID to add: ")
    quantity = input("Quantity: ").strip()
    try:
        line = bs.add_item_to_order(order_id, item_id, quantity)
        print(f"  Added: {line}")
    except ValueError as e:
        print(f"  Error: {e}")


def remove_item_from_order_flow(bs):
    print("\n-- Remove Item from Order --")
    order_id = prompt_int("Order ID: ")
    item_id = prompt_int("Item ID to remove: ")
    try:
        removed = bs.remove_item_from_order(order_id, item_id)
        print("  Removed." if removed else "  Item not found in that order.")
    except ValueError as e:
        print(f"  Error: {e}")


def apply_discount_flow(bs):
    print("\n-- Apply Discount --")
    order_id = prompt_int("Order ID: ")
    discount = input("Discount percent (0-100): ").strip()
    try:
        bs.apply_discount(order_id, discount)
        print("  Discount applied.")
    except ValueError as e:
        print(f"  Error: {e}")


def view_order_flow(bs):
    print("\n-- View Order --")
    order_id = prompt_int("Order ID: ")
    order = bs.get_order(order_id)
    if order is None:
        print(f"  No order found with ID {order_id}.")
        return
    print(f"  {order}")
    for line in order.items:
        print(f"    {line}")
    print(f"  Subtotal: ${order.subtotal:.2f}  Discount: ${order.discount_amount:.2f}  "
          f"Tax: ${order.tax_amount:.2f}  Total: ${order.total:.2f}")


def generate_bill_flow(bs):
    print("\n-- Generate Bill --")
    order_id = prompt_int("Order ID: ")
    try:
        bs.generate_bill(order_id)
        print(bs.format_receipt(order_id))
    except ValueError as e:
        print(f"  Error: {e}")


def cancel_order_flow(bs):
    print("\n-- Cancel Order --")
    order_id = prompt_int("Order ID: ")
    try:
        order = bs.cancel_order(order_id)
        print(f"  Cancelled: {order}")
    except ValueError as e:
        print(f"  Error: {e}")


def view_all_orders_flow(bs):
    print("\n-- All Orders --")
    print("  1. All\n  2. By status\n  3. By table\n  4. Sort by total")
    choice = input("  Choose an option: ").strip()
    if choice == "2":
        status = input("  Status (Open/Billed/Cancelled): ").strip().capitalize()
        orders = bs.filter_orders_by_status(status)
    elif choice == "3":
        table = input("  Table number: ").strip()
        orders = bs.filter_orders_by_table(table)
    elif choice == "4":
        order = input("  Order (asc/desc) [desc]: ").strip().lower() or "desc"
        orders = bs.sort_orders(key="total", reverse=(order == "desc"))
    else:
        orders = bs.orders

    if not orders:
        print("  (no orders to show)")
    for o in orders:
        print(f"  {o}")


def sales_summary_flow(bs):
    print("\n-- Sales Summary --")
    s = bs.sales_summary()
    print(f"  Billed orders:      {s['billed_orders']}")
    print(f"  Open orders:        {s['open_orders']}")
    print(f"  Cancelled orders:   {s['cancelled_orders']}")
    print(f"  Total revenue:      ${s['total_revenue']:.2f}")
    print(f"  Average order value:${s['average_order_value']:.2f}")


def export_csv_flow(bs):
    print("\n-- Export Orders to CSV --")
    path = input("Output path [data/orders_export.csv]: ").strip() or "data/orders_export.csv"
    try:
        saved = bs.export_orders_to_csv(path)
        print(f"  Exported {len(bs.orders)} order(s) to {saved}")
    except IOError as e:
        print(f"  Error: {e}")


def main():
    bs = BillingSystem(menu_file="data/menu.json", orders_file="data/orders.json")

    actions = {
        "1": add_menu_item_flow, "2": view_menu_flow, "3": search_filter_sort_menu_flow,
        "4": create_order_flow, "5": add_item_to_order_flow, "6": remove_item_from_order_flow,
        "7": apply_discount_flow, "8": view_order_flow, "9": generate_bill_flow,
        "10": cancel_order_flow, "11": view_all_orders_flow, "12": sales_summary_flow,
        "13": export_csv_flow,
    }

    print("Welcome to Lazeez-e-Hyderabadi — Restaurant Billing System!")

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option. Please choose a number from the menu.")
            continue
        try:
            action(bs)
        except Exception as e:
            print(f"  Unexpected error: {e}")


if __name__ == "__main__":
    main()
