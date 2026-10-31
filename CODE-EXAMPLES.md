# Annotated factory examples

These are **teaching excerpts, not a deployed application**. The Python fixture and freshness self-check run with the standard library. The other examples need the services, files, credentials, permissions, and compatible package versions named beside them. They are not executed by this page.

## Python · Establish an answer before a pipeline

**Milestone M1. File: `fixture.py`. Runnable as-is with Python.** One row means one order line. The discount is a total for that line, not a per-item discount. Money uses `Decimal`, not binary floating point.

```python
from decimal import Decimal

lines = [
    {"line_id": 1, "quantity": 4, "unit_price": Decimal("5.00"), "discount": Decimal("2.00")},
    {"line_id": 2, "quantity": 3, "unit_price": Decimal("9.00"), "discount": Decimal("0.00")},
]
total = sum(
    (line["quantity"] * line["unit_price"] - line["discount"] for line in lines),
    Decimal("0.00"),
)
assert total == Decimal("45.00")
print(f"Expected net shipped sales: ${total:.2f}")
```

**Try it:** change the second quantity from 3 to 4. Predict the total before running it. The new total should be $54.00. All values here and in the browser experiment are synthetic USD examples; returns and taxes are excluded.

## MySQL · Declare the source grain

**Milestone M1. File: `seed.sql`. Requires a new, empty tutorial database and a user allowed to create its tables.** This is a deliberately tiny source, not the full factory schema. IDs are explicit to keep the fixture deterministic. Do not rerun these inserts against an already-seeded database; duplicate keys should fail rather than silently change the fixture.

```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    ordered_at DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL
);
CREATE TABLE order_lines (
    line_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    line_discount DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
INSERT INTO orders VALUES (100, '2026-01-05 10:00:00', 'shipped');
INSERT INTO order_lines VALUES
    (1, 100, 10, 4, 5.00, 2.00),
    (2, 100, 20, 3, 9.00, 0.00);

SELECT SUM(l.quantity * l.unit_price - l.line_discount) AS net_sales
FROM order_lines AS l
JOIN orders AS o ON l.order_id = o.order_id
WHERE o.status = 'shipped';
-- Expected: 45.00, from two lines belonging to one order.
```

**When:** transactions and referential constraints belong at the operational source. Document that this fixture's timestamps are UTC. The larger project adds product/factory tables, checks, and reliable change timestamps before incremental extraction. [MySQL tutorial](https://dev.mysql.com/doc/refman/8.4/en/tutorial.html)

## dlt · Extract and load a small full snapshot

**Milestone M2. File: `ingestion/load.py`. Requires dlt SQL/ClickHouse dependencies, a MySQL driver, source credentials, and a configured ClickHouse destination.** `MYSQL_SOURCE_URL` is a server-side SQLAlchemy MySQL URL supplied through the environment, never committed. Do not execute until the destination is an isolated tutorial database.

```python
import os
import dlt
from dlt.sources.sql_database import sql_database

source = sql_database(
    credentials=os.environ["MYSQL_SOURCE_URL"],
    table_names=["orders", "order_lines"],
)
pipeline = dlt.pipeline(
    pipeline_name="factory_tutorial",
    destination="clickhouse",
    dataset_name="raw",
)
# Full snapshot of these selected tables; replaces their destination data.
load_info = pipeline.run(source, write_disposition="replace")
print(load_info)
```

**Companion config: `.dlt/config.toml`.** The separator is explicit because dlt emulates datasets with table-name prefixes in ClickHouse. With this configuration, inspect `raw__orders` and `raw__order_lines` in the destination database. Do not assume that `raw` is a native nested schema.

```toml
[destination.clickhouse]
dataset_table_separator = "__"
```

**Credentials:** provision the `factory_raw` ClickHouse database and destination credentials separately. The dlt destination needs the correct native and HTTP ports plus TLS settings for that endpoint; a single generic port is not sufficient configuration. Keep `.dlt/secrets.toml` outside Git or use dlt's environment configuration. This excerpt does not implement incremental polling or deletes. [Destination setup and dataset behavior](https://dlthub.com/docs/dlt-ecosystem/destinations/clickhouse)

## ClickHouse · Check facts instead of trusting keys

**Milestone M2. Requires the preceding load into `factory_raw`.** The first query should return two rows and two distinct business keys. The second should return no rows.

