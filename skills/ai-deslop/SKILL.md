---
name: ai-deslop
description: Find and remove the visual and copy tells that make a website or UI look AI-generated ("AI slop"), block invented proof (fake stats, reviews, logos, dead links), and design new pages that never have them. Use when the user says de-slop, deslop, "remove AI slop", "looks AI-made", "looks generated", "make it look human-designed", "art-directed", or shares the 20 AI design slop indicators. Also use whenever building or reviewing a landing page, marketing site, portfolio, showroom or UI, so the result never needs de-slopping later.
---

# AI de-slop

Goal: a page that reads as designed by a person with a point of view. One typographic voice, real content where labels used to be, decoration only where it carries meaning. Removing tells is half the job; the other half is proving nothing broke where they used to be.

Work in this order and do not skip steps: **scope → audit → keep list → edit → repair → verify → report**. The visual tells (section 3), the copy tells (section 5) and the honesty gate (section 6) are all part of every pass. A pass is done only when every gate in "Definition of done" is met.

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

- `fix` tells must reach zero (or carry a reasoned `deslop-keep` marker). `check` tells need a human verdict each, recorded in the report: gradient, glow, counter-css, eyebrow, stripe, em-heading, shape, not-but, title-case, emoji, exclaim, em-dash, bold, and the honesty claims stat, proof and fake-live (these pass only with a source the user gave).
- The copy and honesty checks read visible text only: text nodes in markup and prose-like strings in data files. They cannot judge restated headings (C5) or template cards (C6); read those by eye.
- The scanner skips comments and node_modules/build output. It cannot judge intent, find layout breakage, or see rendered text; that is what the repair and verify steps are for.
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

## 5. Copy tells

Generated copy has its own tells, and they show up on the same pages as the visual ones. Read every heading, button, card and paragraph, not only the stylesheet. The script flags the ids in the second column.

| # | Tell | Script id | Exact action | Keep only when |
|---|------|-----------|--------------|----------------|
| C1 | Stock words: seamless, elevate, unlock, empower, leverage, cutting-edge, game-changer, revolutionize, next-gen, world-class, state-of-the-art, supercharge, unleash, transformative, holistic, unparalleled, delve, synergy; and vague fillers: countless, a wide range of, all your needs, one-stop shop, peace of mind, hassle-free, tailored to your needs | `stock-word` | Replace with the concrete thing: what is done, to what, how fast, for how much. "Seamless booking" → "Book online in two steps" | The word is literal for the trade (a locksmith unlocks, an elevator company elevates); mark it `deslop-keep` |
| C2 | Hype openers, reaction prompts, chatbot closers: "In today's fast-paced world", "Imagine a world where", "Say goodbye to", "Let that sink in", "Here's the thing", "The best part?", "Ready to take the next step?", "Why wait?", "Don't just take our word for it" | `hype` | Delete. Start with the fact, end on the action ("Book a visit") | Never |
| C3 | Staccato and triad headings: "Fast. Simple. Reliable.", "Design. Build. Launch.", "Close the valve. Then call." | `staccato` | One natural sentence (see the rewrites below) | A question plus an instruction: "Water off? Book a morning visit" |
| C4 | "Not just X, it's Y" and "not X, but Y" contrasts | `not-but` | State Y plainly | It corrects a real, common misunderstanding about the trade |
| C5 | A heading restated by the sentence under it | by eye | Cut the sentence, or make the heading the fact and the sentence the detail | Never |
| C6 | Template cards: every card the same sentence shape, length and verb | by eye | Write each card from its own fact; let lengths differ | A data table, where sameness is the point |
| C7 | Title Case In Headings, Buttons, Cards And Bullets | `title-case` | Sentence case | Proper nouns, product and place names, real titles of works |
| C8 | Emoji as bullets or in headings and buttons | `emoji` | Remove; use the list itself or a real icon with meaning | The product is about messaging or the brand voice is built on it |
| C9 | Exclamation marks in UI copy | `exclaim` | Period, or nothing | Quoted speech; one success message after a real action |
| C10 | Em dashes in copy | `em-dash` | Comma, colon, parentheses, or two sentences | The project's own style guide allows them |
| C11 | Bold sprinkled through body text | `bold` | Remove; at most one bold fact per section | A real warning or a price the reader must not miss |

