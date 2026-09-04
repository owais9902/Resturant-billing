"""
order.py
---------
Defines OrderItem (a menu item + quantity within an order) and Order
(a table's full order: items, discount, tax, status, receipt totals).

Demonstrates: OOP, encapsulation, input validation, computed properties.
"""

from datetime import datetime

VALID_STATUSES = ("Open", "Billed", "Cancelled")


class OrderItem:
    """One line item within an order: a menu item plus a quantity."""

    def __init__(self, menu_item, quantity):
        self.menu_item = menu_item
        self.quantity = self._validate_quantity(quantity)

    @staticmethod
    def _validate_quantity(quantity):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if quantity > 100:
            raise ValueError("Quantity cannot exceed 100 per line item.")
        return quantity

    @property
    def subtotal(self):
        return round(self.menu_item.price * self.quantity, 2)

    def to_dict(self):
        return {
            "item_id": self.menu_item.item_id,
            "name": self.menu_item.name,
            "unit_price": self.menu_item.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal,
        }

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity} = ${self.subtotal:.2f}"


class Order:
    """
    Represents a full order for one table.

    Attributes:
        order_id (int): unique identifier
        table_number (str): e.g. "T04"
        items (list[OrderItem]): line items in the order
        discount_percent (float): 0-100
        tax_percent (float): 0-100
        status (str): Open / Billed / Cancelled
        created_at (str): timestamp
    """

    def __init__(self, order_id, table_number, items=None, discount_percent=0,
                 tax_percent=5.0, status="Open", created_at=None):
        self.order_id = order_id
        self.table_number = self._validate_table(table_number)
        self.items = items if items is not None else []
        self.discount_percent = self._validate_percent(discount_percent, "Discount")
        self.tax_percent = self._validate_percent(tax_percent, "Tax")
        self.status = self._validate_status(status)
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _validate_table(table_number):
        if not isinstance(table_number, str) or not table_number.strip():
            raise ValueError("Table number cannot be empty.")
        return table_number.strip().upper()

    @staticmethod
    def _validate_percent(value, label):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{label} percent must be a number.")
        if not (0 <= value <= 100):
            raise ValueError(f"{label} percent must be between 0 and 100.")
        return value

    @staticmethod
    def _validate_status(status):
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {', '.join(VALID_STATUSES)}.")
        return status

    # ------------------------------------------------------------------
    # Order manipulation
    # ------------------------------------------------------------------
    def add_item(self, menu_item, quantity):
        """Add an item to the order, or increase quantity if already present."""
        for line in self.items:
            if line.menu_item.item_id == menu_item.item_id:
                line.quantity = OrderItem._validate_quantity(line.quantity + int(quantity))
                return line
        line = OrderItem(menu_item, quantity)
        self.items.append(line)
        return line

    def remove_item(self, item_id):
        """Remove a line item by menu item id. Returns True if removed."""
        for line in self.items:
            if line.menu_item.item_id == item_id:
                self.items.remove(line)
                return True
        return False

    # ------------------------------------------------------------------
    # Bill calculation
    # ------------------------------------------------------------------
    @property
    def subtotal(self):
        return round(sum(line.subtotal for line in self.items), 2)

    @property
    def discount_amount(self):
        return round(self.subtotal * (self.discount_percent / 100), 2)

    @property
    def taxable_amount(self):
        return round(self.subtotal - self.discount_amount, 2)

    @property
    def tax_amount(self):
        return round(self.taxable_amount * (self.tax_percent / 100), 2)

    @property
    def total(self):
        return round(self.taxable_amount + self.tax_amount, 2)

    def mark_billed(self):
        if not self.items:
            raise ValueError("Cannot bill an order with no items.")
        self.status = "Billed"

    def mark_cancelled(self):
        self.status = "Cancelled"

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "table_number": self.table_number,
            "items": [line.to_dict() for line in self.items],
            "discount_percent": self.discount_percent,
            "tax_percent": self.tax_percent,
            "status": self.status,
            "created_at": self.created_at,
            "subtotal": self.subtotal,
            "discount_amount": self.discount_amount,
            "tax_amount": self.tax_amount,
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, data, menu_lookup):
        """Rebuild an Order from a saved dict, resolving items via menu_lookup (dict of item_id -> MenuItem)."""
        order = cls(
            order_id=data["order_id"],
            table_number=data["table_number"],
            discount_percent=data.get("discount_percent", 0),
            tax_percent=data.get("tax_percent", 5.0),
            status=data.get("status", "Open"),
            created_at=data.get("created_at"),
        )
        for line_data in data.get("items", []):
            menu_item = menu_lookup.get(line_data["item_id"])
            if menu_item is not None:
                order.items.append(OrderItem(menu_item, line_data["quantity"]))
        return order

    def __str__(self):
        return (f"Order #{self.order_id} | Table {self.table_number} | "
                f"{len(self.items)} item(s) | {self.status} | Total ${self.total:.2f}")