```sql
SELECT
    count() AS loaded_rows,
    uniqExact(line_id) AS unique_lines
FROM factory_raw.raw__order_lines;

SELECT line_id, count() AS copies
FROM factory_raw.raw__order_lines
GROUP BY line_id
HAVING copies > 1;
```

**When:** after loading or replaying a batch, verify logical uniqueness. ClickHouse primary keys do not enforce it for you. [MergeTree key behavior](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree)

## dbt · Turn source rows into a business model

**Milestone M3. Requires an initialized dbt project, a compatible `dbt-clickhouse` adapter, and a working profile targeting `factory_analytics`.** First declare the actual loaded table names in `models/sources.yml`:

```yaml
version: 2
sources:
  - name: factory
    schema: factory_raw
    tables:
      - name: orders
        identifier: raw__orders
      - name: order_lines
        identifier: raw__order_lines
```

**File: `models/fct_order_line.sql`.** For this small first model, source references are direct; later lessons introduce staging models. It deliberately preserves **one row per shipped order line**.

```sql
{{ config(materialized='table', order_by='line_id') }}

SELECT
    l.line_id,
    l.product_id,
    toDate(o.ordered_at) AS sales_date,
    l.quantity * l.unit_price - l.line_discount AS net_sales
FROM {{ source('factory', 'order_lines') }} AS l
JOIN {{ source('factory', 'orders') }} AS o
    ON l.order_id = o.order_id
WHERE o.status = 'shipped'
```

**File: `models/mart_daily_sales.sql`.** Aggregate the fact only after establishing its grain.

```sql
{{ config(materialized='table', order_by='sales_date') }}

SELECT sales_date, sum(net_sales) AS net_sales
FROM {{ ref('fct_order_line') }}
GROUP BY sales_date
```

**File: `models/schema.yml`.** A duplicate key should fail a test rather than quietly inflate a chart.

```yaml
version: 2
models:
  - name: fct_order_line
    columns:
      - name: line_id
        data_tests:
          - unique
          - not_null
  - name: mart_daily_sales
    columns:
      - name: sales_date
        data_tests:
          - unique
          - not_null
```

