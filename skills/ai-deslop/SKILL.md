---
name: ai-deslop
description: Find and remove the visual and copy tells that make a website or UI look AI-generated ("AI slop"), and design new pages that never have them. Use when the user says de-slop, deslop, "remove AI slop", "looks AI-made", "looks generated", "make it look human-designed", "art-directed", or shares the 20 AI design slop indicators. Also use whenever building or reviewing a landing page, marketing site, portfolio, showroom or UI, so the result never needs de-slopping later.
---

# AI de-slop

Goal: a page that reads as designed by a person with a point of view. One typographic voice, real content where labels used to be, decoration only where it carries meaning. Removing tells is half the job; the other half is proving nothing broke where they used to be.

Work in this order and do not skip steps: **scope → audit → keep list → edit → repair → verify → report**. A pass is done only when every gate in "Definition of done" is met.

## 1. Scope

- List every site, page, shared component, data file and thumbnail in scope. The parent site counts, not only demos or subpages. If the user says "all", that means all; never stop at a subset and report it as done.
- Content lives in three places; audit all three: stylesheets, markup/components, and data files (arrays of titles, typography facts, nav labels, metadata).
- Ask once if scope is genuinely unclear. Otherwise proceed.

## 2. Audit with the script, then by eye

Run the bundled scanner first. It lists every candidate with file:line, grouped by tell, and exits 1 while fix-level tells remain.

```bash
python3 <skill-dir>/scripts/audit.py <paths...> --keep-caps ".wordmark,.logo,.heroTitle"
python3 <skill-dir>/scripts/audit.py src --only caps,tracking,period      # focus
python3 <skill-dir>/scripts/audit.py src --json > audit.json               # machine-readable
```

- `fix` tells must reach zero (or carry a reasoned `deslop-keep` marker). `check` tells (gradient, glow, counter-css, eyebrow, stripe, em-heading, shape) need a human verdict each, recorded in the report.
- The scanner skips comments and node_modules/build output. It cannot judge intent, find layout breakage, or see rendered text; that is what steps 5 and 6 are for.
- Extra searches the script does not cover are in `references/audit.md`.

## 3. The 20 tells: exact actions and keep rules

