# Data Warehouse and Pipeline Architecture Resources

Sources consulted while preparing the syllabus. Documentation is live: recheck APIs, supported versions, and examples when creating each lab. Reading a page does not establish that a particular package combination runs successfully.

## Knowledge

### Architecture and modeling
- **[R1] [Kimball Group: dimensional modeling techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)**
  Primary practitioner reference for business processes, grain, dimensions, facts, conformed dimensions, and slowly changing dimensions. Use for architecture and warehouse-modeling decisions.
- **[R2] [Kimball Group: fact tables](https://www.kimballgroup.com/2008/11/fact-tables/)**
  Explains transaction, periodic snapshot, and accumulating snapshot grains. Use before modeling sales, batches, or inventory, particularly to avoid mixing measurement grains.

### First lesson: architectural vocabulary
- **[R19] [Microsoft Architecture Center: online analytical processing](https://learn.microsoft.com/en-us/azure/architecture/data-guide/relational-data/online-analytical-processing)**
  Primary reading for lesson 1: read the introduction contrasting transactional work with analytical queries. Use for OLTP/OLAP workload classification; Azure products and cube implementation details are not prerequisites.
- **[R20] [AWS: what is a data pipeline?](https://aws.amazon.com/what-is/data-pipeline/)**
  Definitions of pipeline stages, sources, and destinations. Use to separate the movement/processing workflow from the stores that it reads and writes.
- **[R21] [AWS: what is a data mart?](https://aws.amazon.com/what-is/data-mart/)**
  Distinguishes subject-focused marts from broader warehouses and describes dependent/independent marts. Use for the sales mart example; a mart need not be a separate database server or a dashboard.
- **[R22] [AWS: ETL versus ELT](https://aws.amazon.com/compare/the-difference-between-etl-and-elt/)**
  Use the order and transform-location comparison: transform before versus after loading the analytical destination. Do not generalize the vendor page's performance claims into a rule that one pattern is always faster or better.
- **[R23] [Apache Beam: basics of the Beam model](https://beam.apache.org/documentation/basics/)**
  Read only the PCollection subsection on bounded versus unbounded data. Use to ground batch/streaming definitions; Beam, runners, windows, and distributed processing are not installed or taught in lesson 1.

### Foundations and local setup
- **[R3] [Python: virtual environments and packages](https://docs.python.org/3/tutorial/venv.html)**
  Official environment-isolation reference. Use for reproducible local setup; select the Python version supported by the actual adapter/integration set rather than assuming the documentation's newest Python is compatible.
- **[R4] [MySQL 8.4 tutorial](https://dev.mysql.com/doc/refman/8.4/en/tutorial.html)**
  Official source for relational-table creation and SQL practice. Use for source schema, inserts, joins, and baseline reconciliation queries.
- **[R5] [Docker Compose quickstart](https://docs.docker.com/compose/gettingstarted/)**
  Official multi-service local setup guide. Use for service names, networks, configuration, and lifecycle; deployment hardening requires additional work.

### Lesson 2: Windows / WSL setup
- **[R24] [Microsoft: install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)**
  Official PowerShell installation, restart/Ubuntu first-launch, and distribution-version checks. Use to distinguish the WSL software version from a distribution's WSL 1/2 mode.
- **[R25] [Docker Desktop: Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)**
  Live Windows-build, architecture, hardware, and installation requirements, plus Desktop subscription terms. Check eligibility before downloading; WSL support alone is insufficient.
- **[R26] [Docker Desktop: WSL backend and integration](https://docs.docker.com/desktop/features/wsl/)**
  Engine selection, Linux containers, and Ubuntu integration; warns against a second Engine installation in WSL. Its [WSL best practices](https://docs.docker.com/desktop/features/wsl/best-practices/) explain Linux-home project storage.
- **[R27] [Git: Linux installation](https://git-scm.com/install/linux)**
  Official Debian/Ubuntu package-manager route. Install Git in the development environment rather than silently mixing Windows and Linux toolchains.
- **[R28] [Python: version support status](https://devguide.python.org/versions/)**
  Maintenance phase and end-of-life dates. Python 3.12 was security-supported when lesson 2 was authored; recheck support and integration compatibility before a later upgrade.
- **[R29] [Astral uv: working on projects](https://docs.astral.sh/uv/guides/projects/)**
  Primary lesson 2 reading: distinguish project requirements, uv.lock, and .venv. Follow official [installation](https://docs.astral.sh/uv/getting-started/installation/), [managed Python](https://docs.astral.sh/uv/guides/install-python/), [locked sync](https://docs.astral.sh/uv/concepts/projects/sync/), and [environment-path](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path) references for the single selected workflow. Locking does not prove full-stack compatibility.
- **[R30] [dlt: installation and Python support](https://dlthub.com/docs/reference/installation)**
  Official runtime support and base-library installation. In lesson 2, dlt core demonstrates a real dependency lock; no SQL drivers or database integration are validated yet.
- **[R31] [Docker: Compose installation options](https://docs.docker.com/compose/install/)**
  Confirms Docker Desktop bundles Engine, CLI, and Compose. Use the Compose plugin; avoid adding a legacy standalone installation for this path.

### Ingestion and ClickHouse
- **[R6] [dlt: ClickHouse destination](https://dlthub.com/docs/dlt-ecosystem/destinations/clickhouse)**
  Official destination installation, write dispositions, engines, and deduplication behavior. Use before choosing merge or append behavior; destination support must be checked against the pinned versions.
- **[R7] [dlt: SQL database advanced usage](https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database/advanced)**
  Source configuration, incremental cursors, chunking, and bounded loads. Use for MySQL extraction and controlled backfills.
- **[R8] [dlt: incremental loading](https://dlthub.com/docs/general-usage/incremental-loading)**
  Official explanation of full loads, append, merge, and pipeline state. Use to distinguish reading changed rows from how those rows are written to the destination.
- **[R9] [ClickHouse: MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree)**
  Official explanation of parts, background merges, sorting keys, sparse indexes, and partitions. Explicitly notes that primary keys need not be unique. Use for correctness and query-performance experiments.

### dbt and Dagster
- **[R10] [ClickHouse: dbt integration](https://clickhouse.com/docs/integrations/dbt)**
  Official ClickHouse adapter and materialization overview. Use to select `dbt-clickhouse` and verify supported dbt versions/features; do not copy another warehouse's incremental SQL uncritically.
- **[R11] [dbt: data tests](https://docs.getdbt.com/docs/build/data-tests)**
  Official reference for generic and SQL data tests, including unique, not_null, accepted_values, and relationships. Use for schema expectations and business invariants.
- **[R12] [Dagster: dlt integration](https://docs.dagster.io/integrations/libraries/dlt)**
  Official integration documentation. Use to expose dlt ingestion through Dagster assets; follow the API style appropriate to the locked integration version.
- **[R13] [Dagster: dbt integration](https://docs.dagster.io/integrations/libraries/dbt)**
  Official model/asset integration, dependency, and execution reference. Use to connect transformations to ingestion without duplicating the SQL in Python.
- **[R14] [Dagster: Docker Compose deployment](https://docs.dagster.io/deployment/oss/deployment-options/docker)**
  Official deployment topology for webserver, daemon, and user code. Its example includes PostgreSQL; the course proposes MySQL metadata storage instead, so do not copy the example unchanged or its sample image tags as current recommendations.
- **[R15] [Dagster: instance configuration](https://docs.dagster.io/deployment/oss/oss-instance-configuration)**
  Official persistent storage, run monitoring, and retry configuration. Documents MySQL storage with `dagster-mysql`; use a separate metadata database and credentials.

### Applications and operations
- **[R16] [Streamlit: connecting to data](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data)**
  Official Python/database access, connection, secrets, and caching guidance. Use for a read-only dashboard and honest display of data freshness.
- **[R17] [Reflex: self-hosting](https://reflex.dev/docs/hosting/self-hosting/)**
  Official production hosting and frontend/backend connectivity guide. Use for app deployment, secrets, and WebSocket routing; topology is version-dependent.
- **[R18] [ClickHouse: system.query_log](https://clickhouse.com/docs/operations/system-tables/query_log)**
  Official query-log field reference. Use for measuring query duration, rows/bytes read, errors, and performance regressions; protect logs because queries may contain sensitive information.

## Wisdom (Communities)

Optional review opportunities, not required accounts or paid services:
- [dlt community](https://dlthub.com/community)
  Ask for feedback on a minimal reproducible ingestion/state problem after reproducing it locally. Linked by the official dlt documentation.
- [dbt community](https://www.getdbt.com/community)
  Seek review of a small grain/modeling decision and its tests; never post credentials or real customer data.
- [Dagster community](https://dagster.io/community)
  Ask practitioners to critique a small asset graph, scheduling decision, or recovery runbook rather than an entire unexplained repository.

## Gaps
- No combined version matrix has been installed or integration-tested. Establish and lock it in milestone 1.
- Windows / WSL and 16+ GB RAM are learner-reported; Docker is not installed. Exact build, architecture, virtualization, disk space, and installation results remain unverified. Budget is deferred. The proposed single-host deployment is a portfolio exercise, not a high-availability design.
- Recheck provider-specific TLS, authentication, backups, and alert-delivery documentation once hosting is selected.
- Community activity and suitability have not been independently assessed; joining is optional.
