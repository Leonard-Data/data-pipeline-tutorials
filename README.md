# Factory Data Lab

A portable, milestone-based study guide for data warehouse and pipeline architecture, centered on an ice cream factory analytics project.

## Open the guide

Open **[index.html](index.html)** directly in a modern browser. No server, account, CDN, or application installation is required. Keep `assets/` and `reference/` beside it; this is a portable folder, not a single bundled file.

The guide includes two-level **Guide / Lessons** navigation on the left and a separate **On this page** outline on the right, linking directly to milestones, examples, and reference groups. Both rails stay available while scrolling on wide screens; below 1200px, navigation moves above the content and the longer outline starts collapsed. It also includes an expandable architecture map, all 20 weeks, ten milestone gates, a synthetic rerun experiment, annotated examples, a grain self-check, and a printable glossary. Its content works offline; external documentation links need internet. Clipboard restrictions on local files fall back to selecting the code. Use **Print guide** or your browser's Print command; collapsed sections are expanded for printing.

## Start lesson 1

Open **[From one order to an insight](lessons/0001-from-order-to-insight.html)**. In about 20 minutes, trace an order through OLTP/OLAP, a pipeline, a warehouse, and a mart; compare ETL/ELT and batch/streaming. It includes a delivery-timing model, runnable standard-library Python, six instant-feedback questions, and a [one-page reference](reference/architecture-first-steps.html).

The lesson needs no database setup and does not run a real data service. Share your final architecture explanation with the teaching agent for feedback; opening a page does not establish learning.

## Continue with lesson 2

Open **[A workspace you can rebuild](lessons/0002-reproducible-local-setup.html)**. It targets the confirmed **Windows / WSL, 16+ GB RAM** starting point, with Docker not installed and spending deferred. Allow 20–30 minutes of active work plus downloads/reboots. Check OS/build, architecture, virtualization, memory, disk, permissions, and Desktop licensing; then use **WSL 2 + Ubuntu + Docker Desktop + uv** as the single setup workflow.

The lesson covers Git, managed Python 3.12, project isolation, a real `uv.lock` using dlt core, nondestructive replay into a second environment, Compose availability, and a disposable container check. Four quizzes provide immediate feedback. Keep the **[one-page setup checklist](reference/local-setup-checklist.html)** beside your terminal.

Reading installs nothing. The authoring checks do not certify Windows installation, the target Python/dlt environment, or Docker execution. Send observed results and blockers to the teaching agent; no paid resources or full factory services are provisioned.

## Generate the deterministic source fixture

```sh
python3 simulator/fixture.py
```

This standard-library script prints JSON containing **3 products, 2 orders, and 3 order lines**, with fixed IDs and UTC timestamps. The expected shipped-sales total is **$45.00**; a cancelled order provides a filtering check. It does not install or write anything or connect to MySQL.

See [the fixture walkthrough](simulator/README.md) for source grains, exact money handling, and expected results. Run its focused tests without the browser dependencies:

```sh
python3 -m unittest discover -s tests -p test_fixture.py -v
```

## Course sources

- [SYLLABUS.md](SYLLABUS.md): authoritative 20-week curriculum.
- [CODE-EXAMPLES.md](CODE-EXAMPLES.md): example prerequisites, code, expected results, and limitations.
- [MISSION.md](MISSION.md): learner goal, starting point, and constraints.
- [RESOURCES.md](RESOURCES.md): annotated primary readings and optional communities.
- [reference/glossary.html](reference/glossary.html): printable definitions derived from the syllabus.

The complete factory application is **not implemented** here. The Python fixture and freshness example are executable standard-library self-checks; other snippets require the named services and configured packages. No service credentials belong in the browser or repository.

## Rebuild after editing

The build uses Python and `markdown-it-py` (already present in the authoring environment). If missing in your development environment, install it in an isolated Python environment. Browser readers need no Python packages.

```sh
python3 tools/build_guide.py
```

This regenerates `index.html` and `reference/glossary.html` from the Markdown and `assets/guide-template.html`; edit the sources rather than generated HTML. Lessons and their individual companion references are authored directly as HTML and are not overwritten by this builder. Shared styles and progressive interactions are in `assets/course.css` and `assets/course.js`; reusable lesson quizzes and delivery-timing controls are in `assets/lesson.js`.

## Check changes

Development tests require Python Playwright and its Chromium browser, already present in the authoring environment. If setting up a new test environment, install Playwright and run `python3 -m playwright install chromium` there.

```sh
python3 tools/build_guide.py
node --check assets/course.js
node --check assets/lesson.js
python3 -m unittest discover -s tests -v
```

Tests use a real headless browser for two-level navigation, right-hand outline targets, keyboard/deep-link disclosure, bounded sticky rails, mobile navigation, duplicate/rerun behavior, quiz feedback, clipboard denial, overflow, print state, and no-JavaScript reading. They also parse Python snippets and execute the standard-library fixture, freshness check, first-lesson ETL/ELT model, and setup isolation example in disposable virtual environments. Setup tests exercise guarded new-project creation against existing folders and unsafe environment-path overrides; installation blocks are syntax-checked, not executed. Lesson checks cover all quiz answer branches, changing an answer, timing/reset behavior, cross-file anchors, scriptless reading, and one-page A4 printing of both companion references. They do **not** integration-test MySQL, ClickHouse, dlt, dbt, Dagster, Streamlit, or Reflex.
