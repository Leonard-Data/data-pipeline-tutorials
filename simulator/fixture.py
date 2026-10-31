"""Emit a fixed, synthetic factory source snapshot as JSON; no services required."""
import json


UPDATED_AT = "2026-01-05T11:00:00Z"


def build_fixture():
    """Return fresh source tables; money strings represent exact USD decimals."""
    return {
        "products": [
            {"product_id": 10, "product_name": "Vanilla 1 kg", "flavor": "vanilla", "pack_size_g": 1000, "updated_at": UPDATED_AT},
            {"product_id": 20, "product_name": "Chocolate 1 kg", "flavor": "chocolate", "pack_size_g": 1000, "updated_at": UPDATED_AT},
            {"product_id": 30, "product_name": "Strawberry 1 kg", "flavor": "strawberry", "pack_size_g": 1000, "updated_at": UPDATED_AT},
        ],
        "orders": [
            {"order_id": 100, "ordered_at": "2026-01-05T10:00:00Z", "status": "shipped", "updated_at": UPDATED_AT},
            {"order_id": 101, "ordered_at": "2026-01-05T10:30:00Z", "status": "cancelled", "updated_at": UPDATED_AT},
        ],
        "order_lines": [
            {
                "line_id": 1, "order_id": 100, "product_id": 10,
                "quantity": 4, "unit_price": "5.00", "line_discount": "2.00",
                "updated_at": UPDATED_AT,
            },
            {
                "line_id": 2, "order_id": 100, "product_id": 20,
                "quantity": 3, "unit_price": "9.00", "line_discount": "0.00",
                "updated_at": UPDATED_AT,
            },
            {
                "line_id": 3, "order_id": 101, "product_id": 30,
                "quantity": 5, "unit_price": "10.00", "line_discount": "0.00",
                "updated_at": UPDATED_AT,
            },
        ],
    }


if __name__ == "__main__":
    print(json.dumps(build_fixture(), indent=2, sort_keys=True))
