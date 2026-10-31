# Lesson 2 Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a short Windows/WSL setup lesson with one uv locking workflow, real readiness checks, and a printable companion.

**Architecture:** Author static lesson/reference HTML using existing shared CSS, print/copy helpers, and quiz feedback. Keep OS installation instructions as explicitly labeled learner actions; browser code never claims to inspect the host. Integrate through existing template/Markdown sources and regenerate the guide.

**Tech Stack:** HTML, existing CSS/JavaScript, Python standard-library checks, unittest/Playwright for authoring verification. No new runtime dependencies.

**Spec:** `docs/lesson-2-setup-design.md` (approved).

## Global Constraints
- Windows / WSL; at least 16 GB RAM reported; Docker not installed; budget deferred and no paid provisioning approved.
- WSL 2 + Ubuntu + Docker Desktop + uv only; do not teach competing locking recipes.
- Python 3.12 baseline, primary-source support checked; no full-stack compatibility claim.
- No automatic installation on the authoring host; no destructive environment/data removal or existing-project overwrite.
- Portable HTML, shared assets, offline/no-JavaScript reading, keyboard access, and print support.
- No learning record based on authored material or page visits.

## Review Focus
- PowerShell versus Ubuntu command confusion: every runnable shell block has an explicit terminal label and machine-readable terminal attribute; test both categories.
- Existing directories or a failed creation command: new-project block uses a guarded command chain; regression-test shell syntax and the existing-directory case without running installation commands.
- Client-only Docker success: distinguish `docker --version` from engine/server and disposable container checks; test required commands and troubleshooting copy.
- Misleading lock/isolation proof: run the Python check in a disposable standard-library venv, reject the unisolated interpreter, and explain lock limits/`--locked` failure instead of bypassing it.
- No-script and print regressions: exercise native answer disclosure, shared print state, bounded mobile widths, and one-page A4 companion output.

---

## Task 1: Build the self-contained setup lesson
**Files:** Create `lessons/0002-reproducible-local-setup.html`, `reference/local-setup-checklist.html`, `tests/test_setup_lesson.py`; update `RESOURCES.md`; capture source findings in `docs/lesson-2-setup-research.md`.
**Interfaces:** Reuse `form[data-quiz]`, `data-correct`, radio `data-feedback`, `data-quiz-controls`, `data-quiz-feedback` from `assets/lesson.js`; use existing `data-print`, code copy, and `details` print handling from `assets/course.js`. Python example is extracted from `#environment-check code.language-python` and saved as `check_environment.py` by the learner.
- [x] Add tests for explicit terminal labels, supported-baseline/locking/readiness content, duplicate IDs/local links, all quiz feedback branches/equal-word options, and no-script reading.
- [x] Add tests that syntax-check Bash blocks, reject an existing lab directory before later commands run, execute the environment example in a temporary `.venv`, and reject an unisolated interpreter.
- [x] Run `python3 -m unittest discover -s tests -p test_setup_lesson.py -v`; observe failure because the new lesson/reference are missing.
- [x] Write cited HTML and compact reference using the existing visual language. Use a new Linux-home project, uv-managed Python, dlt core as the lock example, a nondestructive second-environment replay, explicit Windows/Ubuntu boundaries, Docker Desktop integration, smoke checks, stop/recovery guidance, retrieval, and an exit report.
- [x] Run focused tests; inspect desktop/mobile screenshots together and the companion's A4 output. Fix observed defects in one batch, then confirm once.

## Task 2: Integrate and verify the course
**Files:** Modify `assets/guide-template.html`, Lesson 1 footer, `SYLLABUS.md`, `README.md`, `NOTES.md`, `DESIGN.md`; regenerate `index.html` and `reference/glossary.html`; extend `tests/test_setup_lesson.py` with entry-point coverage.
**Interfaces:** Add a Lesson 2 link under the existing Lessons group; keep Guide and On this page structures unchanged. Primary resources receive new stable R-numbers; Markdown remains authoritative for generated pages.
- [x] Test direct guide navigation and the Lesson 1 → Lesson 2 link; expect failure before integration.
- [x] Add the links/documentation and current teaching state without changing the learner's practice script or inferring mastery.
- [x] Run builder, JS syntax checks, and `python3 -m unittest discover -s tests -v`; require all tests green.
- [x] Review against the approved design, record verification evidence and platform limits, and finish the task tracker.

## Execution / review ruling
No Git repository or subagent tool is available. Implement inline in this session, self-review, and make no Git commits or tool installations. Windows/WSL/Docker Desktop installation remains learner-verified. Plan self-review: both deliverables and all five review-focus cases have named checks above; no independent subsystem or new asset is necessary.
