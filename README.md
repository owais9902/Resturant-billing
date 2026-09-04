# Lazeez-e-Hyderabadi — Restaurant Billing System

A Restaurant Billing System — available as a CLI, a Flask web app, and
a pure HTML/CSS/JS web app — for **Lazeez-e-Hyderabadi**, a Hyderabadi
restaurant serving biryani, mutton and chicken curries, shawarma, and
cold drinks. Manages the menu, takes table orders, applies discounts
and taxes, and generates downloadable itemized receipts.

## Problem Statement

Lazeez-e-Hyderabadi needs a simple, reliable way to record what each
table ordered, calculate the correct bill (accounting for discounts
and tax), and produce an accurate, downloadable receipt — without
manual arithmetic errors or losing track of open tables.

## Objective

Build a functional Python CLI application that lets staff:

- Manage a **menu** (add/search/filter/sort items by name, price, category).
- Take an **order** per table, adding items with quantities.
- Apply a **discount** and compute **tax** automatically.
- Generate an accurate **itemized receipt** with subtotal, discount,
  tax, and total.
- Persist all data between runs and track sales over time.

## Features

| # | Feature | Description |
|---|---------|--------------|
| 1 | Add menu item | Name, price, category (Starter/Main/Dessert/Beverage/Other) |
| 2 | View menu | Lists every menu item |
| 3 | Search/filter/sort menu | By name (search), category (filter), price (sort) |
| 4 | Create order | New order for a table number (e.g. T04) |
| 5 | Add item to order | Item + quantity; adding the same item again increases quantity |
| 6 | Remove item from order | Remove a line item before billing |
| 7 | Apply discount | Percentage discount (0–100%) on the order subtotal |
| 8 | View order | Running total before billing |
| 9 | Generate bill / receipt | Locks the order (`Billed`) and prints a formatted receipt |
| 10 | **Download receipt** | Receipt downloads as a `.txt` file (Flask and pure-JS web versions) |
| 11 | Cancel order | Marks an order `Cancelled` |
| 12 | View all orders | Filter by status/table, or sort by total |
| 13 | Sales summary | Revenue, order counts, average order value |
| 14 | Export orders to CSV | Snapshot of all orders as a `.csv` file |

Every change is saved immediately to `data/menu.json` and
`data/orders.json`, so nothing is lost between runs.

### Menu

**Starters / Kebabs:** Chicken Seekh Kebab, Mutton Seekh Kebab,
Chicken 65, Mutton Fry

**Biryani:** Hyderabadi Chicken Biryani, Hyderabadi Mutton Biryani,
Vegetable Biryani, Egg Biryani

**Chicken Curries & Dishes:** Chicken Curry, Chicken Korma, Butter
Chicken, Chicken Tikka Masala, Chicken Chettinad

**Mutton Curries & Dishes:** Mutton Curry, Mutton Korma, Mutton Rogan
Josh, Mutton Kheema, Mutton Chukka

**Shawarma:** Chicken Shawarma Roll, Mutton Shawarma Roll, Chicken
Shawarma Plate

**Desserts:** Double Ka Meetha, Qubani Ka Meetha

**Cold Drinks:** Coca-Cola, Sprite, Mango Lassi, Sweet Lassi, Masala
Soda

(All three versions — CLI, Flask, and pure-JS — ship pre-seeded with
this full menu and two sample orders.)

### Example workflow (matches the required scenario)

```
Create order for table T04
Add Hyderabadi Chicken Biryani x2
Add Coca-Cola x2
Apply 10% discount, 5% tax
Generate bill → downloadable receipt:

========================================
        LAZEEZ-E-HYDERABADI
           RESTAURANT RECEIPT
========================================
Order #: 1    Table: T04
Status: Billed
----------------------------------------
Hyderabadi Chicken B x2     $500.00
Coca-Cola            x2      $80.00
----------------------------------------
Subtotal:                   $580.00
Discount (10%):             -$58.00
Tax (5%):                    $26.10
========================================
TOTAL:                      $548.10
========================================
```

## Technologies Used

- **Python 3** (standard library only)
- `json` — data persistence for menu and orders
- `csv` — order export
- `datetime` — order timestamps
- `unittest` — automated testing

## Installation / Setup Instructions

```bash
python3 --version   # need Python 3.8+
```

No `pip install` required — the project uses only the standard library.

## How to Run the Project

From inside the `restaurant_billing/` folder:

```bash
python3 main.py
```

Enter a menu number and follow the prompts. Choose `0` to exit.

## Web Version — Pure HTML/CSS/JavaScript (No Server Needed)

`web/index.html` is a fully self-contained, client-side web app — plain
HTML, CSS, and vanilla JavaScript, no Python, no Flask, no build step,
no dependencies of any kind.

### Run it

Just open the file directly in any browser:

```bash
open web/index.html        # macOS
start web/index.html       # Windows
xdg-open web/index.html    # Linux
```

Or double-click `web/index.html` in your file explorer, or drag it
into an open browser window.

### What it does

- **Menu Board** — add/search/filter menu items by name, price, category
- **Current Ticket** — start an order for a table, add items with a
  click, adjust quantities, set discount % and tax %, live totals