| # | Tell | Exact action | Keep only when |
|---|------|--------------|----------------|
| 1 | Tags and pills | radius 999px → 3 to 4px, or make the tag plain colored text | It carries state the reader acts on (urgency, status, active filter) |
| 2 | Excessive italics | delete `font-style: italic`, `italic` utilities, `<em>`/`<i>` used for flair | Real titles of works, a quoted foreign term, a wordmark |
| 3 | Default AI fonts | replace Instrument Serif, Instrument Sans, Geist, Geist Mono, Space Grotesk, IBM Plex Mono, JetBrains Mono, Space Mono when used as the voice of the page | Never as the voice; see font rules |
| 4 | Negative kerning | delete every negative `letter-spacing` and `tracking-[-…]`, `tracking-tight(er)` | Never |
| 5 | Over-detailed UI | delete gadgets: live status dots, fake trackers, cursor lenses, magnetic buttons, scroll-skew marquees, spinning counters, decorative level meters | The gadget is the product (calculator, planner, configurator) |
| 6 | Overusing dividers | keep at most one structural rule per list; delete rules that only separate | The rule groups rows in a table or list |
| 7 | Shades and opacities | solid color tokens; delete glows, blur, backdrop-filter, shadows over 40px blur | A scrim keeps text readable on a photo; a single subtle elevation on a real overlay (dialog, menu) |
| 8 | Bordered containers | unbox cards whose border only decorates; delete left accent stripes (border-left ≥ 3px) | The box is a real object (form, receipt, ticket, sheet, table), or the stripe signals status (form success/error) |
| 9 | Over-detailed diagrams | cut "Plate I", "Fig. 2", legends and labels that do not explain | Every element maps to something real |
| 10 | Verbose, redundant text | one disclosure line in the footer instead of repeated "sample" notes; cut sentences that restate the heading | The note adds information not stated elsewhere |
| 11 | Code breadcrumbs | delete `// LABEL`, `/services` link text, `[1]`, `EV-01`, `R-03`, `STATUS:`, `TEL/MAIL/AREA` caps labels | A real navigation breadcrumb ("Home / About") |
| 12 | Section numbering | delete "01 /", "§", "Chapter 1", roman numerals, "Z1", zero-padded counters in markup and in CSS `counter()` | Order is the content: instructions, timelines, form steps, quiz questions, numbers that match markers on a diagram. Then plain `1.` not `01` |
| 13 | Eyebrows | delete the small label above a heading; if it held facts (place, trade, price), move them into the heading or the first sentence | It is a functional label: form label, legend, `dt`, table head, footer column head |
| 14 | Dithering, noise | delete dither and noise textures | The texture is the art direction (risograph print, paper edge); mark it `deslop-keep` |
| 15 | ASCII images | delete | Never by default |
| 16 | Squircles | radius 12px and up → 4 to 6px (sections, cards, images, dialogs) | True circles (equal width and height: avatars, icon dots, round checks), deliberate shapes (arch windows, pipe ends) with `deslop-keep` |
| 17 | Mono fonts | replace with the site's text font plus `font-variant-numeric: tabular-nums` | Real code on the page |
| 18 | ALL CAPS subtitles | delete `text-transform: uppercase`, `uppercase` utilities, caps in source strings; also delete their positive letter-spacing | Wordmarks, real signage (DANGER / WARNING / NOTICE, pipe markers), and a brand built on condensed display headlines (keep those selectors on `--keep-caps`) |
| 19 | Gradient backgrounds | solid color | Data scales (temperature, seasons), photo scrims, hard-stop hairlines |
| 20 | Periods in titles | drop the final period of h1 to h3, page titles, card and data titles, display-size one-sentence footer lines | Body sentences, multi-sentence paragraphs, abbreviations ("Co.", "Inc.") |

