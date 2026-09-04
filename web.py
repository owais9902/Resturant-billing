"""
web.py
-------
Flask web front end for Lazeez-e-Hyderabadi's Restaurant Billing System.

Reuses the existing MenuItem/Order/BillingSystem classes from
menu_item.py / order.py / billing.py unchanged -- this file only adds
routes (URLs) and renders HTML templates. All validation, bill math,
and persistence logic still lives in billing.py / order.py / menu_item.py.

Run with:
    python3 web.py
Then open:
    http://127.0.0.1:5000
"""

import io

from flask import Flask, render_template, request, redirect, url_for, flash, send_file

from billing import BillingSystem

RESTAURANT_NAME = "Lazeez-e-Hyderabadi"

app = Flask(__name__)
app.secret_key = "lazeez-e-hyderabadi-dev-key"  # only needed for flash messages
app.jinja_env.globals["restaurant_name"] = RESTAURANT_NAME

bs = BillingSystem(menu_file="data/menu.json", orders_file="data/orders.json")


# ----------------------------------------------------------------------
# Dashboard: menu board + ticket rail (all orders)
# ----------------------------------------------------------------------
@app.route("/")
def index():
    status = request.args.get("status", "").strip()
    sort_key = request.args.get("sort", "order_id").strip()
    order = request.args.get("order", "desc").strip()

    orders = bs.orders
    if status:
        orders = bs.filter_orders_by_status(status)

    reverse = order == "desc"
    try:
        orders = sorted(orders, key=lambda o: (o.total if sort_key == "total" else getattr(o, sort_key)), reverse=reverse)
    except AttributeError:
        pass

    summary = bs.sales_summary()
    return render_template(
        "index.html", menu=bs.menu, orders=orders, summary=summary,
        status=status, sort_key=sort_key, order=order,
    )


# ----------------------------------------------------------------------
# Menu management
# ----------------------------------------------------------------------
@app.route("/menu/add", methods=["GET", "POST"])
def add_menu_item():
    if request.method == "POST":
        name = request.form.get("name", "")
        price = request.form.get("price", "")
        category = request.form.get("category", "")
        try:
            bs.add_menu_item(name, price, category)
            flash(f'Added "{name}" to the menu.', "success")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("menu_form.html", name=name, price=price, category=category)
    return render_template("menu_form.html")


@app.route("/menu/delete/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):
    if bs.delete_menu_item(item_id):
        flash("Menu item deleted.", "success")
    else:
        flash(f"No menu item found with ID {item_id}.", "error")
    return redirect(url_for("index"))


# ----------------------------------------------------------------------
# Order lifecycle
# ----------------------------------------------------------------------
@app.route("/order/create", methods=["POST"])
def create_order():
    table = request.form.get("table", "")
    tax = request.form.get("tax", "5.0")
    try:
        order = bs.create_order(table, tax_percent=tax)
        flash(f"Order #{order.order_id} started for table {order.table_number}.", "success")
        return redirect(url_for("view_order", order_id=order.order_id))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))


@app.route("/order/<int:order_id>")
def view_order(order_id):
    order = bs.get_order(order_id)
    if order is None:
        flash(f"No order found with ID {order_id}.", "error")
        return redirect(url_for("index"))
    return render_template("order.html", order=order, menu=bs.menu)


@app.route("/order/<int:order_id>/add_item", methods=["POST"])
def add_item_to_order(order_id):
    item_id = request.form.get("item_id", "")
    quantity = request.form.get("quantity", "1")
    try:
        bs.add_item_to_order(order_id, int(item_id), quantity)
    except (ValueError, TypeError) as e:
        flash(str(e), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/order/<int:order_id>/remove_item/<int:item_id>", methods=["POST"])
def remove_item_from_order(order_id, item_id):
    try:
        bs.remove_item_from_order(order_id, item_id)
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/order/<int:order_id>/discount", methods=["POST"])
def apply_discount(order_id):
    discount = request.form.get("discount", "0")
    try:
        bs.apply_discount(order_id, discount)
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/order/<int:order_id>/bill", methods=["POST"])
def generate_bill(order_id):
    try:
        bs.generate_bill(order_id)
        flash(f"Order #{order_id} billed.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/order/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    try:
        bs.cancel_order(order_id)
        flash(f"Order #{order_id} cancelled.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/order/<int:order_id>/receipt")
def receipt(order_id):
    order = bs.get_order(order_id)
    if order is None:
        flash(f"No order found with ID {order_id}.", "error")
        return redirect(url_for("index"))
    receipt_text = bs.format_receipt(order_id)
    return render_template("receipt.html", order=order, receipt_text=receipt_text)


@app.route("/order/<int:order_id>/receipt/download")
def download_receipt(order_id):
    """Download the receipt as a plain-text .txt file."""
    order = bs.get_order(order_id)
    if order is None:
        flash(f"No order found with ID {order_id}.", "error")
        return redirect(url_for("index"))
    receipt_text = bs.format_receipt(order_id)
    buffer = io.BytesIO(receipt_text.encode("utf-8"))
    filename = f"{RESTAURANT_NAME.replace(' ', '_')}_Receipt_Order{order_id}.txt"
    return send_file(
        buffer, mimetype="text/plain", as_attachment=True, download_name=filename
    )


# ----------------------------------------------------------------------
# Reports
# ----------------------------------------------------------------------
@app.route("/summary")
def summary():
    return render_template("summary.html", summary=bs.sales_summary())


@app.route("/export")
def export_csv():
    path = bs.export_orders_to_csv("data/orders_export.csv")
    return send_file(path, as_attachment=True, download_name="orders_export.csv")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