Copy rules that always apply:

- Headings: no final period, no `<em>`, no accent span, sentence case.
- Rewrite staccato two-sentence headings into one natural sentence:
  - "Close the valve. Then call." → "Close the valve, then call"
  - "Find the leak. Plan the roof." → "Find the leak, then plan the roof"
  - "Fast, contained, explained." → "Fast, contained and explained"
  - "A professional website. A clear price." → "A professional website at a clear price"
  - "Seven layers. One you see." → "Seven layers, and you see one"
- Replace adjectives with facts the business can stand behind: a time, a price, an area, a step, a name. If no fact exists, cut the line rather than invent one (see the honesty gate).
- When removing an eyebrow that carried a fact, the fact must survive somewhere visible.
- Follow the project's own style rules (spelling variant, banned words, dash style). Check spelling consistency after edits.

## 6. Honesty gate

A page is not done while it claims something nobody can back up. These are hard failures: there is no style reason to keep any of them, only a real source. Ask the user for the source; if there is none, remove the claim.

| # | Claim | Script id | Exact action |
|---|-------|-----------|--------------|
| H1 | Numbers that need a source: "10,000+ customers", "99.9% uptime", "#1", "5-star rated", "4.9 rating", "20 years of experience", "since 1998" | `stat` | Keep only with a source the user gave; otherwise remove, or turn into a true process fact ("We reply the same day") |
| H2 | Proof: testimonials, reviews, star ratings, "Trusted by" and "As seen in" logo bars, awards, certifications, licenses, insurance, compliance (SOC 2, HIPAA, ISO 27001, PCI DSS, GDPR-compliant) | `proof` | Keep only what the user confirmed. Never write a testimonial, a reviewer name, an avatar or a logo the business did not supply |
| H3 | Invented people and history: team members, founders, quotes, addresses, license numbers, founding stories | by eye | Remove, or use an honest placeholder the user will replace ("Your photo here") on drafts only |
| H4 | Fake live signals and urgency: "3 people viewing", "Only 2 spots left", "Selling fast", countdown timers, "Available now" dots | `fake-live` | Remove unless a real data source drives it; then name that source in the report |
| H5 | Dead ends: `href="#"`, empty `href`, `javascript:` links, `onClick={() => {}}`, nav items pointing to sections or pages that do not exist, forms that submit nowhere | `dead-end` | Point it at something real (a section, a page, `tel:`, `mailto:`, a form handler) or remove the control |
| H6 | Placeholder left in: lorem ipsum, "Your Company", "Company Name", John or Jane Doe, TODO, TBD | `placeholder` | Replace with real content or remove the block |

Sample and concept work (demos, portfolios, pitches) may invent a business name and contact details only in reserved formats (555-01XX phone numbers, `.example` domains), with one disclosure line in the footer. It still never invents reviews, ratings, client logos, awards or counts.

Prove the gate, do not assert it: click every nav link, button and form at 1440 and 390, and record each result in the report ("Book a visit → /contact#form, form shows the success message"). An unrecorded control counts as unchecked.

## 7. Edit

- Mechanical changes (caps, tracking, italics, radii, heading periods) by script; judgment calls (rewrites, gadgets, layouts) by hand.
- Edit CSS rule by rule with a small parser (match `selector { body }` blocks, change the body, write back). Never run one large backtracking regex over a whole stylesheet.
- Keep list first, edits second. Write down which selectors keep caps and which numbers stay, then pass that list to the script.
- Mark deliberate exceptions inline so future audits skip them: `/* deslop-keep: reason */` in CSS, `{/* deslop-keep: reason */}` in JSX, on the same or the previous line. Wrap a whole block (a table that quotes the tells, a style guide page) in `deslop-keep-start: reason` and `deslop-keep-end`.

