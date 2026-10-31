source_rows = [
    {"line_id": 1, "status": "shipped", "net_cents": 1800},
    {"line_id": 2, "status": "shipped", "net_cents": 2700},
    {"line_id": 3, "status": "cancelled", "net_cents": 5000},
]


def summarize(rows: list[dict]) -> dict:
    shipped = [row for row in rows if row["status"] =="shipped"]
    return {
        "shipped_count": len(shipped),
        "net_cents": sum(row["net_cents"] for row in shipped)
    }


# ELT: copy source-shaped rows into our pretend warehouse, then transform.
warehouse_raw = [row.copy() for row in source_rows]
mart_elt = summarize(warehouse_raw)

print("ELT:", mart_elt)

#ETL: transform first