- **Fire & Bill** — locks the order and prints an animated receipt
  (subtotal → discount → tax → total, same math as the Python backend)
- **Download Receipt** — one click downloads the receipt as a `.txt`
  file (built client-side with a `Blob` + temporary download link)
- **Ticket Rail** — sales stats, all orders, filterable/sortable

All the same validation rules (empty names, non-positive price/
quantity, out-of-range discount/tax) and the same discount-before-tax
billing math as `billing.py`/`order.py` are reimplemented in
JavaScript in this file.

**Note:** this version keeps all data in the browser's memory for the
current tab only — it comes pre-seeded with sample data, and refreshing
the page resets it. It does not read or write `data/menu.json` /
`data/orders.json`; those are used only by `main.py` (CLI) and `web.py`
(Flask). All three versions implement the same business logic
independently, in their respective languages.

## Web Version — Flask (Python Backend)

The same `MenuItem`/`Order`/`BillingSystem` logic is also available as a
local web app (`web.py`), built with Flask.

### Install the one extra dependency

```bash
pip install -r requirements.txt
```

### Run it

```bash
python3 web.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

You get a dashboard to manage the menu, start orders per table, add
items/quantities, apply discounts, generate bills, view formatted
receipts, **download a receipt as a `.txt` file**, and export orders to
CSV — all backed by the same validated logic as the CLI. Press
`Ctrl+C` to stop the server.

## Project Structure

```
restaurant_billing/
├── main.py              # CLI entry point / menu loop
├── web.py                # Flask web front end (optional, reuses billing.py etc.)
├── web/
│   └── index.html         # Pure HTML/CSS/JS web app (no server, open directly in browser)
├── menu_item.py          # MenuItem class (model + validation)
├── order.py              # OrderItem + Order classes (bill math)
├── billing.py            # BillingSystem class (business logic + persistence)
├── templates/             # HTML templates used by web.py (Flask version only)
│   ├── base.html
│   ├── index.html
│   ├── order.html
│   ├── menu_form.html
│   ├── receipt.html
│   └── summary.html
├── requirements.txt       # Only needed for the Flask web version
├── data/
│   ├── menu.json          # Auto-created menu data store (CLI/Flask only)
│   ├── orders.json        # Auto-created order data store (CLI/Flask only)
│   └── orders_export.csv  # Created when exporting orders
├── tests/
│   └── test_billing.py    # 27 automated unit tests
├── docs/
│   └── project_report.md  # Project report
└── README.md
```

### Design overview

- **`menu_item.py`** — `MenuItem` validates name, price (0 < price ≤
  100000), and category on construction, so an item is never invalid
  once created.
- **`order.py`** — `OrderItem` (one line: item + quantity) and `Order`
  (a table's full order). All bill math — subtotal, discount amount,
  taxable amount, tax amount, total — lives here as computed
  properties, so it's always derived fresh from the current items
  rather than manually kept in sync.
- **`billing.py`** — `BillingSystem` owns the menu and order
  collections and every operation on them: menu CRUD, order lifecycle
  (create → add/remove items → discount → bill/cancel), search/filter/
  sort, receipt formatting, sales reporting, and JSON/CSV persistence.
- **`main.py`** — a thin CLI layer that only collects input and
  delegates to `BillingSystem`, catching `ValueError`/`IOError` so bad
  input never crashes the app.

## Testing Details

Run the full automated test suite:

```bash
python3 -m unittest discover -s tests -v
```

**27 tests, all passing**, across 5 test classes:

| Test class | What it covers |
|---|---|
| `TestMenuItemValidation` | Valid item creation, empty name, zero/negative price, invalid category, price rounding |
| `TestOrderItemAndCalculations` | Quantity validation, subtotal math, duplicate item merging, full bill calculation (subtotal/discount/tax/total), zero-discount/tax boundary, invalid discount percent |
| `TestBillingSystemMenuManagement` | Auto-incrementing IDs, duplicate item names allowed, deleting a missing item, case-insensitive search |
| `TestBillingSystemOrderWorkflow` | Full order→bill workflow, billing an empty order (rejected), modifying a billed order (rejected), adding to a missing order (rejected), removing an item, cancelling an order |
| `TestPersistenceAndReports` | Missing files start empty, data persists across instances, corrupt JSON handled gracefully, empty-system sales summary (no divide-by-zero), correct summary math, CSV export |

This covers **normal inputs, invalid inputs, boundary conditions,
duplicate data, and missing/corrupt data**, per the assignment
requirements.

## Limitations

- Single-location, local file storage — no multi-user/concurrent access.
- No login/staff accounts — anyone running the app has full access.
- Discount is percentage-only (no flat-amount or itemized discounts).
- No printer integration — receipts print to the terminal only.
- No support for split bills across multiple parties at one table.

## Future Improvements

- A GUI or web front end (e.g. Flask) reusing `BillingSystem` unchanged.
- Flat-amount and itemized discounts, plus discount codes.
- Split-bill support and multiple simultaneous orders per table.
- Inventory tracking tied to menu items (stock depletion on order).
- Staff accounts and per-shift sales reporting.
