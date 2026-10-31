# A tiny deterministic factory source

From the workspace root:

```sh
python3 simulator/fixture.py
```

This prints one JSON document containing three source tables. It installs nothing, connects to no database, and does not write files. Fixed records are sufficient here: there is no random generator, seed argument, current clock, or configurable row count.

## What the fixture contains

| Table | Grain | Primary key | Rows |
|---|---|---|---:|
| `products` | One 1 kg product/SKU | `product_id` | 3 |
| `orders` | One order header | `order_id` | 2 |
| `order_lines` | One product line within an order | `line_id` | 3 |

- Order **100** is shipped, with two lines for vanilla and chocolate.
- Order **101** is cancelled, with one strawberry line.
- Each line references an existing order and product.
- Source timestamps are fixed on **2026-01-05**, in UTC (`Z`). `updated_at` is present on every row for later ingestion exercises; this snapshot does not simulate changes.
- Money is serialized as two-decimal **USD strings**. Parse it with `Decimal`, not `float`, and map it to MySQL `DECIMAL` when building a real loader. The JSON itself does not enforce database types or constraints.
- `quantity` counts packs; `line_discount` is a discount on the entire line, not each pack. Taxes and returns are excluded.

## Know the answer before loading

| Line | Order status | Calculation | Net USD |
|---|---|---|---:|
| 1 | shipped | `4 × 5.00 − 2.00` | 18.00 |
| 2 | shipped | `3 × 9.00 − 0.00` | 27.00 |
| 3 | cancelled | `5 × 10.00 − 0.00` | 50.00 |

**Expected shipped sales: $45.00 from two lines and one order.** Summing all three lines incorrectly gives $95.00. There should still be **three raw order lines**: preserving source data and excluding cancelled sales from a mart are different responsibilities.

The earlier two-line SQL/dashboard examples omit the cancelled control order. Their shipped-sales answer is the same, but their raw-row count is two instead of three.

## Use it from Python

```python
from simulator.fixture import build_fixture

source = build_fixture()
print(len(source["order_lines"]))  # 3
```

Each call returns fresh dictionaries and lists, so changing a returned record does not modify the next fixture. The CLI emits stable, sorted JSON keys and preserves the explicit row order.

## Verify it

```sh
python3 -m unittest discover -s tests -p test_fixture.py -v
```

The five standard-library tests check:

1. Table counts, unique keys, and valid order/product references.
2. Exact decimal amounts and the cancelled-order exclusion.
3. Fixed UTC timestamps and sensible order/update ordering.
4. Independent fixture instances after mutation.
5. Byte-identical CLI output across fresh processes, including execution outside the workspace and no files written there.

**Try it:** in a practice script, add a shipped line to the returned data, predict the new total, and reconcile it. Do not silently update expected totals just to make a failed test pass—first explain the intended data change.

**Next boundary:** loading this JSON into MySQL requires explicit schema/type mapping and a safe seeding policy. Neither a database loader nor incremental updates are implemented here. Your existing `practices/0001/load.py` is unchanged.
