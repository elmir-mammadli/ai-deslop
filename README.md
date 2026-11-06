<p align="center">
  <img src=".claude-plugin/icon.png" width="96" height="96" alt="AI De-slop">
</p>

<h1 align="center">AI De-slop</h1>

<p align="center">
  A Claude skill that finds and removes the tells that make a website look AI-generated,<br>
  then proves nothing broke where they used to be.
</p>

<p align="center">
  <a href="https://elmir-mammadli.github.io/ai-deslop/">Documentation</a> ·
  <a href="#install">Install</a> ·
  <a href="#the-audit-script">Audit script</a> ·
  <a href="#the-20-tells">The 20 tells</a> ·
  <a href="#copy-tells">Copy tells</a> ·
  <a href="#the-honesty-gate">Honesty gate</a>
</p>

---

Generated pages share a look: an uppercase eyebrow over every heading, `01 / 02 / 03` section numbers, mono labels, pill buttons, a soft gradient, a period at the end of every headline. Each choice is harmless alone. Together they read as "nobody designed this".

AI De-slop gives Claude a precise playbook for removing them:

- **Exact rules** for 20 visual tells and 11 copy tells, with the action to take and the cases where the element should stay.
- **An honesty gate** that blocks invented proof: unsourced numbers, made-up reviews and logos, fake urgency, dead links and leftover placeholders.
- **An audit script** that scans CSS, HTML, JSX/TSX, Vue, Svelte, Astro and data files, lists every hit with file and line, and fails until fix-level tells reach zero. It reads styles and markup for the visual tells, and the visible text for the copy tells and honesty claims.
- **A repair checklist** for what removal breaks: grid columns that held a number, indents that aligned past one, dead classes, fonts that change line counts.
- **A definition of done** and a fixed report format, so a pass is never declared finished on a subset.

It was built while de-slopping 27 production concept websites and the site that hosts them, and every rule in it comes from something that went wrong or right during that work.

## Install

### Claude Code, as a plugin

```
/plugin marketplace add elmir-mammadli/ai-deslop
/plugin install ai-deslop@ai-deslop
```

### Claude Code, as a personal skill

```bash
git clone https://github.com/elmir-mammadli/ai-deslop.git /tmp/ai-deslop
cp -R /tmp/ai-deslop/skills/ai-deslop ~/.claude/skills/
```

Every project on your machine can now use it. To share it with a team instead, copy `skills/ai-deslop` into the project's `.claude/skills/` folder and commit it.

### Claude.ai

