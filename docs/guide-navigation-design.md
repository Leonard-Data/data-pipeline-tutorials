# Guide navigation update

## Intent and scope
Make the long portable guide easier to navigate without changing its lessons, examples, or visual identity. Update the generated `index.html` through its template/build script and shared assets; individual lesson pages stay unchanged.

## Approaches
- **Keep both — selected by the learner:** retain left guide navigation, group it into two levels, and add a separate right-side section outline. This distinguishes course-level navigation from the current page.
- **Right-side contents only — not selected:** a wider reading area, but no separate course-level navigation.

## Proposed layout
- Left: `Guide contents`, with parent groups `Guide` and `Lessons`. The existing guide-section links sit beneath `Guide`; the existing first-lesson link sits beneath `Lessons`. Keep the glossary link and teaching note.
- Center: the existing guide content and interactions, unchanged.
- Right: `On this page`, with the main section links and nested links to the ten roadmap milestones, code examples, and reference groups. Generate these links from the same data that builds those sections so labels and targets do not drift.
- Wide desktop: three columns; both navigation rails remain accessible while scrolling. Long contents use a bounded, independently scrollable rail rather than disappearing below the viewport.
- Tablet/mobile: return navigation to document flow above the guide; use a native disclosure for the longer right-hand outline so it does not bury the first paragraph. Keep link targets keyboard accessible and do not create horizontal page overflow.
- Print: omit both rails; preserve the existing expand/restore behavior for content disclosures.

## Constraints and checks
No framework, CDN, dependencies, content rewrites, persistence, or automatic learning-completion tracking. Preserve offline use, no-JavaScript reading, existing typography/colors, and keyboard focus. Test nested targets opening their disclosures, deep links, responsive overflow, and printing; inspect desktop and mobile screenshots.

## Builder decisions
Use the existing grid, native lists/details, Markdown generator, and anchor-opening helper. No active-section tracking or extra navigation animation is needed for this request.
