# SDD ledger — plan: docs/superpowers/plans/2026-10-30-guide-navigation.md

Pre-flight: the generator supplies stable milestone/example/handbook IDs; template, outline, and anchor-opening helper must use those same IDs. No conflicts found.

Ruling: execute in the existing workspace without Git worktree/commit helper scripts — `git rev-parse --show-toplevel` confirms this is not a Git repository — no branch history or independent checkout is available; preserve unrelated files.

Task 1: complete. Four new browser tests failed on the missing navigation, then all 13 guide tests passed after template/generator/CSS/JS changes (`python3 -m unittest discover -s tests -p test_guide.py -v`). Builder and course.js syntax check passed. Baseline desktop screenshot inspected. Existing layout scan is degraded because optional parser modules are unavailable; use rendered-browser checks rather than treating empty detector output as clearance.

Task 2: complete. Builder, both JavaScript syntax checks, and all 25 tests passed (`python3 -m unittest discover -s tests -v`). Desktop/mobile screenshots were inspected in one batch and one confirmation batch. Collapsed/expanded content has no page overflow at 320, 390, 768, 1024, 1199, 1200, 1440, and 1920px; no browser script errors observed.

Verification fix: the first rail-height calculation omitted the initial header/inset and placed its bottom at 1074.5px in a 1000px viewport. Strengthened the browser regression test, watched it fail, and reserved 10rem rather than 4rem in the shared rail max-height. The test now passes; manual checks confirm viewport-contained rails at heights 600/844/1000px and sticky positioning after body scrolling. Full suite green after the fix.

Final review: self-review (no subagent tool). Template/build IDs and escaping, disclosure navigation, breakpoint behavior, keyboard/DOM order and skip link, print visibility/state restoration, offline/no-script use, shared lesson compatibility, and documentation were checked against the approved design. No unresolved critical/important findings or deferred minors. The detector remains degraded; this is not an accessibility certification or cross-browser clearance. No Git helper scratch directory was created or deleted.