1. Download [`ai-deslop.zip`](https://github.com/elmir-mammadli/ai-deslop/releases/latest) from the latest release, or zip the `skills/ai-deslop` folder yourself.
2. Open **Settings → Capabilities → Skills** and upload the zip.

Skills on claude.ai depend on your plan and settings; if you do not see the Skills section, it is not enabled for your account yet.

## Use

Ask in plain words. The skill loads on its own when the request matches:

```
Deslop the marketing site in apps/web.
This landing page looks AI-made. Fix it.
Here are the 20 AI slop indicators. Go through every page and remove them.
Build a pricing page for a roofing company, art-directed, no AI tells.
```

Claude then works through a fixed order: scope, audit, keep list, edit, repair, verify, report. It stops only when the definition of done is met, and ends with a report of what was removed, what was kept on purpose and why, what broke and was repaired, and what was checked.

## The audit script

The script ships inside the skill and runs on its own too. It needs Python 3 and nothing else.

```bash
python3 skills/ai-deslop/scripts/audit.py src
python3 skills/ai-deslop/scripts/audit.py src --keep-caps ".wordmark,.logo,.heroTitle"
python3 skills/ai-deslop/scripts/audit.py src --only caps,tracking,period
python3 skills/ai-deslop/scripts/audit.py src --json > audit.json
```

| Option | What it does |
|--------|--------------|
| `--keep-caps` | Selectors allowed to keep uppercase and positive letter-spacing: wordmarks, real signage, condensed display headlines |
| `--only` | Report only these tells, comma separated |
| `--json` | Machine-readable output |

Hits are grouped into **fix** tells, which must reach zero, and **check** tells, which need a human verdict but never fail the run. Check tells are gradients, glows, CSS counters, eyebrows, accent stripes, emphasis in headings, shaped corners, "not just X" contrasts, Title Case, emoji, exclamation marks, em dashes, scattered bold, and the honesty claims (`stat`, `proof`, `fake-live`), which pass only with a real source. The exit code is `0` when no fix-level tells remain and `1` otherwise, so the script works as a CI gate.

Sample run on the files in [`examples/`](examples):

```
python3 skills/ai-deslop/scripts/audit.py examples/before.html

== caps [fix]: ALL CAPS text-transform or utility (18)  [3]
  examples/before.html:24  text-transform: uppercase; letter-spacing: 0.18em; color: #7c3aed;
...
Summary
  total            65  (fix: 41, check: 24)

FAIL: fix-level tells remain
```

```
python3 skills/ai-deslop/scripts/audit.py examples/after.html
...
PASS: no fix-level tells left
```

### Keeping something on purpose

Some tells are the right call: rounded pipe ends on a plumbing site, a print texture that is the whole art direction. Mark the line, or the line above it, and the audit skips it:

```css
border-radius: 999px; /* deslop-keep: rounded pipe ends */
```

```jsx
{/* deslop-keep: printed paper edge is the art direction */}
<feTurbulence type="fractalNoise" baseFrequency="0.9" />
```

To skip a whole block, such as a table that quotes the tells as examples, wrap it:

```html
<!-- deslop-keep-start: this table quotes the tells as examples -->
...
<!-- deslop-keep-end -->
```

Always give a reason. The marker is a decision, not an escape hatch.

## The 20 tells

| # | Tell | Action | Keep when |
|---|------|--------|-----------|
| 1 | Tags and pills | 999px radius to 3 to 4px, or plain colored text | The tag carries state the reader acts on |
| 2 | Excessive italics | Remove italics and `<em>` used for flair | Titles of works, quoted terms, wordmarks |
| 3 | Default AI fonts | Replace Instrument Serif/Sans, Geist, Space Grotesk, IBM Plex Mono, JetBrains Mono, Space Mono as the page voice | Never as the voice |
| 4 | Negative kerning | Remove all negative letter-spacing | Never |
| 5 | Over-detailed UI | Remove gadgets: live dots, fake trackers, cursor lenses, magnetic buttons, skew marquees | The gadget is the product |
| 6 | Overusing dividers | At most one structural rule per list | The rule groups rows |
| 7 | Shades and opacities | Solid tokens; no glows, blur or soft 40px+ shadows | Photo scrims, one subtle elevation on a real overlay |
| 8 | Bordered containers | Unbox decorative cards, remove left accent stripes | Real objects (forms, tickets, tables) and status stripes |
| 9 | Over-detailed diagrams | Cut plates, figure labels and legends that do not explain | Every element maps to something real |
| 10 | Verbose, redundant text | One footer disclosure instead of repeated notes | The note adds new information |
| 11 | Code breadcrumbs | Remove `// LABEL`, `/services`, `[1]`, `EV-01`, `STATUS:` | A real navigation breadcrumb |
| 12 | Section numbering | Remove `01 /`, `§`, chapters, roman numerals, padded counters | Order is the content; then plain `1.` |
| 13 | Eyebrows | Remove; move any fact it held into the heading or body | Form labels, legends, `dt`, table and column heads |
| 14 | Dithering and noise | Remove | The texture is the art direction, marked `deslop-keep` |
| 15 | ASCII images | Remove | Never by default |
| 16 | Squircles | 12px+ radius to 4 to 6px | True circles and deliberate shapes |
| 17 | Mono fonts | Text face plus `tabular-nums` | Real code |
| 18 | ALL CAPS subtitles | Remove uppercase and its tracking | Wordmarks, signage, condensed display brands |
| 19 | Gradient backgrounds | Solid color | Data scales, photo scrims, hairlines |
| 20 | Periods in titles | Drop the final period of headings and title fields | Body text, multi-sentence paragraphs, abbreviations |

## Copy tells

| # | Tell | Action | Keep when |
|---|------|--------|-----------|
| C1 | Stock words: seamless, elevate, unlock, cutting-edge, world-class, peace of mind, hassle-free | Say the concrete thing: what is done, how fast, for how much | The word is literal, as when a locksmith unlocks |
| C2 | Hype openers and closers: "In today's fast-paced world", "Let that sink in", "Ready to take the next step?" | Delete; start with the fact, end on the action | Never |
| C3 | Staccato headings: "Fast. Simple. Reliable." | One natural sentence | A question plus an instruction |
| C4 | "Not just X, it's Y" | State Y plainly | It corrects a real misunderstanding |
| C5 | A heading restated by the sentence under it | Cut the sentence, or make the heading the fact | Never |
| C6 | Every card the same sentence shape and length | Write each card from its own fact | Data tables |
| C7 | Title Case On Headings And Buttons | Sentence case | Proper nouns and real titles |
| C8 | Emoji as bullets or in headings | Remove | Messaging products, emoji-led brands |
| C9 | Exclamation marks in interface copy | A period, or nothing | Quoted speech, one real success message |
| C10 | Em dashes in copy | Comma, colon or two sentences | The house style allows them |
| C11 | Bold sprinkled through body text | At most one bold fact per section | A warning or a price that must not be missed |

## The honesty gate

A page is not finished while it claims something nobody can back up. There is no style reason to keep any of these, only a real source.

| # | Claim | Action |
|---|-------|--------|
| H1 | Numbers that need a source: 10,000+ customers, 99.9% uptime, 4.9 rating, since 1998 | Keep only with a source; otherwise remove, or turn into a true process fact |
| H2 | Testimonials, star ratings, "Trusted by" logo bars, awards, certifications, compliance badges | Keep only what the business confirmed; never write one |
| H3 | Invented team members, founders, quotes, addresses and history | Remove, or leave an honest placeholder on drafts |
| H4 | Fake live signals: "3 people viewing", "Only 2 spots left", countdowns | Remove unless real data drives it |
| H5 | Dead ends: `href="#"`, empty click handlers, nav items to missing pages | Point it somewhere real, or remove the control |
| H6 | Placeholder left in: lorem ipsum, Your Company, Jane Doe, TODO | Real content, or remove the block |

Sample and concept sites may invent a business name and contact details only in reserved formats (555-01XX numbers, `.example` domains), with one disclosure in the footer. They never invent reviews, ratings, logos, awards or counts. The gate is proved, not asserted: every link, button and form is clicked, and where it went is recorded in the report.

The full rules, including copy rewrites, the repair checklist and the definition of done, are in [`skills/ai-deslop/SKILL.md`](skills/ai-deslop/SKILL.md).

## Repository layout

```
.claude-plugin/        plugin and marketplace manifests, listing icon
skills/ai-deslop/
  SKILL.md             the playbook Claude follows
  references/audit.md  manual searches and the visual check protocol
  scripts/audit.py     the scanner
examples/              a deliberately sloppy page and its fixed version
docs/                  the documentation site
```

## FAQ

**Does it change my design language?**
No. It removes tells and keeps the identity. A condensed-caps brand keeps its caps on the headlines that define it; a texture that is the art direction stays, marked as such.

**Does it work without Claude?**
The audit script does. The judgment calls, rewrites and repairs are what the skill teaches Claude to do.

**Which frameworks?**
Anything that ends up as CSS and markup: plain HTML, React and Next.js, Vue, Svelte, Astro, Tailwind or CSS Modules.

**Will it flag things that are fine?**
Sometimes, which is why hits are split into fix and check, and why keep lists and `deslop-keep` markers exist. A clean run means zero fix-level tells, not zero hits.

## Contributing

Issues and pull requests are welcome, especially new tells with a clear keep rule, false positives in the script with a small reproduction, and support for more file types. Run the script on `examples/` before and after any change to it.

## License

[MIT](LICENSE) © 2026 Elmir Mammadli
