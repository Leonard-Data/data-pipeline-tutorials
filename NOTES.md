# Teaching notes

## Confirmed by the learner
- Goal: become job-ready.
- Starting point: basic Python and SQL.
- Pace: 6–8 hours weekly.
- Structure: milestone-based rather than separate tool courses.
- Project: ice cream factory analytics.
- Include fundamental definitions, setup, how and when to use the tools, coding along, milestone checks, deployment, and monitoring.
- Wants HTML visualizations and code snippets; selected a portable study guide that opens directly without a server.
- Lesson 2 setup: Windows / WSL, Docker not installed, and at least 16 GB RAM (learner-reported). Exact Windows build, WSL status, CPU architecture, virtualization, and free disk space remain unverified.
- Spending budget: decide later. Do not provision paid resources; Docker Desktop licensing eligibility still needs checking for the actual use.
- Selected Lesson 2 workflow: WSL 2 + Ubuntu + Docker Desktop integration, with uv managing Python, the project environment, and uv.lock. Approved the setup lesson design.

## Instructor proposals / assumptions
- 20 weeks (120–160 hours), with ten acceptance-gated milestones; this is a learning plan, not a guarantee of mastery or employment.
- DLT means dlt (data load tool), not a different product with the same acronym.
- Batch-first architecture; start locally, then deploy a small single-host portfolio system.
- Streamlit is the main analytics dashboard; Reflex is a small alternative consumer, not a replacement warehouse or a second pipeline.
- Use MySQL as a separate logical Dagster metadata database via `dagster-mysql` if compatible with the locked versions; do not silently add PostgreSQL.
- No production infrastructure, package versions, cloud provider, or budget has been approved or validated. The authoring host is not evidence that the learner's Windows / WSL machine is configured.

## Current lesson and next session
Lesson 1 is available at lessons/0001-from-order-to-insight.html: OLTP/OLAP, pipeline/warehouse/mart, source/destination, ETL/ELT, and batch/streaming. It reuses assets/course.css and assets/course.js, with reusable quizzes and a delivery-timing model in assets/lesson.js. The printable companion is reference/architecture-first-steps.html.

The learner offered a sales-report freshness rationale; the assistant clarified that hourly requirements justify batch, while ELT describes transformation order. The learner has not yet demonstrated the complete architecture explanation, so do not record mastery merely from lesson coverage.

The learner then requested a small deterministic source fixture. `simulator/fixture.py` now emits fixed products/orders/order_lines as JSON without services or disk writes; `simulator/README.md` explains the three raw lines, cancelled control order, and $45.00 shipped-sales baseline. Five focused standard-library tests cover its data and reproducibility. An existing `practices/0001/load.py` contains the earlier in-memory ELT exercise and was left unchanged.

Lesson 2 is available at lessons/0002-reproducible-local-setup.html, with reference/local-setup-checklist.html. It teaches machine preflight, PowerShell/Ubuntu boundaries, Git, uv-managed Python 3.12, isolation, a dlt-core dependency lock, nondestructive replay, and Docker Desktop/Compose smoke checks. It reuses the existing shared scripts; reading does not run installations or inspect the host. The target Windows/WSL installation and Python 3.12/dlt/container commands still need learner-observed results; do not infer readiness from authoring tests on Linux / Python 3.14.

Next, ask for the Lesson 2 exit report, especially Windows build/architecture, virtualization, actual available RAM/disk, WSL mode, and tool/check results. Address blockers before any MySQL loader. Then have the learner run the fixture, explain why three raw lines yield two shipped lines, and inspect source grains. Deployment spending and the full version matrix remain unapproved/unverified; assess Python/SQL depth and the complete architecture explanation through their work, not lesson coverage.

## Teaching protocol
The visual course entry is index.html; rebuild it and reference/glossary.html with tools/build_guide.py from the Markdown sources and assets/guide-template.html. Annotated examples live in CODE-EXAMPLES.md. Each future lesson is one short HTML file in lessons/, using assets/course.css and reusable assets/ components. Reuse reference/glossary.html and the definitions in SYLLABUS.md consistently. Use primary-source readings, short recall questions, coding-along, an independent variation, immediate checks, and later retrieval practice. Record demonstrated understanding, not mere lesson completion.
