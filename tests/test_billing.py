"""
test_billing.py
-----------------
Unit tests for the Restaurant Billing System (MenuItem, Order, BillingSystem).

Run with:
    python -m unittest discover -s tests -v
(from the project root, i.e. restaurant_billing/)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from menu_item import MenuItem
from order import Order, OrderItem
from billing import BillingSystem

TEST_MENU_FILE = os.path.join(os.path.dirname(__file__), "test_menu.json")
TEST_ORDERS_FILE = os.path.join(os.path.dirname(__file__), "test_orders.json")


class TestMenuItemValidation(unittest.TestCase):
    """Normal, invalid, and boundary input for MenuItem."""

    def test_valid_menu_item(self):
        m = MenuItem(1, "Pizza", 12.5, "Main")
        self.assertEqual(m.name, "Pizza")
        self.assertEqual(m.price, 12.5)
        self.assertEqual(m.category, "Main")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            MenuItem(1, "   ", 10, "Main")

    def test_zero_and_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            MenuItem(1, "Water", 0, "Beverage")
        with self.assertRaises(ValueError):
            MenuItem(1, "Water", -5, "Beverage")

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValueError):
            MenuItem(1, "Pizza", 10, "Snack")

    def test_price_rounds_to_two_decimals(self):
        m = MenuItem(1, "Coffee", 3.4567, "Beverage")
        self.assertEqual(m.price, 3.46)


class TestOrderItemAndCalculations(unittest.TestCase):
    """Order line items and bill math (subtotal, discount, tax, total)."""

    def setUp(self):
        self.pizza = MenuItem(1, "Pizza", 12.50, "Main")
        self.coke = MenuItem(2, "Coke", 2.50, "Beverage")

    def test_order_item_quantity_validation(self):
        with self.assertRaises(ValueError):
            OrderItem(self.pizza, 0)
        with self.assertRaises(ValueError):
            OrderItem(self.pizza, -2)

    def test_order_item_subtotal(self):
        line = OrderItem(self.pizza, 2)
        self.assertEqual(line.subtotal, 25.00)

    def test_add_item_combines_duplicate_menu_item(self):
        """Adding the same menu item twice should increase quantity, not create two lines."""
        order = Order(1, "T04")
        order.add_item(self.pizza, 2)
        order.add_item(self.pizza, 1)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 3)

    def test_bill_calculation_matches_expected_values(self):
        """Normal scenario: T04, 2 Pizzas, 3 Cokes, 10% discount, 8% tax."""
        order = Order(1, "T04", discount_percent=10, tax_percent=8)
        order.add_item(self.pizza, 2)
        order.add_item(self.coke, 3)
        self.assertEqual(order.subtotal, 32.50)
        self.assertEqual(order.discount_amount, 3.25)
        self.assertEqual(order.taxable_amount, 29.25)
        self.assertEqual(order.tax_amount, 2.34)
        self.assertEqual(order.total, 31.59)

    def test_zero_discount_and_tax_boundary(self):
        order = Order(1, "T04", discount_percent=0, tax_percent=0)
        order.add_item(self.pizza, 1)
        self.assertEqual(order.discount_amount, 0)
        self.assertEqual(order.tax_amount, 0)
        self.assertEqual(order.total, order.subtotal)

    def test_invalid_discount_percent_rejected(self):
        with self.assertRaises(ValueError):
            Order(1, "T04", discount_percent=150)
        with self.assertRaises(ValueError):
            Order(1, "T04", discount_percent=-10)


class TestBillingSystemMenuManagement(unittest.TestCase):
    def setUp(self):
        self._cleanup()
        self.bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        for f in (TEST_MENU_FILE, TEST_ORDERS_FILE):
            if os.path.exists(f):
                os.remove(f)

    def test_add_menu_item_assigns_incrementing_ids(self):
        m1 = self.bs.add_menu_item("Pizza", 12.5, "Main")
        m2 = self.bs.add_menu_item("Coke", 2.5, "Beverage")
        self.assertEqual(m1.item_id, 1)
        self.assertEqual(m2.item_id, 2)

    def test_duplicate_menu_item_names_allowed(self):
        """Duplicate scenario: two menu items with the same name are distinct entries."""
        m1 = self.bs.add_menu_item("Lemonade", 3.0, "Beverage")
        m2 = self.bs.add_menu_item("Lemonade", 3.5, "Beverage")
        self.assertNotEqual(m1.item_id, m2.item_id)

    def test_delete_nonexistent_menu_item_returns_false(self):
        self.assertFalse(self.bs.delete_menu_item(999))

    def test_search_menu_case_insensitive(self):
        self.bs.add_menu_item("Margherita Pizza", 11.0, "Main")
        results = self.bs.search_menu("pizza")
        self.assertEqual(len(results), 1)


class TestBillingSystemOrderWorkflow(unittest.TestCase):
    def setUp(self):
        self._cleanup()
        self.bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        self.pizza = self.bs.add_menu_item("Pizza", 12.50, "Main")
        self.coke = self.bs.add_menu_item("Coke", 2.50, "Beverage")

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        for f in (TEST_MENU_FILE, TEST_ORDERS_FILE):
            if os.path.exists(f):
                os.remove(f)

    def test_full_order_to_bill_workflow(self):
        """End-to-end: create order, add items, apply discount, generate bill."""
        order = self.bs.create_order("T04", tax_percent=8)
        self.bs.add_item_to_order(order.order_id, self.pizza.item_id, 2)
        self.bs.apply_discount(order.order_id, 10)
        billed = self.bs.generate_bill(order.order_id)
        self.assertEqual(billed.status, "Billed")
        self.assertEqual(billed.total, 24.30)  # 25 - 10% = 22.5, +8% tax = 24.30

    def test_cannot_bill_order_with_no_items(self):
        """Missing-data scenario: an empty order cannot be billed."""
        order = self.bs.create_order("T05")
        with self.assertRaises(ValueError):
            self.bs.generate_bill(order.order_id)

    def test_cannot_modify_billed_order(self):
        order = self.bs.create_order("T06")
        self.bs.add_item_to_order(order.order_id, self.pizza.item_id, 1)
        self.bs.generate_bill(order.order_id)
        with self.assertRaises(ValueError):
            self.bs.add_item_to_order(order.order_id, self.coke.item_id, 1)

    def test_add_item_to_nonexistent_order_raises(self):
        with self.assertRaises(ValueError):
            self.bs.add_item_to_order(999, self.pizza.item_id, 1)

    def test_remove_item_from_order(self):
        order = self.bs.create_order("T07")
        self.bs.add_item_to_order(order.order_id, self.pizza.item_id, 1)
        removed = self.bs.remove_item_from_order(order.order_id, self.pizza.item_id)
        self.assertTrue(removed)
        self.assertEqual(len(order.items), 0)

    def test_cancel_order(self):
        order = self.bs.create_order("T08")
        cancelled = self.bs.cancel_order(order.order_id)
        self.assertEqual(cancelled.status, "Cancelled")


class TestPersistenceAndReports(unittest.TestCase):
    def setUp(self):
        self._cleanup()

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        for f in (TEST_MENU_FILE, TEST_ORDERS_FILE):
            if os.path.exists(f):
                os.remove(f)
        export_path = os.path.join(os.path.dirname(__file__), "test_orders_export.csv")
        if os.path.exists(export_path):
            os.remove(export_path)

    def test_missing_files_start_empty(self):
        bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        self.assertEqual(bs.menu, [])
        self.assertEqual(bs.orders, [])

    def test_data_persists_across_instances(self):
        bs1 = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        pizza = bs1.add_menu_item("Pizza", 12.5, "Main")
        order = bs1.create_order("T04")
        bs1.add_item_to_order(order.order_id, pizza.item_id, 2)

        bs2 = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        self.assertEqual(len(bs2.menu), 1)
        self.assertEqual(len(bs2.orders), 1)
        self.assertEqual(bs2.orders[0].items[0].quantity, 2)

    def test_corrupt_menu_file_handled_gracefully(self):
        with open(TEST_MENU_FILE, "w", encoding="utf-8") as f:
            f.write("{ not valid json ]]")
        bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        self.assertEqual(bs.menu, [])

    def test_sales_summary_on_empty_system(self):
        """Boundary condition: summary math shouldn't divide by zero with no orders."""
        bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        summary = bs.sales_summary()
        self.assertEqual(summary["billed_orders"], 0)
        self.assertEqual(summary["average_order_value"], 0.0)

    def test_sales_summary_calculates_correctly(self):
        bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        pizza = bs.add_menu_item("Pizza", 10.0, "Main")
        order = bs.create_order("T01", tax_percent=0)
        bs.add_item_to_order(order.order_id, pizza.item_id, 1)
        bs.generate_bill(order.order_id)
        summary = bs.sales_summary()
        self.assertEqual(summary["billed_orders"], 1)
        self.assertEqual(summary["total_revenue"], 10.0)

    def test_csv_export_creates_file(self):
        bs = BillingSystem(menu_file=TEST_MENU_FILE, orders_file=TEST_ORDERS_FILE)
        pizza = bs.add_menu_item("Pizza", 10.0, "Main")
        order = bs.create_order("T01")
        bs.add_item_to_order(order.order_id, pizza.item_id, 1)
        export_path = os.path.join(os.path.dirname(__file__), "test_orders_export.csv")
        result = bs.export_orders_to_csv(export_path)
        self.assertTrue(os.path.exists(result))


if __name__ == "__main__":
    unittest.main(verbosity=2)
