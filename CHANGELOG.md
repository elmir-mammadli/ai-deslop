# Changelog

## 1.1.0 (2026-11-06)

- Copy tells C1 to C11: stock words, hype openers and closers, staccato headings, "not just X" contrasts, restated headings, template cards, Title Case, emoji, exclamation marks, em dashes and scattered bold, each with an exact action and keep rule.
- The honesty gate H1 to H6: unsourced numbers, invented proof, invented people, fake live signals, dead ends and leftover placeholders. Every link, button and form is clicked and the result recorded.
- `audit.py` scans visible text for the new tells: `stock-word`, `hype`, `staccato`, `dead-end` and `placeholder` are fix-level; `not-but`, `title-case`, `emoji`, `exclaim`, `em-dash`, `bold`, `stat`, `proof` and `fake-live` are check-level.
- `deslop-keep-start` and `deslop-keep-end` markers skip a whole block, such as a table of examples.
- The definition of done and the report format include copy, honesty and click-through evidence.

## 1.0.0 (2026-11-05)

First public release.

- The ai-deslop skill: rules for 20 tells with exact actions and keep cases, copy rewrites, a repair checklist, a verification protocol, a definition of done and a report format.
- `audit.py`: a dependency-free scanner for CSS, HTML, JSX/TSX, Vue, Svelte, Astro and data files, with fix and check tells, `--keep-caps`, `--only`, `--json` and `deslop-keep` markers.
- Claude Code plugin and marketplace manifests.
- Example pages and a documentation site.
