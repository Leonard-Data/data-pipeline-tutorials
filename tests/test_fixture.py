"""Standard-library tests: python3 -m unittest discover -s tests -p test_fixture.py -v."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from simulator.fixture import build_fixture

ROOT = Path(__file__).resolve().parents[1]


class SourceFixtureTests(unittest.TestCase):
    def test_tables_have_unique_keys_and_valid_relationships(self):
        fixture = build_fixture()
        self.assertEqual(set(fixture), {"products", "orders", "order_lines"})
        self.assertEqual({table: len(rows) for table, rows in fixture.items()}, {
            "products": 3, "orders": 2, "order_lines": 3,
        })
        for table, key in [("products", "product_id"), ("orders", "order_id"), ("order_lines", "line_id")]:
            keys = [row[key] for row in fixture[table]]
            self.assertEqual(len(keys), len(set(keys)), table)
        orders = {row["order_id"] for row in fixture["orders"]}
        products = {row["product_id"] for row in fixture["products"]}
        for line in fixture["order_lines"]:
            self.assertIn(line["order_id"], orders)
            self.assertIn(line["product_id"], products)
        self.assertEqual(sum(line["order_id"] == 100 for line in fixture["order_lines"]), 2)

    def test_exact_shipped_sales_excludes_the_cancelled_order(self):
        fixture = build_fixture()
        orders = {row["order_id"]: row for row in fixture["orders"]}
        shipped_amounts = []
        all_amounts = []
        for line in fixture["order_lines"]:
            self.assertIsInstance(line["quantity"], int)
            self.assertGreater(line["quantity"], 0)
            for field in ["unit_price", "line_discount"]:
                self.assertRegex(line[field], r"^\d+\.\d{2}$")
            amount = line["quantity"] * Decimal(line["unit_price"]) - Decimal(line["line_discount"])
            self.assertGreaterEqual(amount, Decimal("0.00"))
            all_amounts.append(amount)
            if orders[line["order_id"]]["status"] == "shipped":
                shipped_amounts.append(amount)
        self.assertEqual(len(shipped_amounts), 2)
        self.assertEqual(sum(shipped_amounts), Decimal("45.00"))
        self.assertEqual(sum(all_amounts), Decimal("95.00"))
        self.assertEqual({row["status"] for row in fixture["orders"]}, {"shipped", "cancelled"})

    def test_timestamps_are_fixed_utc_and_updates_do_not_precede_orders(self):
        fixture = build_fixture()
        for rows in fixture.values():
            for row in rows:
                value = datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                self.assertEqual(value.tzinfo, timezone.utc)
                self.assertEqual(value.date().isoformat(), "2026-01-05")
        for order in fixture["orders"]:
            ordered = datetime.fromisoformat(order["ordered_at"].replace("Z", "+00:00"))
            updated = datetime.fromisoformat(order["updated_at"].replace("Z", "+00:00"))
            self.assertLessEqual(ordered, updated)

    def test_calls_return_fresh_data_without_shared_mutable_rows(self):
        first = build_fixture()
        first["order_lines"][0]["quantity"] = 999
        first["orders"].clear()
        second = build_fixture()
        self.assertEqual(second["order_lines"][0]["quantity"], 4)
        self.assertEqual(len(second["orders"]), 2)

    def test_cli_emits_identical_json_from_another_directory_without_writing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = [subprocess.run(
                [sys.executable, str(ROOT / "simulator/fixture.py")],
                cwd=directory, capture_output=True, check=True,
            ) for _ in range(2)]
            self.assertEqual(runs[0].stdout, runs[1].stdout)
            self.assertEqual(runs[0].stderr, b"")
            parsed = json.loads(runs[0].stdout)
            self.assertEqual(len(parsed["order_lines"]), 3)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
