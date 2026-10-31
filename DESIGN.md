# Factory Data Lab visual system

## Reading surface
The HTML guide is a reference/workbook, not a marketing page. Keep definitions, code, primary readings, and acceptance gates easy to find. It is read on a normally lit desktop and on narrow browser screens; the surface uses white with dark ink rather than a dark application shell.

## Shared assets
- `assets/course.css` is the shared stylesheet for the guide, glossary, and future lessons.
- `assets/course.js` progressively enhances the guide and lessons with code copying, in-page disclosure, and printing; essential readings do not depend on JavaScript.
- `assets/lesson.js` enhances `form[data-quiz]` and `[data-delivery-lab]` components. Quizzes announce per-choice feedback without storing learner progress. Lesson and companion-reference layouts use the shared `lesson-shell` and `reference-sheet` classes. Lesson 2 adds no new scripts: it reuses these components for terminal-labeled setup blocks, four feedback quizzes, no-script answers, and nondestructive replay instructions. The reusable `terminal-checks` table class reserves readable terminal/command column widths; on narrow screens its focusable scroll region keeps overflow local.
- `assets/guide-template.html` defines the page composition; the generated HTML is not the editing source.

## Typography and color
Body text uses the local Georgia/Cambria serif stack; headings, navigation, controls, and tables use the system UI stack. Code uses a local monospace stack. No web fonts or CDN are required.

CSS tokens own the palette: white paper, `#202d32` ink, `#51646b` secondary text, `#006b60` interaction/diagram accent, `#f3f6f6` secondary surfaces, and `#993b30` error feedback. Code uses light text on `#172e36`. Explicit text labels accompany color-dependent states.

## Layout and interaction
The main guide uses three columns from 1200px: a two-level **Guide / Lessons** rail on the left, the reading column in the center, and a separate **On this page** outline on the right. Both rails are sticky with bounded vertical scrolling; their height reserves room for the header and initial reading inset. Below 1200px, both navigation regions return to document flow above the guide. The right-hand native disclosure initially collapses at those widths and can be opened without JavaScript. Desktop JavaScript opens it automatically and responds to breakpoint changes. Individual lesson layouts are unchanged.

The outline's milestone, example, and reference-group links are generated from the same IDs and labels used for their content. Nested links reuse the shared anchor-opening helper; no scrollspy or completion state is stored. The pipeline reads horizontally on wide screens and vertically below 1100px. Milestones and examples use native details/summary rather than a card grid. In-page milestone links open the destination before navigation.

Preserve keyboard focus, meaningful headings, semantic tables, reduced-motion support, and local rather than page-wide code overflow. Clipboard denial selects code and announces the alternative. The rerun and quiz controls appear only after their JavaScript is available. Do not save or imply learning completion automatically.

## Printing and verification
Printing opens all details and restores the reader's prior state afterward. Remove both navigation rails and interactive controls in print and keep code wrapping. The separate glossary is the short-print reference.

Desktop (1440px) and mobile (390px) captures were inspected in-thread; browser checks also covered 320, 768, and 1024px widths. Twenty-five fixture/course/lesson browser and example tests passed, including nested navigation, keyboard/deep-link opening, rail scrolling and viewport bounds, collapsed and expanded mobile content, print hiding, no-script reading, and a one-page A4 companion reference. Navigation overflow checks cover 320, 390, 768, 1024, 1199, 1200, 1440, and 1920px; rail bounds also cover viewport heights of 600, 844, and 1000px. Final guide desktop/mobile captures are `.impeccable/review/navigation-desktop.png` and `.impeccable/review/navigation-mobile.png`. Lesson desktop/mobile/reference captures are in `.impeccable/review/lesson-*.png`. The style detector was degraded because its optional parser packages were unavailable, so its empty output is not an accessibility certification. Checked palette contrast pairs exceed 4.5:1; no independent design reviewer was available. Full-stack snippet execution remains outside this UI verification.

Lesson 2 verification: all 33 fixture/guide/lesson tests passed after integration. Added coverage includes explicit PowerShell/Ubuntu labels, Bash syntax, safe new-directory/environment-override guards, the exact standard-library isolation script in two disposable environments, all four quiz branches, guide/previous-lesson entry points, scriptless reading, copy fallback, and one-page A4 checklist output. Lesson/reference expanded-content checks cover 320, 390, 768, 1024, and 1440px, with no script errors observed. Reviewed captures: `.impeccable/review/setup-desktop.png`, `setup-mobile.png`, `setup-mobile-code.png`, and `setup-reference-print.png`. Windows/WSL installation, the Python 3.12/dlt environment, and Docker Desktop/container execution require learner observations; the Linux authoring checks do not certify those steps.
