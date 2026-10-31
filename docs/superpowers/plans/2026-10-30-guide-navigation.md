# Guide Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add approved two-level left navigation and a separate right-hand outline to the main guide.

**Architecture:** Preserve the static generator and reading content. Generate nested outline links alongside milestones/examples/reference groups, reuse the anchor-opening helper, and adapt the existing grid and native disclosure for different widths.

**Tech Stack:** Python, HTML, CSS, vanilla JavaScript, unittest and Playwright.

**Spec:** `docs/guide-navigation-design.md` (approved).

## Global Constraints
- No framework, CDN, dependencies, content rewrites, persistence, or automatic learning-completion tracking.
- Individual lesson pages stay unchanged; shared assets must retain their behavior.
- Preserve offline use, no-JavaScript reading, existing typography/colors, and keyboard focus.
- Print: omit both rails; preserve the existing expand/restore behavior for content disclosures.

## Review Focus
- Long outlines: bound scrolling to the rail without hiding later links.
- Narrow widths: put both navigation regions above the reading content without page overflow.
- Nested targets: open closed milestone/example/reference disclosures before scrolling.
- Direct hashes: retain working initial-load deep links.
- No JavaScript/printing: native navigation remains usable and neither rail appears on paper.

## Task 1: Build and test the navigation
**Files:** `tests/test_guide.py`, `tools/build_guide.py`, `assets/guide-template.html`, `assets/course.css`, `assets/course.js`, generated `index.html`.
**Interfaces:** Retain `build()` and `openTarget(id)`; add a `PAGE_CONTENTS` template slot and `.contents-outline` native disclosure. Derive nested targets from the existing milestone IDs, example IDs, and handbook group IDs.

- [x] Add failing browser tests for two-level guide groups, separate outline links, rail placement/stickiness, bounded scrolling, nested-target opening, deep links, and mobile/print/no-script behavior.
- [x] Run `python3 -m unittest discover -s tests -p test_guide.py -v`; confirm new assertions fail on the old layout.
- [x] Implement the template slot and generated section/child lists. Place both nav regions before `main` in DOM order and use explicit grid areas for left/center/right desktop placement.
- [x] Adapt CSS at 1200px: three columns above; navigation in document flow below. Keep existing pipeline/lesson/print rules. Use a matchMedia listener to open the outline on desktop and initially collapse it below 1200px, while preserving native no-script disclosure.
- [x] Regenerate and run guide tests; expect all passing.

## Task 2: Verify and document
**Files:** `README.md`, `DESIGN.md`, `.impeccable/review/navigation-*.png`.
**Interfaces:** Preserve all existing links and the generated glossary; no new service or package requirements.

- [x] Run the builder, both JavaScript syntax checks, and the complete unittest suite; expect exit zero.
- [x] Capture and inspect desktop/mobile together; verify intermediate widths, expanded content, keyboard links, rail scrolling, and print CSS. Fix evidenced issues once and confirm if necessary.
- [x] Document navigation layout, source ownership, breakpoint, and verification limits.

No Git repository is configured here; do not create a repository or make commits for this UI change.
