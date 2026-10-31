# From Factory Transactions to a Trustworthy Data Warehouse

## A milestone-based data engineering syllabus

**Visual edition:** [Open the HTML study guide](index.html) · [Lesson 1: from one order to an insight](lessons/0001-from-order-to-insight.html) · [Lesson 2: local setup](lessons/0002-reproducible-local-setup.html) · [Annotated code examples](CODE-EXAMPLES.md) · [Printable glossary](reference/glossary.html)

**Project:** Ice Cream Factory Analytics  
**Goal:** job-ready fundamentals in warehouse and pipeline architecture  
**Starting point:** basic Python and SQL  
**Pace:** 20 weeks × 6–8 hours = approximately **120–160 hours**  
**Stack:** Python · dlt · MySQL · ClickHouse · dbt · Dagster · Streamlit · Reflex

This is a proposed learning path, not a promise of mastery or employment in 20 weeks. Advance when you can pass the milestone independently, not merely when you finish watching or copying. Repeat a week when necessary.

**Navigation:** [Mission](MISSION.md) · [Definitions](#fundamental-definitions) · [Tool decisions](#what-each-tool-does-and-when-to-use-it) · [Milestones](#milestone-map) · [Weekly plan](#weekly-plan) · [Assessment](#final-assessment) · [Primary sources](RESOURCES.md)

---

## 1. What you will be able to do

1. Explain OLTP versus OLAP, ETL versus ELT, and batch versus streaming using business requirements rather than tool names.
2. Design a warehouse around explicit fact-table grains and consistent dimensions.
3. Extract MySQL data with Python/dlt, load ClickHouse, and build tested dbt models.
4. Handle reruns, incremental state, changed records, soft deletes, late data, and backfills deliberately.
5. Orchestrate assets with Dagster and distinguish successful execution from correct, fresh data.
6. Build a Streamlit dashboard and a small Reflex application against the same trusted marts.
7. Package, deploy, monitor, troubleshoot, restore, and explain the resulting system.
8. Defend what you did **not** build: no streaming cluster or elaborate infrastructure without a requirement.

## 2. The business project

You are the data engineer for a fictional factory making vanilla, chocolate, and strawberry ice cream. Start with one factory and synthetic data; add a second factory only when practicing conformed dimensions and comparisons.

### Business questions

- Which products sell most, and what is their net shipped sales value?
- How much planned production becomes accepted finished product?
- Which products or lines have the highest waste rate?
- What was the end-of-day stock of each product at each factory?
- Can a manager trust these numbers, and how old is the underlying data?

### Small source schema

Build these progressively, not all in the first session:

| Source table | Meaning / intended row grain |
|---|---|
| `products` | One current product/SKU; includes pack size and flavor |
| `factories` | One factory |
| `production_lines` | One production line belonging to a factory |
| `orders` | One sales order header with status and business timestamps |
| `order_lines` | One product line within an order |
| `production_batches` | One batch on one line, with planned, actual, and accepted output in kg |
| `waste_events` | One recorded disposal event in kg, with reason and batch reference where known |
| `inventory_movements` | One signed finished-goods stock movement in kg, with product, factory, and event time |

Use stable source IDs, explicit units, UTC storage, a documented business-day timezone, and `updated_at` where records can change. Small reproducible fixtures establish expected answers; larger synthetic datasets are for experimentation, not proof of correctness.

### Metric contracts, before dashboards

| Metric | Initial project definition | Important limitation |
|---|---|---|
| Net shipped sales | Sum `quantity × unit_price − line_discount` for shipped order lines in one agreed currency | Excludes taxes, returns, credit notes, and formal revenue-recognition rules; label it accurately |
| Accepted output | Sum accepted batch output in kg | Do not mix kg, liters, and pack counts without an explicit conversion |
| Production yield | `sum(accepted_output_kg) / sum(actual_output_kg)` for completed batches | Weighted ratio, not an average of per-batch percentages; zero denominator produces null |
| Waste rate | `sum(waste_kg) / sum(actual_output_kg)` over the same factory/time scope | Disposal timing can differ from production timing; reconcile before interpreting |
| Closing stock | Opening balance plus signed movements through business-day end | Additive across products/factories at a fixed time, not across snapshot dates |

Keep waste categories and output definitions explicit so recorded waste is not counted twice. Production and sales are different processes: aggregate each to a compatible grain before comparing them. No invented profit, demand forecast, or OEE without the data those measures require.

## 3. Proposed architecture

```text
Python synthetic factory simulator
                 |
                 v
       MySQL operational tables
                 |
                 | dlt: extract + load; preserve incremental state
                 v
       ClickHouse raw/source tables
                 |
                 | dbt: staging -> dimensions/facts -> business marts
                 v
       ClickHouse tested analytical marts
              /                  \
             v                    v
      Streamlit dashboard    Small Reflex app

Dagster orchestrates ingestion -> transformations -> checks.
Apps refresh/query validated marts; they do not trigger ingestion on page load.
CI checks changes before deployment; monitoring observes both the data and services.
```

This is **batch ELT**. Start with manual full loads; introduce incremental loads and schedules only after you can reconcile a full load. The example business target later becomes an hourly refresh, not real-time streaming.

Logical raw/staging/mart layers can live in one ClickHouse instance. A warehouse is an analytical architecture and set of modeled data, not necessarily a separate database product for every layer.

## Fundamental definitions

Learn these through the project; do not memorize the entire table before starting. The modeling vocabulary follows [Kimball][r1][r2]; loading behavior follows [dlt][r8]; physical key behavior follows [ClickHouse][r9]. Operational targets below are course proposals, not universal standards. Local setup follows [Python environments][r3] and [uv project structure](https://docs.astral.sh/uv/guides/projects/).

| Term | Working definition / factory example |
|---|---|
| Virtual environment | An isolated Python environment for installed packages; this course uses uv-managed `.venv`, separate from system Python |
| Dependency lockfile | A tool-managed record of resolved dependencies used to recreate an environment; `uv.lock` is not the installed environment or a full-stack compatibility test |
| Data pipeline | Repeatable steps moving and processing data from a source to a useful destination |
| Data warehouse | Integrated, historically useful analytical data organized for answering business questions |
| OLTP | Transaction-oriented work: recording an order or stock movement in MySQL |
| OLAP | Analysis-oriented work: aggregating a year of sales by product in ClickHouse |
| ETL / ELT | Transform before loading / load before transforming; this course uses the latter |
| Batch / streaming | Process bounded groups periodically / process a continuing flow; latency requirements drive the choice |
| Raw / staging / mart | Source-oriented loaded data / cleaned and standardized models / business-ready models |
| Data mart | A focused analytical dataset for a subject or audience; can be a table or view within the warehouse, not the dashboard itself |
| Source / destination | The data read from / written to by a particular step; one step's destination can be another step's source |
| Grain | The precise meaning of one row; for example, one order line, not vaguely “sales data” |
| Fact / dimension | A measured business event or snapshot / descriptive context such as product or factory |
| Star schema | Fact tables connected to descriptive dimensions at explicitly declared grains |
| Conformed dimension | A consistently defined dimension shared across processes, such as product in sales and production |
| Natural / surrogate key | An identifier from the source / an identifier assigned for warehouse modeling |
| SCD type 1 / type 2 | Overwrite an attribute / preserve versions with validity periods; type 2 requires correct historical lookup |
| Transaction / snapshot fact | A row for an event / a row describing a state over a defined interval or at a defined time |
| Additive / semi-additive measure | Can be summed over relevant dimensions / cannot be summed over some dimension, such as inventory over time |
| Full / incremental load | Read all relevant source rows / read only a bounded set of new or changed rows |
| Cursor / watermark | Column used to select progress / saved progress boundary; this is not a guarantee that every change was observed |
| Append / merge / replace | Add rows / apply key-based changes / replace a selected destination scope; extraction and write mode are separate choices |
| Idempotency | Rerunning the same logical work does not duplicate facts or change the intended business answer |
| CDC | Change data capture: changes, including deletes when supported, obtained from a change mechanism such as a database log; timestamp polling is not log-based CDC |
| Event time / processing time | When a stock movement happened / when the pipeline handled it |
| Late-arriving data | A record arriving after its event-time period was already processed |
| Backfill | Controlled processing of a past interval, without unintentionally changing normal incremental progress |
| DAG / asset / materialization | A directed dependency graph / a meaningful data object / execution that produces or updates it |
| Data contract / data test | Agreed structure, semantics, and expectations / an executable check of those expectations |
| Lineage | Traceable dependencies from source columns and models to a reported number |
| Freshness / completeness | How recent relevant data is / whether the expected data is present; neither follows from a green run alone |
| SLI / SLO | Measured service indicator / chosen target for it, such as age of the latest validated mart |
| RPO / RTO | Maximum acceptable data loss interval / maximum acceptable recovery time; backups must be restore-tested |

**ClickHouse trap:** its primary key does not enforce uniqueness. A MySQL primary key, a dlt merge key, a dbt model's `unique_key`, and a ClickHouse sorting/primary key are not interchangeable guarantees. Test uniqueness explicitly. [R6][r6] [R9][r9] [R11][r11]

## What each tool does and when to use it

| Tool | Setup / first use | Use it when… | Do not confuse it with… |
|---|---|---|---|
| Python | Isolated environment, supported version, locked packages; run the simulator and a tested CLI | You need extraction glue, deterministic fixtures, validation, or automation | A reason to rewrite warehouse SQL transformations in Python |
| MySQL | Container, persistent volume, migrations, seed data, separate users | The source application needs relational transactions and constraints | A ban on analytics in MySQL; small reporting workloads may not need another system |
| dlt | SQL source + MySQL driver + ClickHouse destination; externalized secrets | You need repeatable Python-based extraction/loading with schema and state handling | Dagster scheduling, dbt modeling, or automatic capture of MySQL hard deletes |
| ClickHouse | Persistent service, scoped users, tested client connection | Analytical scans/aggregations justify a column-oriented engine | A drop-in OLTP replacement or uniqueness-enforcing relational store |
| dbt + `dbt-clickhouse` | Compatible adapter/core, profile, sources, `dbt debug`, first model | SQL transformations need dependencies, tests, documentation, and repeatable builds | A source extractor; adapter-specific behavior must be verified |
| Dagster | `dagster-dlt` / `dagster-dbt`, asset definitions, persistent instance later | Multiple dependent steps need scheduling, lineage, retries, and backfills | The transformation engine itself or a requirement for a single exploratory script |
| Streamlit | Read-only ClickHouse connection, secrets, cache policy | You need an internal analytical dashboard quickly in Python | A production ERP or an excuse to query source transactions from every chart |
| Reflex | Separate app environment if dependencies conflict; read-only server-side queries | You need a more application-like, stateful Python UI | A necessary extra pipeline stage or a reason to rebuild every dashboard feature |

**Architecture comparison:** the chosen milestone approach delivers one increasingly reliable system. Tool-by-tool study isolates APIs but delays integration; it was considered and not selected. A streaming-first build adds operational complexity before a demonstrated latency requirement, so it is deferred.

## 4. How each week works

A suggested **6-hour core**, with up to **2 optional hours**:

- **30 min:** closed-book recall from previous weeks.
- **60 min:** one concept and a targeted section of a primary source.
- **90 min:** coding along with a short guided lesson.
- **120 min:** independent variation and automated checks.
- **60 min:** troubleshoot, explain your decision, and commit a working checkpoint.
- **Optional 0–120 min:** deeper reading, larger data, or interview practice.

A guided lesson should take about 15–25 minutes and teach one thing; a week's coding-along consists of several small lessons rather than one huge HTML page. Future lessons live in `lessons/`, reusable components in `assets/`, and printable references in `reference/`. They are not pre-generated as part of this syllabus.

**Feedback loop:** predict the result → run the code → inspect the check → explain the difference → fix → rerun. After coding along, change the product, date, source update, or failure condition without copying the solution.

**Retention:** revisit an idea roughly 1, 7, and 21 days after learning it. Interleave practical tasks later: fix a duplicate, identify a grain error, and diagnose stale data in the same exercise. Future quizzes should balance answer length and vary correct-answer positions.

## Milestone map

| Milestone | Weeks | Demonstrable outcome |
|---|---|---|
| M1 — Factory foundation | 1–2 | Reproducible MySQL source, metric contracts, and an architecture sketch |
| M2 — First warehouse load | 3–4 | Reconciled dlt load into ClickHouse, safely rerunnable |
| M3 — Modeled warehouse | 5–6 | Tested dbt sales star schema and documented grain |
| M4 — Reliable changes | 7–8 | Incremental updates, soft deletes, late data, and a bounded backfill |
| M5 — Factory analytics | 9–10 | Tested production, waste, inventory, and sales marts |
| M6 — Orchestrated system | 11–12 | Dagster asset graph, schedule, retries, checks, and failure demonstration |
| M7 — Usable analytics | 13–14 | Streamlit dashboard and a small Reflex consumer using the same metrics |
| M8 — Release candidate | 15–16 | Measured query improvement, reproducible builds, and passing CI |
| M9 — Deployed portfolio | 17–18 | Securely scoped single-host deployment with durable state and tested restore |
| M10 — Operated portfolio | 19–20 | Alerts, recovery evidence, operational report, and interview demonstration |

## Weekly plan

### M1 · Weeks 1–2 · Understand the architecture and establish the source

**Week 1 — Requirements, definitions, setup**
- Learn: OLTP/OLAP, pipeline/warehouse/mart, batch/streaming, ETL/ELT, source versus destination.
- Setup: confirm OS, Docker availability, hardware, and budget; install Git, a supported Python, an isolated environment, and Docker Compose as needed. [Lesson 2: reproducible local setup](lessons/0002-reproducible-local-setup.html) teaches the selected Windows / WSL 2 + Ubuntu + Docker Desktop + uv workflow, with a Python 3.12 baseline and a [printable checklist](reference/local-setup-checklist.html).
- Diagnostic: write a small Python function, join two tables, aggregate by date, and explain how a one-to-many join changes row counts. Add only the refreshers the results justify.
- Code along: start MySQL, seed a tiny product/order dataset, and query a known total. Establish a tested version matrix for Python, dlt, dbt/adapter, Dagster/integrations, and clients; defer loading all services at once.
- When: start with business questions and latency requirements before choosing infrastructure.

**Week 2 — Source contracts and trustworthy fixtures**
- Learn: keys, constraints, transactions, joins, nulls, decimals, UTC versus business dates, units, and source change timestamps.
- Code along: add a seeded Python factory-data CLI, schema migration, `updated_at`, and source reconciliation SQL. Add production/inventory fixtures as their modules arrive.
- Independent task: add one order with multiple lines and prove a header/line join does not duplicate sales totals. Draw the source-to-dashboard architecture without notes.

**Pass M1:** a clean local environment can start the source and reproduce a hand-checked fixture total; secrets are ignored by Git; simulator output is repeatable; five metric contracts have explicit units/grains; version compatibility has a recorded smoke-test result, not just unconstrained package installs.

**Primary reading:** [Python environments][r3], [MySQL tutorial][r4], [Compose quickstart][r5], [Kimball modeling process][r1].

### M2 · Weeks 3–4 · Load your first analytical data

**Week 3 — ClickHouse and the first dlt pipeline**
- Learn: column-oriented analytical storage, MergeTree basics, extract/load stages, schema mapping, load metadata, and full-load write modes.
- Setup: ClickHouse with durable storage and scoped users; configure dlt SQL-source dependencies, the MySQL driver, and ClickHouse destination. Keep credentials outside code.
- Code along: load `products`, `orders`, and `order_lines` into raw/source tables; inspect types, timestamps, decimals, row counts, and load output.
- When: full loads are easiest to reason about for small datasets and the first correctness baseline.

**Week 4 — Reconciliation and safe reruns**
- Learn: extraction/write-mode separation, idempotency, partial failure, and the difference between load success and data correctness.
- Code along: build source-versus-raw checks for counts, key coverage, and shipped sales on the fixture; rerun the same full-load pipeline. Use a deliberate replace scope rather than blindly appending a complete extract.
- Independent task: insert a null or unexpected status, observe the failure, and fix the validation boundary. Do not accidentally truncate an unrelated table during a retry.

**Pass M2:** source and warehouse agree on the fixture; repeated runs do not double business totals; a failed connection yields an actionable error and a safe rerun; logical keys remain unique under the selected strategy.

**Primary reading:** [dlt ClickHouse destination][r6], [SQL source configuration][r7], [load modes][r8], [MergeTree][r9].

### M3 · Weeks 5–6 · Model the warehouse, not just copied tables

**Week 5 — Grain, facts, dimensions, dbt**
- Learn: star schema, natural/surrogate keys, conformed dimensions, additive measures, and transaction versus snapshot facts.
- Setup: compatible `dbt-clickhouse`, an isolated development target, sources, profile, and `dbt debug`.
- Code along: build staging models, `dim_product`, `dim_factory` where applicable, `dim_date`, and `fct_order_line`. Explicitly document that one fact row is one source order line.
- When: use dbt when transformations must be named, tested, documented, and built in dependency order.

**Week 6 — Marts, tests, and historical context**
- Code along: create `mart_daily_sales`, uniqueness/not-null/relationship/status tests, and a business-total reconciliation test. Use `dbt build` and generate documentation.
- Learn: type 1 versus type 2 history. Implement one tiny product-category history exercise with validity intervals and an as-of lookup; discuss when current-value reporting is enough. Keep transaction price on the fact rather than reusing today's product price.
- Independent task: introduce a duplicate dimension key and demonstrate why a join multiplies sales; then make the test catch it.

**Pass M3:** declared grain matches tested keys; dbt builds from raw data in a fresh development target; daily sales match the known fixture; historical category lookup returns one version, not multiple matches. Explain why inventory needs another fact grain.

**Primary reading:** [dimensional modeling][r1], [fact-table grains][r2], [ClickHouse/dbt adapter][r10], [dbt data tests][r11].

### M4 · Weeks 7–8 · Make changed data safe

**Week 7 — Incremental ingestion and destination behavior**
- Learn: `updated_at` cursor, saved state, overlap/lookback, key-based deduplication, update ordering, and soft versus hard deletes.
- Code along: move suitable tables from full extraction to incremental polling; choose and test a supported dlt/ClickHouse write strategy. Keep small reference tables full-loaded if that remains simpler.
- Update an old order, add a new one, repeat a boundary timestamp, and mark a row deleted. Make mart filtering of deletion markers explicit.
- When: incremental loading is justified when a full load costs too much time or source load; it is not automatically safer.

**Week 8 — Late events and isolated backfills**
- Code along: load a stock or waste event whose event date is yesterday but whose update timestamp is current. Recompute the affected business period. Run a bounded historical extraction without advancing or corrupting the regular cursor.
- Introduce an additive schema change; fail visibly on an incompatible type change instead of silently coercing important values.
- Compare dbt incremental materializations with small full rebuilds. Implement incremental transformation for one growing model only after its correctness can be compared with a full rebuild.

**Pass M4:** new, updated, repeated, soft-deleted, same-timestamp, and late records yield the expected current answer after reruns; the backfilled slice matches a full-rebuild baseline; ordinary incremental progress still works afterward.

**Important boundary:** timestamp polling does not discover physically deleted rows or changes with an unmodified/missed cursor. Document the remaining risk and alternatives: tombstones, periodic reconciliation/full refresh, or log-based CDC. Do not claim exactly-once delivery because one duplicate test passed.

**Primary reading:** [dlt incremental loading][r8], [bounded SQL loads][r7], [destination engines and write behavior][r6], [dbt/ClickHouse materializations][r10].

### M5 · Weeks 9–10 · Answer the factory's real questions

**Week 9 — Production, waste, and inventory facts**
- Learn: process-specific grains, weighted ratios, periodic snapshots, opening balances, business-day boundaries, and late corrections.
- Code along: add `fct_production_batch`, `fct_waste_event`, `fct_inventory_movement`, and `fct_daily_inventory` at product/factory/day grain. Reuse conformed dimensions.
- When: event facts answer “what happened”; inventory snapshots answer “what was the state at day end.”

**Week 10 — Business marts and quality gates**
- Build `mart_daily_production`, `mart_daily_waste`, and `mart_daily_inventory` alongside sales. Aggregate facts separately before cross-process comparisons.
- Add tests for units, invalid negative production, accepted output greater than actual output, missing dimensions, duplicate snapshots, zero denominators, and stock reconciliation. Negative stock is an explicit business rule decision, not automatically impossible.
- Independent task: seed a second factory, an inactive product/day, and an overnight movement. Explain which zero-activity rows the inventory report needs and how late data changes them.

**Pass M5:** all five business questions have documented SQL answers; weighted yield and waste rates match hand calculations; closing inventory reconciles to opening stock plus movements; no summing stock across dates or mixing kg with packs.

**Primary reading:** [Kimball techniques][r1], [transaction/snapshot grains][r2], [dbt tests][r11].

### M6 · Weeks 11–12 · Orchestrate dependencies and failures

**Week 11 — Dagster assets and lineage**
- Learn: asset versus task, dependency versus schedule, materialization metadata, retries, and lineage.
- Setup: Dagster, matching dlt/dbt integrations, local development UI, and explicit mappings from raw assets to dbt sources.
- Code along: expose ingestion and dbt builds as a connected asset graph; attach load counts, row counts, and check results. Keep extraction in dlt and business SQL in dbt.
- When: orchestration adds value when dependent work needs consistent execution and operational visibility, not because every script requires a scheduler.

**Week 12 — Scheduling, partitions, and recovery**
- Add an hourly schedule, bounded retry/backoff, concurrency limits around shared ingestion state, and observable failure handling.
- Partition a suitable derived daily mart; practice targeted recomputation without creating overlapping writers. Do not force one mutable shared dlt cursor into concurrent date backfills.
- Stop MySQL during ingestion; break a dbt test; simulate an unavailable destination. Recover deliberately and confirm the resulting business data.

**Pass M6:** lineage runs source → raw → mart; failed required checks prevent the downstream release/promotion step; scheduled runs work while the daemon is running; retries are bounded; recovery produces correct totals without duplicate facts.

**Primary reading:** [Dagster/dlt][r12], [Dagster/dbt][r13], [instance configuration][r15].

### M7 · Weeks 13–14 · Deliver useful applications

**Week 13 — Streamlit analytics dashboard**
- Learn: analytical UX, safe parameter binding, read-only credentials, caching, stale-data labeling, and empty/error states.
- Setup: Streamlit and a ClickHouse client/connection pattern supported by the locked dependencies.
- Code along: add date/factory/product filters, sales trend, output/yield/waste views, inventory view, and “data validated at” metadata. Use marts rather than untested raw tables.
- When: Streamlit is the shortest path to a usable internal Python analytics dashboard.

**Week 14 — Small Reflex manager view**
- Learn: UI state, server-side events/data access, loading/error handling, and how app deployment differs from pipeline execution.
- Setup: a small Reflex project; use its own environment if needed instead of forcing conflicting packages together.
- Code along: build one read-only production/waste explorer using the same mart definitions and filters as Streamlit. Do not duplicate the entire dashboard.
- Independent task: compare the two apps for the same scope; stop ClickHouse and verify helpful error states without leaking credentials or SQL internals.

**Pass M7:** both consumers agree with the SQL baseline; filters work; warehouse secrets never reach browser code; read-only users cannot write; cached results display honest freshness; charts/tables have clear units and usable labels. Confirm semantic equality, not pixel similarity.

**Primary reading:** [Streamlit connections][r16], [Reflex deployment model][r17]. Revisit the locked version's app APIs when writing each lesson.

### M8 · Weeks 15–16 · Improve performance and make releases repeatable

**Week 15 — Measure ClickHouse instead of guessing**
- Learn: sorting versus partitioning, sparse indexes, parts/merges, query plans, and resource trade-offs. Start without partitioning if the workload does not benefit from it.
- Code along: expand synthetic data to fit the machine, record a baseline query, inspect the plan and `system.query_log`, and test one sorting/model change.
- Compare rows/bytes read and query latency under recorded cache/concurrency conditions. Avoid universal millisecond promises based on a tiny warm-cache demo.
- When: optimize a measured bottleneck; materialized views and complex engines are optional comparison topics, not default requirements.

**Week 16 — Tests, CI, and release artifacts**
- Learn: unit versus integration versus end-to-end tests, isolated test databases, schema changes, locks, and rollback.
- Code along: CI runs Python checks, a tiny real MySQL→dlt→ClickHouse integration test, dbt build/tests, and an application query smoke test. Use synthetic credentials and scoped cleanup.
- Package deployable images, record compatible versions/image tags, and document one release command sequence plus a safe rollback/migration policy.

**Pass M8:** a clean checkout passes the small end-to-end test; an intentional SQL/test defect makes CI fail; a measured optimization preserves all business answers; secrets and production databases are not used by CI.

**Primary reading:** [MergeTree][r9], [query log][r18], [dbt tests][r11], [Compose][r5]. Consult the selected CI provider's official documentation when the provider is chosen.

### M9 · Weeks 17–18 · Deploy and restore the system

**Week 17 — Production-shaped single-host deployment**
- Learn: development versus deployment, network boundaries, TLS/authentication, health checks, persistent storage, scheduler uptime, and resource limits.
- Confirm a hosting budget and choose a VM or equivalent single-host environment. Run only the services the host can support; managed alternatives require a separate cost/security decision.
- Code along: deploy MySQL, ClickHouse, Dagster webserver/daemon/user code, and the two small apps. Choose a simple run-launching approach supported by the locked release rather than adding unnecessary dynamic container infrastructure.
- Persist Dagster metadata in a separate MySQL database/user through `dagster-mysql`; persist dlt state/working data and database volumes. MySQL source and metadata may share a server for this exercise, but that shares a failure domain.

**Week 18 — Access, release, backup, and restore**
- Keep databases private; protect Dagster and apps behind authenticated access and TLS or a private authenticated tunnel. Configure WebSocket proxying where required by the app versions.
- Store secrets outside images/Git; separate source, loader, transformer, dashboard, and metadata privileges. Test denied operations.
- Back up needed databases, orchestration metadata, configuration, and dlt recovery state. Restore to an isolated target and reconcile a known business day.
- Define a mart publication approach: failed validation must not advertise partial results as a fresh release. For the small course dataset, prefer rebuilding candidate marts, validating them, and explicitly promoting them over inventing a distributed transaction.

**Pass M9:** a host/service restart preserves data and execution history; an actual scheduled refresh runs; only intended entry points are reachable; authorized app access works; restored data matches expected counts/totals; last-validated data remains clearly identified when a candidate build fails.

**Deployment boundary:** this is a portfolio-grade single-host system, not high availability. Protect the administrative UI; backups on the same disk do not protect against losing that disk. MySQL metadata storage and the complete topology still need hands-on compatibility verification.

**Primary reading:** [Dagster Compose topology][r14], [MySQL instance storage][r15], [Reflex self-hosting][r17], [Streamlit connection/secrets guidance][r16]. Add current hosting, database-backup, and authentication primary sources before implementing this milestone.

### M10 · Weeks 19–20 · Monitor, recover, and defend the design

**Week 19 — Observe data and services**
- Learn: logs versus metrics versus checks, SLI/SLO, alert routing, runbooks, and why “the last job succeeded” is not enough.
- Instrument load progress, row counts, duration, retries/failures, source-to-mart reconciliation, freshness, volume anomalies, ClickHouse query cost, free disk, daemon health, and app availability.
- Add an alert destination you can actually receive. Use an independent host/service check so a dead Dagster daemon is not responsible for reporting its own death.
- Distinguish event-time lag from last successful validation. A quiet factory can have old events without a broken pipeline; use a source heartbeat or expected arrival schedule to interpret freshness.

**Week 20 — Failure drills and portfolio handover**
- Drill a stopped source, a missed schedule, a schema change, a duplicate update, a late event, and a controlled backup restore. Exercise low-disk handling in an isolated test or with safe thresholds, never by filling an important host disk.
- Track detection and recovery times. Reconcile the repaired day and document what data was lost, if any.
- Deliver a README, architecture diagram, model grains/metric dictionary, setup instructions, version matrix, CI evidence, deployment instructions, runbook, and a short narrated demo.
- Explain when MySQL alone would suffice, when CDC/streaming would be justified, when ClickHouse is a poor fit, and when you would remove Reflex or Dagster to simplify a smaller system.

**Pass M10:** a deliberately broken pipeline or freshness condition sends a received alert; a daemon outage is detected independently; another person can follow the runbook; a restored/replayed slice matches the baseline; you can explain the architecture without reading tool documentation.

**Primary reading:** [Dagster instance/run monitoring][r15], [ClickHouse query log][r18], [dlt state/load behavior][r8], and the selected deployment provider's official operations guides.

## 5. Monitoring contract and recovery targets

These are **proposed lab targets**, to test and revise against the host and fixture volume, not claims of achieved reliability:

| Signal | Proposed target / exercise | Response |
|---|---|---|
| Data freshness | Hourly runs; latest validated mart age ≤ 90 minutes during expected operation | Check source heartbeat → ingestion state → dbt/checks → release metadata |
| Execution failures | Alert after bounded retries are exhausted | Inspect the first failing stage; do not retry destructive operations blindly |
| Data correctness | Zero unexpected duplicate fact keys or reconciliation differences on the known fixture | Keep the failing candidate out of the validated release; inspect grain and changes |
| Volume/completeness | Compare with known fixture expectations first; add business-calendar thresholds later | Check missing source days, filters, partial loads, and legitimate quiet periods |
| Query performance | Record query, data size, cache state, p50/p95 timing, and rows/bytes read | Inspect query log/plan before changing keys or adding pre-aggregation |
| Service availability | Independent periodic check of app, daemon/heartbeat, and host health | Restore the failed component and verify actual data progress |
| Capacity | Alert at a documented safe disk/memory threshold before exhaustion | Stop unnecessary work, investigate growth, follow retention policy; do not delete warehouse files manually |
| Restore | Proposed RPO ≤ 24 hours and RTO ≤ 2 hours for the small demo | Test an off-host backup restore and replay; document observed results honestly |

A historical backfill completing now does not make today's data fresh. Display the processed coverage period, source event watermark, and last validated publication time as distinct values.

## 6. Portfolio artifacts and milestone assessment

The project grows toward this shape; **these application files are planned, not created yet**:

```text
project/
  simulator/             deterministic source data and changes
  ingestion/             dlt sources and pipelines
  warehouse/             dbt sources, staging, dimensions, facts, marts, tests
  orchestration/         Dagster assets, schedules, checks, configuration
  apps/streamlit/        primary dashboard
  apps/reflex/           small alternate consumer
  tests/                 fixtures, unit and integration checks
  deploy/                Compose, images, environment template, access configuration
  docs/                  architecture, metric dictionary, decisions, runbooks
  .github/workflows/     CI if GitHub is the selected host
```

At **every milestone**, demonstrate four things:

1. **Build:** run it from the documented checkpoint.
2. **Verify:** pass the specified checks on deterministic data.
3. **Break and repair:** reproduce a relevant failure safely, then restore correctness.
4. **Explain:** give a two-minute account of the design, its alternative, and its limitations.

Keep a small set of expected fixture answers in version control. Screenshots and green job badges do not substitute for reconciled results.

## Final assessment

### Practical examination

Without copying the guided solution:

1. Add a new flavor/SKU and a production batch.
2. Update yesterday's order and add a late inventory movement.
3. Run ingestion and recompute the affected models.
4. Show the same corrected numbers in SQL, Streamlit, and Reflex.
5. Fail a required data check and show that the candidate is not presented as validated.
6. Diagnose and recover a stopped service, then rerun without duplicates.
7. Restore a small backup to an isolated target and prove one day's metrics match.

### Interview explanation

Present the business requirement, source schema, fact grains, data flow, incremental strategy, failure handling, deployment boundary, performance evidence, and one deliberate simplification. Then answer: **“What would need to change if we required five-second freshness or ten times the data?”** Discuss evidence and trade-offs; do not reflexively add Kafka, Kubernetes, or more services.

### Completion rule

All milestone checks pass, a clean setup is reproducible, recovery is demonstrated, and you can independently explain and modify the system. This establishes a strong practical foundation; deeper mastery comes from maintaining real systems and encountering new workloads.

## 7. Wisdom: get one small design reviewed

After M3, ask an experienced practitioner to review a fact-table grain and its tests. After M10, request critique of the architecture or recovery runbook. Optional official communities are listed in [RESOURCES.md](RESOURCES.md#wisdom-communities). Share synthetic data and a minimal example, never credentials or private business records. Community participation is optional.

## 8. Deliberate scope limits and open decisions

**Deferred, not required for this first course:** Kafka, Spark, Kubernetes, Airflow, a data lake/lakehouse, log-based CDC implementation, multi-region replication, machine learning forecasting, a full factory ERP, and a second feature-complete frontend. Learn what problems they solve, but do not build them without a requirement.

**Setup established:** Windows / WSL, at least 16 GB RAM reported, Docker not installed; selected uv for Python environments and dependency locking. **Still to verify:** exact Windows build/architecture, virtualization, available memory/disk, Docker Desktop eligibility and installation, deployment provider/budget, DLT naming, and the full installed version matrix. Confirm metric definitions before treating reports as business truth. The fixture and lesson self-checks run on the authoring host; the learner's Windows setup, full package integrations, databases, and deployment have not been verified.

**Start learning:** [Lesson 1: from one order to an insight](lessons/0001-from-order-to-insight.html) covers the architectural vocabulary with a visual path, Python example, and retrieval practice. Share your exit explanation with the teaching agent before moving to environment setup. Ask follow-up questions whenever terminology or a design decision is unclear.

[r1]: https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/
[r2]: https://www.kimballgroup.com/2008/11/fact-tables/
[r3]: https://docs.python.org/3/tutorial/venv.html
[r4]: https://dev.mysql.com/doc/refman/8.4/en/tutorial.html
[r5]: https://docs.docker.com/compose/gettingstarted/
[r6]: https://dlthub.com/docs/dlt-ecosystem/destinations/clickhouse
[r7]: https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database/advanced
[r8]: https://dlthub.com/docs/general-usage/incremental-loading
[r9]: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree
[r10]: https://clickhouse.com/docs/integrations/dbt
[r11]: https://docs.getdbt.com/docs/build/data-tests
[r12]: https://docs.dagster.io/integrations/libraries/dlt
[r13]: https://docs.dagster.io/integrations/libraries/dbt
[r14]: https://docs.dagster.io/deployment/oss/deployment-options/docker
[r15]: https://docs.dagster.io/deployment/oss/oss-instance-configuration
[r16]: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
[r17]: https://reflex.dev/docs/hosting/self-hosting/
[r18]: https://clickhouse.com/docs/operations/system-tables/query_log
