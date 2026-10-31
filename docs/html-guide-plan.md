# Portable HTML study guide

## Agreed scope
Turn the existing 20-week syllabus into a portable study guide opened directly from `index.html`, with a printable layout, clickable pipeline stages, all 20 weeks, copyable snippets, and short self-checks. Keep the Markdown syllabus authoritative and do not build or deploy the factory application.

## Approach
Use static HTML/CSS and a small shared script, not a framework or server. Generate the curriculum from `SYLLABUS.md` using the already-installed `markdown-it-py`; maintain annotated snippets in `CODE-EXAMPLES.md`. Share typography/print styles with a standalone glossary. No CDN or external font dependency.

## File responsibilities
- `assets/guide-template.html`: page composition, architecture, practice controls.
- `assets/course.css`: responsive reading, diagram, code, print styles.
- `assets/course.js`: copy buttons, rerun demonstration, quiz feedback.
- `CODE-EXAMPLES.md`: labeled prerequisite-aware Python/SQL/config examples.
- `tools/build_guide.py`: render Markdown, milestones, snippets, and glossary.
- `index.html`, `reference/glossary.html`: generated browser artifacts.
- `tests/test_guide.py`: real-browser interaction, narrow-screen, links, and snippet checks.

## Execution and checks
1. Write a browser test for the guide and rerun correctness; observe failure before building.
2. Build the static guide and reusable assets; keep all milestone outcomes and source readings.
3. Run the complete test suite, JS syntax and example checks; inspect desktop/mobile screenshots, fix in one batch, and confirm once.
4. Document how to open/rebuild the guide and what examples have not been integration-tested.

## Boundary risks
Clipboard access varies under file URLs: offer selectable code when copying is denied. No-JS readers must retain curriculum, examples, and architecture explanations. Print all collapsed milestone content. Example ingestion deliberately replaces only the named tutorial tables; no destructive command runs in the browser. Third-party stack examples remain illustrative until the actual lab environments are configured.