Run `dbt debug`, then `dbt build`. Expected fixture result: one daily row for 2026-01-05 with net sales of 45.00. Rebuilding a table is sufficient at this scale; incremental materializations arrive only after comparison with a correct full rebuild. [ClickHouse adapter](https://clickhouse.com/docs/integrations/dbt) · [dbt data tests](https://docs.getdbt.com/docs/build/data-tests)

## Dagster · Put a dependency between the two jobs

**Milestone M6. File: `orchestration/definitions.py`. Requires Dagster, the preceding ingestion script, and a configured dbt project in `warehouse/`. Start commands from the project root.** This minimal bridge uses existing CLI entry points so the dependency is easy to see; the later milestone replaces coarse CLI assets with the dlt/dbt integrations for richer lineage.

```python
import subprocess
import sys
from dagster import Definitions, ScheduleDefinition, asset, define_asset_job

@asset
def raw_factory():
    subprocess.run([sys.executable, "ingestion/load.py"], check=True)

@asset(deps=[raw_factory])
def factory_marts():
    subprocess.run(["dbt", "build"], cwd="warehouse", check=True)

hourly_factory = define_asset_job(
    "hourly_factory", selection=["raw_factory", "factory_marts"]
)
defs = Definitions(
    assets=[raw_factory, factory_marts],
    jobs=[hourly_factory],
    schedules=[ScheduleDefinition(
        job=hourly_factory,
        cron_schedule="0 * * * *",
        execution_timezone="UTC",
    )],
)
```

**Boundary:** a schedule needs a running Dagster daemon and must be enabled. `dbt build` returns an error when required tests fail, but this excerpt does not implement candidate-mart promotion or protect a previously published release. Those are explicit deployment tasks. [Dagster integrations and richer lineage](https://docs.dagster.io/integrations/libraries/dbt)

## Shared query · Keep credentials on the server

**Milestone M7. File: `analytics.py`. Requires `clickhouse-connect`, the built daily mart, a TLS-enabled ClickHouse HTTP endpoint, and a read-only account.** Set `CLICKHOUSE_HOST`, `CLICKHOUSE_HTTPS_PORT`, `CLICKHOUSE_READ_USER`, and `CLICKHOUSE_READ_PASSWORD` outside the code. This example requires TLS; local non-TLS development needs deliberately different configuration.

```python
import os
import clickhouse_connect

def fetch_daily_sales():
    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.environ["CLICKHOUSE_HTTPS_PORT"]),
        username=os.environ["CLICKHOUSE_READ_USER"],
        password=os.environ["CLICKHOUSE_READ_PASSWORD"],
        secure=True,
    )
    try:
        return client.query(
            "SELECT sales_date, net_sales "
            "FROM factory_analytics.mart_daily_sales "
            "ORDER BY sales_date DESC LIMIT 30"
        ).result_rows
    finally:
        client.close()
```

**When:** both UIs should read the same modeled metric. Do not copy warehouse credentials into browser code. This fixed query has no user-supplied SQL; when filters arrive, bind parameters rather than interpolating input.

## Streamlit · Show the validated metric

**Milestone M7. File: `streamlit_app.py`. Requires Streamlit and `analytics.py` on the Python import path.** Run `streamlit run streamlit_app.py` in the configured server environment.

```python
import streamlit as st
from analytics import fetch_daily_sales

st.title("Ice cream factory · Daily sales")
st.caption("Synthetic tutorial data · USD · excludes taxes and returns")

@st.cache_data(ttl=60)
def load_sales():
    return [
        {"date": str(day), "net_sales_usd": float(amount)}
        for day, amount in fetch_daily_sales()
    ]

try:
    rows = load_sales()
    if rows:
        st.dataframe(rows, hide_index=True)
    else:
        st.info("No sales rows are available for this dataset.")
except Exception:
    st.error("Sales are unavailable. Check the warehouse connection and retry.")
st.caption("Results may be cached for 60 seconds. Cache age is not source freshness.")
```

**Boundary:** conversion to float here is for display only; calculations remain decimal in SQL/Python. A production dashboard also needs server-side diagnostics and a genuine last-validated publication timestamp, not a fabricated “updated just now.” [Streamlit connection/caching guidance](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data)

## Reflex · Reuse the mart, not a second pipeline

**Milestone M7. Place in the main module of an initialized Reflex project.** Copy `analytics.py` into its import path and configure the same read-only environment variables. Start with `reflex run` from that project. This is a minimal synchronous read example; it is not a production load-management design.

```python
import logging
import reflex as rx
from analytics import fetch_daily_sales

class SalesState(rx.State):
    rows: list[dict[str, str]] = []
    error: str = ""

    @rx.event
    def refresh(self):
        self.error = ""
        try:
            self.rows = [
                {"date": str(day), "amount": f"${amount:.2f}"}
                for day, amount in fetch_daily_sales()
            ]
        except Exception:
            logging.exception("Factory sales query failed")
            self.rows = []
            self.error = "Sales unavailable. Check the connection and retry."

def sales_row(row):
    return rx.hstack(rx.text(row["date"]), rx.text(row["amount"]))

def index():
    return rx.vstack(
        rx.heading("Factory daily sales"),
        rx.text("Synthetic USD data; taxes and returns excluded."),
        rx.button("Load sales", on_click=SalesState.refresh),
        rx.text(SalesState.error, role="status"),
        rx.foreach(SalesState.rows, sales_row),
    )

app = rx.App()
app.add_page(index)
```

**When:** use Reflex for a more application-like stateful interaction. Both apps query the warehouse; neither launches dlt on page load. Self-hosting must account for the version's backend and WebSocket requirements. [Reflex self-hosting](https://reflex.dev/docs/hosting/self-hosting/)

## Monitoring · Test a freshness boundary

**Milestone M10. File: `freshness_check.py`. Runnable as-is with Python.** An hourly pipeline has a proposed 90-minute validated-publication target. Test the exact boundary and stale condition; do not infer event-time freshness from a successful historical backfill.

```python
from datetime import datetime, timedelta, timezone

now = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
limit = timedelta(minutes=90)

def is_stale(validated_at, observed_at):
    if validated_at.tzinfo is None or observed_at.tzinfo is None:
        raise ValueError("Use timezone-aware timestamps")
    age = observed_at - validated_at
    if age < timedelta(0):
        raise ValueError("Validation time cannot be in the future")
    return age > limit

assert not is_stale(now - timedelta(minutes=90), now)
assert is_stale(now - timedelta(minutes=91), now)
print("Freshness boundary checks passed")
```

**Deployment exercise:** run real checks outside the scheduler's own failure domain, send a test alert to a channel you receive, and restore a backup to an isolated target. These snippets do not provision services, implement alert delivery, or establish production reliability. [Dagster instance/run monitoring](https://docs.dagster.io/deployment/oss/oss-instance-configuration)