Also remove: an accent-colored phrase inside a headline (same tell as #2), outlined or stroked giant wordmarks, decorative blobs and circles, empty frames and film strips.

## 4. Fonts

- Never ship a default-AI font (#3) as the voice. Pick for the subject, from what the page is about: signage trades get a highway or condensed face, heritage trades a Caslon or Didone, studios an editorial serif with a quiet sans.
- One display face plus one text face, or one family. No third family for labels.
- Numbers use `font-variant-numeric: tabular-nums` in the text face, never a mono.
- When swapping, also update: font imports, CSS variables, layout class lists, header comments that name fonts, and any data that displays font names (catalogue cards, style guides). Then re-check every headline whose width or line count depended on the old font.
- Do not load italic or unused weights after removing italics.

## 5. Copy rules

- Headings: no final period, no `<em>`, no accent span, sentence case.
- Rewrite staccato two-sentence headings into one natural sentence:
  - "Close the valve. Then call." → "Close the valve, then call"
  - "Find the leak. Plan the roof." → "Find the leak, then plan the roof"
  - "Fast, contained, explained." → "Fast, contained and explained"
  - "A professional website. A clear price." → "A professional website at a clear price"
  - "Seven layers. One you see." → "Seven layers, and you see one"
  - A question plus an instruction may stay as two parts: "Water off? Book a morning visit".
- When removing an eyebrow that carried a fact, the fact must survive somewhere visible.
- Follow the project's own style rules (spelling variant, banned words, dash style). Check spelling consistency after edits.
- Never invent proof: no fake reviews, counts, logos, awards. Label samples once, in the footer.

## 6. Edit

- Mechanical changes (caps, tracking, italics, radii, heading periods) by script; judgment calls (rewrites, gadgets, layouts) by hand.
- Edit CSS rule by rule with a small parser (match `selector { body }` blocks, change the body, write back). Never run one large backtracking regex over a whole stylesheet.
- Keep list first, edits second. Write down which selectors keep caps and which numbers stay, then pass that list to the script.
- Mark deliberate exceptions inline so future audits skip them: `/* deslop-keep: reason */` in CSS, `{/* deslop-keep: reason */}` in JSX, on the same or the previous line.

## 7. Repair what removal breaks

Every removal can leave a hole. Check each of these, for every site:

1. Grids with a small first column (`44px 1fr`, `80px 1fr 360px`, `90px 1fr 1.4fr`) that held a number or code: drop that column at every breakpoint.
2. Left margin or padding of 28 to 60px on `p`, `dd`, `h3`, `li` that aligned text past a removed number: set to 0.
3. Leftover `counter-reset` / `counter-increment`, `li > span` / `dt span` rules, `display: flex; gap` on headings that only spaced a number.
4. Dead classes no longer referenced in markup (skip dynamic ones such as `s[\`badge_${x}\`]`), empty rules, unused `index` params and props, unused imports and font variables, stale comments.
5. Headlines that overlapped an image or relied on a line count, after any font change.
6. Never strip borders inside `::before` / `::after` without reading the rule: a left plus bottom border rotated 45° is a drawn checkmark.

## 8. Verify

- Rendered check of every page at 1440 and 390 wide, with `prefers-reduced-motion: reduce` so animated sections render finished. Scroll the whole page before capturing so lazy images load; remove dev overlays. A blank image area is lazy loading or a stuck dev image optimizer until proven otherwise; compare with production before calling it a bug.
- Automated pass on every route at both widths: zero console errors, zero horizontal overflow (`scrollWidth > innerWidth`).
- Project checks: type check, lint (zero new warnings), the project's copy or banned-word check, production build.
- Re-run the audit script: `fix` total must be 0.
- Refresh thumbnails, previews and showroom images that show the old design, and re-check them.
- Restore files that builds or dev servers rewrite (for example `tsconfig.json`, `next-env.d.ts`) before committing.

## 9. Definition of done

All must be true:

- [ ] Every item in scope was audited (stylesheets, markup, data, thumbnails).
- [ ] `audit.py` reports `fix: 0`; every remaining `check` hit has a verdict.
- [ ] Every exception is on the keep list or carries a `deslop-keep` marker with a reason.
- [ ] Every page rendered and was looked at, at 1440 and 390.
- [ ] Zero console errors and zero horizontal overflow on every route.
- [ ] Type check, lint, copy check and production build pass.
- [ ] Previews and thumbnails refreshed.
- [ ] Nothing pushed or published without the user's go-ahead.

## 10. Report

End with a short report in this shape:

1. **Scope:** what was covered (count of sites and pages).
2. **Removed:** per tell, what changed and roughly how many instances.
3. **Kept on purpose:** each exception and its reason.
4. **Repaired:** layout breakage found and fixed.
5. **Verified:** each check and its result.
6. **Open items:** anything not done or not verified, stated plainly.

## Pitfalls seen in practice

- Disk fills fast with headless browser profiles. Capture one page at a time, delete each profile, watch free space. A full disk breaks the shell and the dev server.
- Do not kill the user's dev server. Start your own on another port and stop it when done.
- Matching on class names alone removes functional labels; match on position and element type.
- Data-driven titles and template-literal page titles are missed by a JSX-only heading scan; the script checks `title:`, `heading:` and `title=` too.
- A pass that skips the parent site, the data file, or the thumbnails is not done.

## Designing new work without the tells

Start from the subject, not a template: one display face and one text face chosen for the trade or audience, one accent color with a meaning, 0 to 6px corners, sentence-case labels, headings without periods, no eyebrows, no numbered sections unless order matters, real copy instead of placeholder labels, and every decorative element tied to something true about the business. Run `audit.py` before handing the work over.