## 8. Repair what removal breaks

Every removal can leave a hole. Check each of these, for every site:

1. Grids with a small first column (`44px 1fr`, `80px 1fr 360px`, `90px 1fr 1.4fr`) that held a number or code: drop that column at every breakpoint.
2. Left margin or padding of 28 to 60px on `p`, `dd`, `h3`, `li` that aligned text past a removed number: set to 0.
3. Leftover `counter-reset` / `counter-increment`, `li > span` / `dt span` rules, `display: flex; gap` on headings that only spaced a number.
4. Dead classes no longer referenced in markup (skip dynamic ones such as `s[\`badge_${x}\`]`), empty rules, unused `index` params and props, unused imports and font variables, stale comments.
5. Headlines that overlapped an image or relied on a line count, after any font change.
6. Never strip borders inside `::before` / `::after` without reading the rule: a left plus bottom border rotated 45° is a drawn checkmark.

## 9. Verify

- Rendered check of every page at 1440 and 390 wide, with `prefers-reduced-motion: reduce` so animated sections render finished. Scroll the whole page before capturing so lazy images load; remove dev overlays. A blank image area is lazy loading or a stuck dev image optimizer until proven otherwise; compare with production before calling it a bug.
- Automated pass on every route at both widths: zero console errors, zero horizontal overflow (`scrollWidth > innerWidth`).
- Project checks: type check, lint (zero new warnings), the project's copy or banned-word check, production build.
- Re-run the audit script: `fix` total must be 0.
- Refresh thumbnails, previews and showroom images that show the old design, and re-check them.
- Restore files that builds or dev servers rewrite (for example `tsconfig.json`, `next-env.d.ts`) before committing.

## 10. Definition of done

All must be true:

- [ ] Every item in scope was audited (stylesheets, markup, data, thumbnails).
- [ ] `audit.py` reports `fix: 0`; every remaining `check` hit has a verdict.
- [ ] Every heading, button and card was read for copy tells (C1 to C11), including the ones the script cannot see (C5, C6).
- [ ] Honesty gate: every number, rating, logo, award and claim has a source the user gave, or is gone.
- [ ] Every link, button and form was clicked at both widths, and each result is recorded.
- [ ] Every exception is on the keep list or carries a `deslop-keep` marker with a reason.
- [ ] Every page rendered and was looked at, at 1440 and 390.
- [ ] Zero console errors and zero horizontal overflow on every route.
- [ ] Type check, lint, copy check and production build pass.
- [ ] Previews and thumbnails refreshed.
- [ ] Nothing pushed or published without the user's go-ahead.

## 11. Report

End with a short report in this shape:

1. **Scope:** what was covered (count of sites and pages).
2. **Removed:** per tell (visual and copy), what changed and roughly how many instances.
3. **Kept on purpose:** each exception and its reason.
4. **Repaired:** layout breakage found and fixed.
5. **Honesty:** each claim kept and its source; each control clicked and where it went.
6. **Verified:** each check, the command or action used, and its result.
7. **Open items:** anything not done or not verified, stated plainly.

## Pitfalls seen in practice

- Disk fills fast with headless browser profiles. Capture one page at a time, delete each profile, watch free space. A full disk breaks the shell and the dev server.
- Do not kill the user's dev server. Start your own on another port and stop it when done.
- Matching on class names alone removes functional labels; match on position and element type.
- Data-driven titles and template-literal page titles are missed by a JSX-only heading scan; the script checks `title:`, `heading:` and `title=` too.
- A pass that skips the parent site, the data file, or the thumbnails is not done.

## Designing new work without the tells

Start from the subject, not a template: one display face and one text face chosen for the trade or audience, one accent color with a meaning, 0 to 6px corners, sentence-case labels, headings without periods, no eyebrows, no numbered sections unless order matters, real copy instead of placeholder labels, and every decorative element tied to something true about the business. Write copy from facts the user gave; where a fact is missing, ask or leave the line out, never fill it with a number, a review or a logo. Run `audit.py` before handing the work over.
