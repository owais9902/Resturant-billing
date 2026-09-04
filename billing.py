"""
billing.py
-----------
Defines BillingSystem: the core manager for the Restaurant Billing System.

Owns the menu (list of MenuItem) and all orders (list of Order), and
provides operations: menu CRUD, order lifecycle, receipt generation,
search/filter/sort, and JSON/CSV persistence.
"""

import json
import csv
import os

from menu_item import MenuItem
from order import Order


class BillingSystem:
    def __init__(self, menu_file="data/menu.json", orders_file="data/orders.json"):
        self.menu_file = menu_file
        self.orders_file = orders_file
        self.menu = []      # list[MenuItem]
        self.orders = []    # list[Order]
        self._next_item_id = 1
        self._next_order_id = 1
        self.load_menu()
        self.load_orders()

    # ------------------------------------------------------------------
    # Menu management
    # ------------------------------------------------------------------
    def add_menu_item(self, name, price, category="Other"):
        item = MenuItem(self._next_item_id, name, price, category)
        self.menu.append(item)
        self._next_item_id += 1
        self.save_menu()
        return item

    def get_menu_item(self, item_id):
        for m in self.menu:
            if m.item_id == item_id:
                return m
        return None

    def update_menu_item(self, item_id, **fields):
        item = self.get_menu_item(item_id)
        if item is None:
            raise ValueError(f"No menu item found with ID {item_id}.")
        current = item.to_dict()
        current.update(fields)
        updated = MenuItem.from_dict({**current, "item_id": item_id})
        self.menu[self.menu.index(item)] = updated
        self.save_menu()
        return updated

    def delete_menu_item(self, item_id):
        item = self.get_menu_item(item_id)
        if item is None:
            return False
        self.menu.remove(item)
        self.save_menu()
        return True

    def search_menu(self, keyword):
        keyword = keyword.strip().lower()
        return [m for m in self.menu if keyword in m.name.lower()]

    def filter_menu_by_category(self, category):
        category = category.strip().capitalize()
        return [m for m in self.menu if m.category == category]

    def sort_menu(self, key="name", reverse=False):
        if key not in ("name", "price", "category"):
            raise ValueError("Sort key must be one of: name, price, category.")
        return sorted(self.menu, key=lambda m: getattr(m, key), reverse=reverse)

    # ------------------------------------------------------------------
    # Order lifecycle
    # ------------------------------------------------------------------
    def create_order(self, table_number, tax_percent=5.0):
        order = Order(self._next_order_id, table_number, tax_percent=tax_percent)
        self.orders.append(order)
        self._next_order_id += 1
        self.save_orders()
        return order

    def get_order(self, order_id):
        for o in self.orders:
            if o.order_id == order_id:
                return o
        return None

    def get_open_order_for_table(self, table_number):
        table_number = table_number.strip().upper()
        for o in self.orders:
            if o.table_number == table_number and o.status == "Open":
                return o
        return None

    def add_item_to_order(self, order_id, item_id, quantity):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")
        if order.status != "Open":
            raise ValueError(f"Order #{order_id} is {order.status.lower()} and cannot be modified.")
        menu_item = self.get_menu_item(item_id)
        if menu_item is None:
            raise ValueError(f"No menu item found with ID {item_id}.")
        line = order.add_item(menu_item, quantity)
        self.save_orders()
        return line

    def remove_item_from_order(self, order_id, item_id):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")
        if order.status != "Open":
            raise ValueError(f"Order #{order_id} is {order.status.lower()} and cannot be modified.")
        removed = order.remove_item(item_id)
        if removed:
            self.save_orders()
        return removed

    def apply_discount(self, order_id, discount_percent):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")
        order.discount_percent = Order._validate_percent(discount_percent, "Discount")
        self.save_orders()
        return order

    def generate_bill(self, order_id):
        """Finalize an order: mark it Billed and return it (ready for receipt printing)."""
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")
        order.mark_billed()
        self.save_orders()
        return order

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")
        order.mark_cancelled()
        self.save_orders()
        return order

    # ------------------------------------------------------------------
    # Search / filter / sort orders
    # ------------------------------------------------------------------
    def filter_orders_by_status(self, status):
        return [o for o in self.orders if o.status == status]

    def filter_orders_by_table(self, table_number):
        table_number = table_number.strip().upper()
        return [o for o in self.orders if o.table_number == table_number]

    def sort_orders(self, key="order_id", reverse=False):
        if key == "total":
            return sorted(self.orders, key=lambda o: o.total, reverse=reverse)
        if key in ("order_id", "table_number", "status", "created_at"):
            return sorted(self.orders, key=lambda o: getattr(o, key), reverse=reverse)
        raise ValueError("Sort key must be one of: order_id, table_number, status, created_at, total.")

    # ------------------------------------------------------------------
    # Receipt formatting
    # ------------------------------------------------------------------
    def format_receipt(self, order_id):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError(f"No order found with ID {order_id}.")

        lines = []
        lines.append("=" * 40)
        lines.append("        LAZEEZ-E-HYDERABADI")
        lines.append("           RESTAURANT RECEIPT")
        lines.append("=" * 40)
        lines.append(f"Order #: {order.order_id}    Table: {order.table_number}")
        lines.append(f"Date: {order.created_at}")
        lines.append(f"Status: {order.status}")
        lines.append("-" * 40)
        for line in order.items:
            lines.append(f"{line.menu_item.name[:20]:<20} x{line.quantity:<3} ${line.subtotal:>8.2f}")
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<28}${order.subtotal:>8.2f}")
        if order.discount_percent > 0:
            lines.append(f"{'Discount (' + str(order.discount_percent) + '%):':<28}-${order.discount_amount:>7.2f}")
        lines.append(f"{'Tax (' + str(order.tax_percent) + '%):':<28}${order.tax_amount:>8.2f}")
        lines.append("=" * 40)
        lines.append(f"{'TOTAL:':<28}${order.total:>8.2f}")
        lines.append("=" * 40)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def sales_summary(self):
        billed = self.filter_orders_by_status("Billed")
        total_revenue = round(sum(o.total for o in billed), 2)
        total_orders = len(billed)
        avg_order = round(total_revenue / total_orders, 2) if total_orders else 0.0
        return {
            "billed_orders": total_orders,
            "open_orders": len(self.filter_orders_by_status("Open")),
            "cancelled_orders": len(self.filter_orders_by_status("Cancelled")),
            "total_revenue": total_revenue,
            "average_order_value": avg_order,
        }

    # ------------------------------------------------------------------
    # Persistence: menu
    # ------------------------------------------------------------------
    def save_menu(self):
        try:
            os.makedirs(os.path.dirname(self.menu_file), exist_ok=True)
            payload = {"next_id": self._next_item_id, "menu": [m.to_dict() for m in self.menu]}
            with open(self.menu_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError as e:
            raise IOError(f"Could not save menu to {self.menu_file}: {e}")

    def load_menu(self):
        if not os.path.exists(self.menu_file):
            self.menu = []
            self._next_item_id = 1
            return
        try:
            with open(self.menu_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.menu = [MenuItem.from_dict(d) for d in payload.get("menu", [])]
            self._next_item_id = payload.get("next_id", (max((m.item_id for m in self.menu), default=0) + 1))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read {self.menu_file} ({e}). Starting with an empty menu.")
            self.menu = []
            self._next_item_id = 1

    # ------------------------------------------------------------------
    # Persistence: orders
    # ------------------------------------------------------------------
    def save_orders(self):
        try:
            os.makedirs(os.path.dirname(self.orders_file), exist_ok=True)
            payload = {"next_id": self._next_order_id, "orders": [o.to_dict() for o in self.orders]}
            with open(self.orders_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError as e:
            raise IOError(f"Could not save orders to {self.orders_file}: {e}")

    def load_orders(self):
        if not os.path.exists(self.orders_file):
            self.orders = []
            self._next_order_id = 1
            return
        try:
            with open(self.orders_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            menu_lookup = {m.item_id: m for m in self.menu}
            self.orders = [Order.from_dict(d, menu_lookup) for d in payload.get("orders", [])]
            self._next_order_id = payload.get("next_id", (max((o.order_id for o in self.orders), default=0) + 1))
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"Warning: could not read {self.orders_file} ({e}). Starting with no orders.")
            self.orders = []
            self._next_order_id = 1

    # ------------------------------------------------------------------
    # Export: CSV
    # ------------------------------------------------------------------
    def export_orders_to_csv(self, csv_file="data/orders_export.csv"):
        try:
            os.makedirs(os.path.dirname(csv_file), exist_ok=True)
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["order_id", "table_number", "status", "subtotal",
                              "discount_amount", "tax_amount", "total", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for o in self.orders:
                    d = o.to_dict()
                    writer.writerow({k: d[k] for k in fieldnames})
            return csv_file
        except OSError as e:
            raise IOError(f"Could not export CSV to {csv_file}: {e}")
