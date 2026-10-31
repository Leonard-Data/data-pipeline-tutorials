# SDD ledger — plan: docs/superpowers/plans/2026-10-30-lesson-2-setup.md

Spec: docs/lesson-2-setup-design.md (learner approved).
Pre-flight: Task 1 produces the Lesson 2/reference paths; Task 2 consumes those exact paths in guide and Lesson 1 links. Existing shared quiz and print interfaces already match. No interface conflicts.

Ruling: execute inline and keep this repo-local ledger because there is no Git repository or subagent capability — avoid inventing branch/reviewer state — costs independent review and commit-based rollback.
Ruling: verify installation guidance from primary docs and limit execution to safe authoring checks — this Linux/Python 3.14.4 host has uv but no Python 3.12, PowerShell, or Docker — actual Windows/WSL installation and the target package/container smoke checks remain the learner's responsibility.

Task 1: complete. Seven tests first failed because Lesson 2 was absent. Built cited lesson/reference HTML, reused existing practice/copy/print components, and added a small reusable terminal-check table layout. Fixed test probes to inspect opened disclosures and select the specific creation block. The first A4 attempt was two pages; concise reference copy and proper table column widths now produce one A4 page without reducing shared type size.

Added an unsafe UV_PROJECT_ENVIRONMENT case, watched it fail, then guarded new-project creation before any writes. Fresh/existing directory and override cases now pass; standard-library example runs in disposable .venv/.venv-replay and rejects system Python. Bash blocks parse; all quiz choices, changed answers, no-script reading, copy denial, and print restoration are tested.

Verification: all 32 tests passed (`python3 -m unittest discover -s tests -v`); lesson/reference have no expanded page overflow at 320/390/768/1024/1440px; no browser script errors. Desktop/mobile/code/A4 screenshots were inspected in one batch and one confirmation batch; final print-flow height is 957px and the PDF is one page. Detector is degraded; surfaced em-dash advisories count CLI double-hyphen options and are not a reason to change valid commands. No accessibility certification is claimed.

Task 2: complete. The new guide-entry regression first failed with `0 != 1`; integrated Lesson 2 in the template, syllabus, README, and Lesson 1 footer. Added canonical virtual-environment/lockfile definitions, regenerated the guide/glossary, and updated teaching constraints/notes without creating a learning record.

Final verification: builder and both JavaScript syntax checks passed; all 33 tests passed (`python3 -m unittest discover -s tests -v`). A second builder run produced byte-identical generated pages and did not overwrite authored Lesson 2. No software installations or changes to practices/0001/load.py.

Final review: self-review (no subagent tool), recorded in docs/lesson-2-setup-review.md. Disposition: ship at the authored guide/lesson/checklist scope. No unresolved critical/important findings or deferred minors. The two execution/platform rulings above remain in force: no Git/independent review, and target Windows/Python 3.12/dlt/Docker checks remain learner-verified. No temporary Git helper workspace was created or deleted.
