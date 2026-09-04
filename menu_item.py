"""
menu_item.py
-------------
Defines MenuItem: a single dish/drink available on the restaurant's menu.

Demonstrates: OOP (class + encapsulation), input validation.
"""

VALID_CATEGORIES = ("Starter", "Main", "Dessert", "Beverage", "Other")


class MenuItem:
    """Represents one sellable item on the restaurant menu."""

    def __init__(self, item_id, name, price, category="Other"):
        self.item_id = item_id
        self.name = self._validate_name(name)
        self.price = self._validate_price(price)
        self.category = self._validate_category(category)

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Item name cannot be empty.")
        return name.strip()

    @staticmethod
    def _validate_price(price):
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError("Price must be a number.")
        if price <= 0:
            raise ValueError("Price must be greater than 0.")
        if price > 100000:
            raise ValueError("Price seems unrealistic (must be <= 100000).")
        return round(price, 2)

    @staticmethod
    def _validate_category(category):
        if not isinstance(category, str):
            raise ValueError("Category must be text.")
        category = category.strip().capitalize()
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of {', '.join(VALID_CATEGORIES)}.")
        return category

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["item_id"], data["name"], data["price"], data.get("category", "Other"))

    def __str__(self):
        return f"[{self.item_id}] {self.name} ({self.category}) - ${self.price:.2f}"

    def __repr__(self):
        return f"MenuItem({self.to_dict()!r})"
