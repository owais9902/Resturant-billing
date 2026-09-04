# Project Report — Restaurant Billing System

## 1. Problem Understanding

A restaurant needs to record what each table ordered, compute an
accurate bill (subtotal, discount, tax, total), and produce a
receipt — reliably, and without manual calculation errors. The billing
math itself (discount applied before tax, correct rounding) is the
part most likely to go wrong if implemented ad hoc, so it needed to be
centralized, tested, and derived automatically from the order's items
rather than tracked as separate fields that could drift out of sync.

## 2. Proposed Approach

Four-layer separation:

1. **`MenuItem`** — one sellable item; guarantees valid name/price/category.
2. **`OrderItem` / `Order`** — one line item, and a full table order.
   All bill math (subtotal → discount → tax → total) is computed as
   properties on `Order`, always derived live from its `items` list.
3. **`BillingSystem`** — owns the menu and all orders; provides every
   operation (menu CRUD, order lifecycle, search/filter/sort, receipt
   formatting, sales reporting, persistence).
4. **`main.py`** — a thin CLI that only handles input/output.

## 3. Implementation

- **Data structures:** `list` for the menu and orders collections;
  dictionaries for JSON/CSV round-tripping and the sales-summary report.
- **Conditional logic & loops:** menu loop in `main.py`; validation
  branching in `MenuItem`/`Order`; list comprehensions for search/filter.
- **Input validation:** name/price/category validated in `MenuItem`;
  quantity/discount/tax/table-number/status validated in `Order`.
  Duration-style bounds apply here too (e.g. quantity 1–100, discount
  and tax 0–100%).
- **Exception handling:** `ValueError` for bad data or invalid
  operations (billing an empty order, modifying a billed order); file
  I/O wrapped in `try/except` for both save and load paths.
- **File handling / JSON / CSV:** menu and orders are two separate
  JSON files, both auto-saved after every mutating call; orders can
  also be exported to CSV via `csv.DictWriter`.
- **OOP:** three classes (`MenuItem`, `Order`/`OrderItem`,
  `BillingSystem`), with computed `@property` values for all bill
  totals so they can never be manually miscalculated or left stale.
- **Search / filter / sort:** menu search by name, filter by category,
  sort by price; orders filterable by status/table and sortable by total.
- **Persistence:** save-on-every-write for both menu and orders, so a
  crash or force-quit never loses billed history.

## 4. Important Technical Decisions

- **Bill totals are computed properties, never stored fields.**
  `subtotal`, `discount_amount`, `tax_amount`, and `total` are
  recalculated from `order.items` and the discount/tax percentages
  every time they're read. This makes it impossible for the displayed
  total to drift from the actual line items — a common bug class in
  billing systems where totals are cached and forgotten.
- **Discount is applied before tax**, i.e. tax is calculated on the
  post-discount amount, matching standard retail/restaurant tax
  practice (not tax-then-discount). This is explicitly tested in
  `test_bill_calculation_matches_expected_values`.
- **Billed and cancelled orders are locked.** Once `generate_bill()` or
  `cancel_order()` runs, no further items can be added or removed —
  enforced in `BillingSystem.add_item_to_order`/`remove_item_from_order`
  — so a printed receipt can never silently become inaccurate.
- **Adding the same menu item twice increases quantity** rather than
  creating a duplicate line, matching how a server would actually enter
  "another pizza" for the same table.
- **Two separate JSON files** (menu vs. orders) rather than one
  combined file, since the menu changes rarely and orders change
  constantly — keeping them separate avoids rewriting the whole menu
  on every single order update.

## 5. Testing Performed

27 automated `unittest` cases across 5 test classes (see `README.md`
for the full table):

- **Normal inputs** — valid menu item creation, correct subtotal/
  discount/tax/total math, correct sales-summary calculation.
- **Invalid inputs** — empty item name, zero/negative price, invalid
  category, non-positive quantity, out-of-range discount percent.
- **Boundary conditions** — zero discount and zero tax (total equals
  subtotal exactly); empty-system sales summary (no divide-by-zero).
- **Duplicate data** — two menu items with the same name are tracked
  as distinct entries; adding the same item twice to one order merges
  quantities instead of duplicating the line.
- **Missing/corrupt data** — billing an order with no items is
  rejected; modifying an already-billed order is rejected; adding to a
  nonexistent order raises a clear error; missing or corrupted JSON
  files are handled without crashing the app.

Manual end-to-end testing was also performed by running the actual
`main.py`/`billing.py` code through the required example scenario
(table T04, Pizza x2, with discount and tax), confirming the printed
receipt matches the expected total exactly.

## 6. Challenges Encountered & Solutions

- **Challenge:** deciding the order of operations for discount vs. tax.
  **Solution:** applied discount first, then computed tax on the
  discounted amount, and wrote an explicit test asserting the exact
  expected numbers for a realistic order, so the calculation order is
  locked in and verified rather than assumed.
- **Challenge:** preventing a receipt from becoming inaccurate after
  it's printed (e.g. someone accidentally adding an item to an already-
  billed order). **Solution:** `BillingSystem` checks `order.status`
  before allowing any item modification and raises `ValueError` if the
  order isn't `Open`.
- **Challenge:** avoiding floating-point rounding drift across
  subtotal → discount → tax → total. **Solution:** every monetary
  property rounds to 2 decimal places at the point of calculation
  (`round(..., 2)`), and the test suite checks exact expected totals
  rather than approximate ones.
- **Challenge:** re-linking saved order items back to menu items after
  a JSON reload, since orders reference items by ID, not full objects.
  **Solution:** `Order.from_dict` accepts a `menu_lookup` dict built
  from the already-loaded menu, so `BillingSystem.load_orders` can
  correctly reconstruct each order's items after restart.

## 7. Future Scope

- Flat-amount and itemized (per-line) discounts, not just a single
  percentage on the whole order.
- Split-bill support for one table across multiple payers.
- A web or GUI front end reusing `BillingSystem` unchanged.
- Inventory tracking so orders can deplete menu-item stock.
- Staff accounts and shift-based sales reporting.
