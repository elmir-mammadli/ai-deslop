# Audit patterns

Start with `scripts/audit.py`; it covers most of what follows, skips comments, honors `--keep-caps` and `deslop-keep` markers, and gates on `fix: 0`. Use the manual searches below for what it cannot see, or when the script is not available.

Run these per site (or per component folder). Adjust globs to the project: CSS Modules, Tailwind classes in TSX, or plain CSS. Read every hit before changing it; the table in SKILL.md decides keep or remove.

## CSS

```bash
F=path/to/site.module.css
grep -n 'text-transform: *uppercase' $F
grep -n 'letter-spacing' $F
grep -n 'font-style: *italic' $F
grep -ni 'mono' $F                       # monospace stacks and --*-mono vars
grep -nE 'radius: *(999|[1-9][0-9]+)px' $F
grep -n 'gradient(' $F                  # then classify: data scale, photo scrim, or decoration
grep -nE 'border-left: *[3-9]px' $F     # accent stripes (check ::before checkmarks first)
grep -n 'counter(' $F                   # CSS-generated numbers, invisible in markup
grep -n -- '-webkit-text-stroke' $F     # outlined wordmarks
grep -nE 'backdrop-filter|filter: *blur' $F
```

## Tailwind / utility classes

```bash
grep -rnE 'uppercase|tracking-|italic|font-mono|rounded-(full|xl|2xl|3xl)|bg-gradient|backdrop-blur' components app
```

## Markup

```bash
# eyebrow candidates: small p/span within 3 lines above a heading
# counters
grep -rnE 'padStart|0\{index \+ 1\}|\{index \+ 1\}|"0[1-9]"|Chapter \{|\["i", "ii"' src
# code breadcrumbs
grep -rnE '>//|>/[a-z-]+<|STATUS:|"[A-Z]{1,2}-0[1-9]"|\[[0-9]\]' src
# headings ending in a period or containing <em>
#   h1-h3, PageTitle-like components, title= props, title:/heading:/headline: data fields, template literals
grep -rnE 'title: "[^"]+\.",|heading="[^"]+\."|title="[^"]+\."' src
```

A small script that walks `<h1|h2|h3|PageTitle ...>…</…>` blocks, strips tags, and flags text ending in "." or containing `<em>` is more reliable than grep for multi-line headings.

## Copy and honesty

`audit.py` covers these on visible text. Without it:

```bash
grep -rniE 'seamless|elevat|unlock|cutting.edge|world.class|game.chang|next.gen|peace of mind|hassle.free|one.stop' src
grep -rniE "in today's|let that sink in|ready to [a-z]+.*\?|not just an? |more than just" src
grep -rnE '[0-9][0-9,.]*[kKM]?\+ [A-Za-z]|99\.9%|#1\b|5.star|[34]\.[0-9] (rating|stars)|since (19|20)[0-9]{2}' src
grep -rniE 'trusted by|as seen (on|in)|award.winning|SOC ?2|HIPAA|licensed (and|&) insured|testimonials? *[:=]' src
grep -rnE 'href="#?"|href=\{"#"\}|javascript:|onClick=\{\(\) => \{\}\}' src
grep -rnE 'Lorem ipsum|Your Company|John Doe|Jane Doe|TODO|TBD' src
```

Then the checks no script can make:

- Read every heading next to the sentence under it; cut the one that only repeats the other.
- Read a row of cards aloud; if every card has the same shape and length, rewrite each from its own fact.
- Open every nav link, button and form at 1440 and 390. Write down where each one went.
- For every number, rating, logo, award or certification left on the page, name its source. No source, no claim.

## After removal: find what broke

```bash
# grids that reserved a number column
grep -nE 'grid-template-columns: *[0-9]{2,3}px +(1fr|minmax)' $F
# text indented past a removed number
grep -nE '(margin|padding)(-left)?: *[^;]*\b(2[8-9]|[3-6][0-9])px;' $F
```

- List classes defined in CSS that no markup references any more and delete them (skip classes built dynamically, like `s[\`badge_${x}\`]`).
- Run lint for unused `index` params, props and imports left behind.
- Check British spellings if the project is US English: centre, colour, favour, organis-, realis-, metre, behaviour.

## Visual pass

- Two widths: 1440 and 390.
- Emulate `prefers-reduced-motion: reduce` so animated sections render in their final state.
- Scroll through the page before the capture so lazy images load, then return to the top.
- Remove dev overlays before capture (Next.js: `document.querySelectorAll('nextjs-portal').forEach(n => n.remove())`).
- Capture one page at a time; delete each temporary browser profile afterwards and watch free disk space.
- Automated pass on every route: console errors and `document.documentElement.scrollWidth > innerWidth`.
