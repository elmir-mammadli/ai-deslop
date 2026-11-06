#!/usr/bin/env python3
"""
AI de-slop audit. Scans CSS, SCSS, HTML, JSX/TSX, Vue, Svelte, Astro and
JS/TS content files for the 20 AI design tells and prints every hit with
file:line, grouped by tell, plus a count summary.

Usage:
  python3 audit.py PATH [PATH ...] [--keep-caps SEL,SEL] [--json] [--only TELLS]

  PATH          files or folders (node_modules, .next, dist, build are skipped)
  --keep-caps   selectors allowed to keep text-transform: uppercase
                (wordmarks, real signage, condensed display heads)
  --only        comma list of tell ids to report, e.g. caps,tracking,period
  --json        machine-readable output

Exit code: 0 when no fix-level hits remain, 1 otherwise. "check" tells
(gradient, glow, counter-css, eyebrow, stripe, em-heading) never fail the
run; read each one and apply the keep rules in SKILL.md.
"""
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {"node_modules", ".next", ".next-build", "dist", "build", ".git", ".open-next", ".wrangler", "coverage", "out"}
STYLE_EXT = {".css", ".scss", ".sass", ".less"}
MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx"}
DATA_EXT = {".ts", ".js", ".mjs", ".json"}

DEFAULT_FONTS = r"Instrument[ _]Serif|Instrument[ _]Sans|Geist(?:[ _]Mono)?|Space[ _]Grotesk|IBM[ _]Plex[ _]Mono|JetBrains[ _]Mono|Space[ _]Mono"

TELLS = {
    "caps": "ALL CAPS text-transform or utility (18)",
    "tracking": "letter-spacing / tracking, negative or positive (4)",
    "italic": "italic styles and <em>/<i> flair (2)",
    "font": "default AI fonts: Instrument, Geist, Space Grotesk, mono label fonts (3, 17)",
    "mono": "monospace font stacks used for UI text (17)",
    "pill": "pill and squircle radii >= 12px or 999px (1, 16)",
    "gradient": "gradients (19): classify as data scale, photo scrim, hairline, or decoration",
    "stripe": "left accent stripes border-left >= 3px (8)",
    "glow": "glows, blur, backdrop-filter, big soft shadows (7)",
    "outline-text": "outlined / stroked text (5)",
    "counter-css": "CSS-generated numbers via counter() (12)",
    "counter": "number counters in markup: padStart, 0{index+1}, roman lists (12)",
    "section-no": "section numbering strings: 01 /, Chapter, Fig., Plate, § (12)",
    "breadcrumb-code": "code breadcrumbs: //, /path labels, [1], AB-01, STATUS:, TEL/MAIL (11)",
    "eyebrow": "eyebrow: small label element right above a heading (13)",
    "period": "headings and title fields ending in a period (20)",
    "em-heading": "<em>/<i>/accent <span> inside headings (2)",
    "dither": "dither / noise / ASCII art (14, 15)",
    "shape": "shaped corners such as arches (16): keep when it is the art direction",
}

RX = {
    "caps": re.compile(r"text-transform\s*:\s*uppercase|class(?:Name)?=[\"'{`][^\"'`}]*(?<![\w-])uppercase(?![\w-])|>[^<>{}]*?(?<![\w-])[A-Z]{2,}[A-Z&'-]*:?(?: (?:[A-Z]{2,}[A-Z&'-]*:?|&|/|·)){2,}(?![\w-])[^<>{}]*<"),
    "tracking": re.compile(r"letter-spacing\s*:\s*-?[0-9.]+(em|px|rem)|(?<![\w-])tracking-(?!normal\b)[\w\[\]\-.]+"),
    "italic": re.compile(r"font-style\s*:\s*italic|font\s*:\s*italic|class(?:Name)?=[\"'{`][^\"'`}]*(?<![\w-])italic(?![\w-])"),
    "font": re.compile(DEFAULT_FONTS),
    "mono": re.compile(r"monospace|(?<![\w-])font-mono(?![\w-])|--[\w-]*mono\b"),
    "pill": re.compile(r"border(?:-[a-z-]+)?-radius\s*:\s*(?:999+px|9999px|50rem|[1-9][2-9]px|[2-9][0-9]px|[1-9][0-9]{2}px)|(?<![\w-])rounded-(?:full|xl|2xl|3xl)(?![\w-])"),
    "gradient": re.compile(r"(?:linear|radial|conic|repeating-linear|repeating-radial)-gradient\(|(?<![\w-])bg-gradient-"),
    "stripe": re.compile(r"border-left\s*:\s*[3-9]px|(?<![\w-])border-l-[4-8](?![\w-])"),
    "glow": re.compile(r"backdrop-filter|filter\s*:\s*blur|box-shadow\s*:[^;]*\b([4-9][0-9]|1[0-9]{2})px|(?<![\w-])(backdrop-blur|blur-(?:xl|2xl|3xl)|shadow-(?:xl|2xl))(?![\w-])"),
    "outline-text": re.compile(r"(?:-webkit-)?text-stroke(?:-width)?\s*:\s*(?!0(?:px)?\s*;)"),
    "counter-css": re.compile(r"content\s*:[^;]*counter\("),
    "counter": re.compile(r"padStart\(\s*[23]\s*,\s*[\"']0[\"']\)|0\{\s*\w*[iI]ndex\s*\+\s*1\s*\}|\[\s*[\"']i[\"']\s*,\s*[\"']ii[\"']|\[\s*[\"']I[\"']\s*,\s*[\"']II[\"']|decimal-leading-zero|upper-roman|lower-roman"),
    "section-no": re.compile(r">\s*(?:0[1-9]|[IVX]{1,4})\s*(?:/|·|\.|—|-)\s*\w|§\s*\d|\bChapter\s+\{|\b(?:Fig\.|Plate)\s+[IVX\d]|[\"']0[1-9] ·"),
    "breadcrumb-code": re.compile(r">\s*//\s*\w|>\s*/(?!(?:mo|month|yr|year|hr|hour|day|week|sq|ft|unit|ea|each|visit|person)\b)[a-z][\w-]*\s*<|>\s*\[\s*\d\s*\]|[\"'][A-Z]{1,3}-0[1-9][\"']|STATUS:|>\s*(?:TEL|MAIL|AREA|ADDR)\s*<|<dt>(?:TEL|MAIL|AREA)</dt>"),
    "dither": re.compile(r"feTurbulence|dither[\w-]*\.(?:png|svg|gif|webp)|class(?:Name)?=[\"'{`][^\"'`}]*dither|noise\.(?:png|svg|webp)|<pre[^>]*>\s*[#@%*=+.:-]{12,}", re.I),
}

ABBR = re.compile(r"\b(?:Co|Inc|Ltd|LLC|St|Jr|Sr|Dr|Mr|Mrs|Ms|No|vs|etc|a\.m|p\.m)\.$")

# Tells where a hit needs judgment; everything else is fixed unless on a keep list.
CHECK_ONLY = {"gradient", "glow", "counter-css", "eyebrow", "stripe", "em-heading", "shape"}

HEADING_RX = re.compile(r"<(h[1-3]|PageTitle|SplitTitle|Heading|Title)\b[^>]*>(.*?)</\1>", re.S)
TITLE_FIELD_RX = re.compile(r"(?:\b(?:title|heading|headline|catalogueTitle|h1|h2)\s*[:=]\s*)([\"'`])([^\"'`]{3,160}?)\.\1")
EYEBROW_EL_RX = re.compile(r"<(p|span|div|small)\b[^>]*>([^<]{1,60})</\1>")


def iter_files(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in STYLE_EXT | MARKUP_EXT | DATA_EXT:
                    yield os.path.join(d, f)


def strip_comments(text, ext):
    """Blank out comments but keep newlines so line numbers stay true."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    if ext not in STYLE_EXT:
        text = re.sub(r"\{\s*/\*.*?\*/\s*\}", blank, text, flags=re.S)
    if ext in MARKUP_EXT:
        # code samples on a page are content, not styling
        text = re.sub(r"(<(pre|code)\b[^>]*>)(.*?)(</\2>)", lambda m: m.group(1) + re.sub(r"[^\n]", " ", m.group(3)) + m.group(4), text, flags=re.S)
        text = re.sub(r"(?m)(^|[^:\"'`/\\])//(?![/*]).*$", lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), text)
    return text


def css_selector_at(text, pos):
    """Selector of the CSS rule that contains pos."""
    open_ = text.rfind("{", 0, pos)
    if open_ < 0:
        return ""
    start = max(text.rfind("}", 0, open_), text.rfind("*/", 0, open_), text.rfind("{", 0, open_))
    return " ".join(text[start + 1 : open_].split()).strip()


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan(path, keep_caps):
    hits = []
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return hits
    ext = os.path.splitext(path)[1].lower()
    raw_text = text
    text = strip_comments(text, ext)
    is_style = ext in STYLE_EXT
    is_markup = ext in MARKUP_EXT
    lines = raw_text.split("\n")
    keep_lines = {i + 1 for i, l in enumerate(lines) if "deslop-keep" in l}

    def add(tell, pos, extra=""):
        ln = line_of(text, pos)
        if ln in keep_lines or (ln - 1) in keep_lines:
            return
        snippet = lines[ln - 1].strip()[:140]
        hits.append({"tell": tell, "file": path, "line": ln, "text": snippet, "note": extra})

    style_tells = ["caps", "tracking", "italic", "font", "mono", "pill", "gradient", "stripe", "glow", "outline-text", "counter-css"]
    markup_tells = ["caps", "tracking", "italic", "font", "mono", "pill", "gradient", "stripe", "glow", "counter", "section-no", "breadcrumb-code", "dither"]
    data_tells = ["font", "counter", "section-no", "breadcrumb-code"]
    active = style_tells if is_style else markup_tells if is_markup else data_tells

    for tell in active:
        for m in RX[tell].finditer(text):
            if is_style:
                sel = css_selector_at(text, m.start())
                parts = [x.strip() for x in sel.split(",") if x.strip()]
                kept = bool(parts) and all(any(x == k or x.startswith(k + " ") or x.startswith(k + ":") for k in keep_caps) for x in parts)
                if tell == "caps" and kept:
                    continue
                if tell == "tracking" and kept and not re.match(r"letter-spacing\s*:\s*-", m.group(0)):
                    continue  # positive tracking on kept caps is allowed
                if tell == "gradient":
                    body = text[m.start(): text.find(";", m.start())]
                    if re.search(r"transparent\s+calc\(", body) or body.count("transparent") >= 2 and "calc(" in body:
                        add(tell, m.start(), f"in {sel}: hard-stop hairline, usually fine")
                        continue
                if tell == "pill":
                    v = m.group(0)
                    if re.search(r"(\d+px)\s+\1\s+\d+px\s+\d+px", text[m.start(): text.find(";", m.start())]):
                        add("shape", m.start(), f"in {sel}: shaped corners (arch or tab), check intent")
                        continue
                if tell == "stripe" and re.search(r"::?(before|after)", sel):
                    # likely a CSS-drawn checkmark or arrow; flag softly
                    add(tell, m.start(), f"in {sel}: check it is not a drawn icon")
                    continue
                if tell == "tracking" and re.search(r"letter-spacing\s*:\s*0(em|px)?\s*;", text[m.start(): m.start() + 30]):
                    continue
                add(tell, m.start(), sel)
            else:
                if tell == "font" and not re.search(r"font-family|fontFamily|family=|next/font|@import|import\s*\{|=\s*[A-Z][A-Za-z_]+\(|typography", lines[line_of(text, m.start()) - 1]):
                    continue  # a font named in prose, not used
                if tell == "pill" and m.group(0) == "rounded-full":
                    cls = raw_text[max(0, raw_text.rfind('"', 0, m.start()) ): raw_text.find('"', m.end()) + 1]
                    hw = re.findall(r"(?<![\w-])([hw])-(\[?[\w.]+\]?)", cls)
                    sizes = {k: v for k, v in hw}
                    if sizes.get("h") and sizes.get("h") == sizes.get("w"):
                        continue  # a circle, not a pill
                add(tell, m.start())

    if is_markup or ext in DATA_EXT:
        for m in HEADING_RX.finditer(text):
            inner = m.group(2)
            plain = re.sub(r"<[^>]+>|\{\"\s*\"\}|\s+", " ", inner).strip()
            if plain.endswith(".") and not plain.endswith("...") and not ABBR.search(plain):
                add("period", m.start(), plain[:100])
            if re.search(r"<(em|i)\b|<span\b[^>]*class(Name)?=", inner):
                add("em-heading", m.start(), plain[:100])
        for m in TITLE_FIELD_RX.finditer(text):
            if ABBR.search(m.group(2) + "."):
                continue
            add("period", m.start(), m.group(2)[:100] + ".")

    if is_markup:
        # eyebrow: short text element whose next non-blank lines open a heading
        for i, raw in enumerate(lines):
            em = EYEBROW_EL_RX.search(raw)
            if not em or re.search(r"<(h[1-6]|label|legend|dt|th|button|a|Link)\b|aria-hidden", raw):
                continue
            label = em.group(2).strip()
            words = re.sub(r"\{[^}]*\}", "X", label).split()
            if not words or len(words) > 6 or label.endswith("."):
                continue
            after = "\n".join(lines[i + 1 : i + 3])
            before = "\n".join(lines[max(0, i - 2) : i])
            if re.search(r"<(h[1-3]|PageTitle|SplitTitle|Heading)\b", after) and not re.search(r"</?(h[1-6]|PageTitle|SplitTitle|Heading)\b", before):
                pos = sum(len(l) + 1 for l in lines[:i])
                add("eyebrow", pos, em.group(2).strip()[:60])
    return hits


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True) for a in argv if a.startswith("--")}
    i = 0
    paths, keep_caps, only = [], [], None
    raw = argv[:]
    while i < len(raw):
        a = raw[i]
        if a in ("--keep-caps", "--only"):
            val = raw[i + 1] if i + 1 < len(raw) else ""
            if a == "--keep-caps":
                keep_caps = [s.strip() for s in val.split(",") if s.strip()]
            else:
                only = set(s.strip() for s in val.split(",") if s.strip())
            i += 2
            continue
        if a.startswith("--keep-caps="):
            keep_caps = [s.strip() for s in a.split("=", 1)[1].split(",") if s.strip()]
        elif a.startswith("--only="):
            only = set(s.strip() for s in a.split("=", 1)[1].split(",") if s.strip())
        elif not a.startswith("--"):
            paths.append(a)
        i += 1
    if not paths:
        print(__doc__)
        return 2

    hits = []
    for f in iter_files(paths):
        hits.extend(scan(f, keep_caps))
    if only:
        hits = [h for h in hits if h["tell"] in only]

    fixes = [h for h in hits if h["tell"] not in CHECK_ONLY]
    if "--json" in argv:
        print(json.dumps(hits, indent=2))
        return 1 if fixes else 0

    by = defaultdict(list)
    for h in hits:
        by[h["tell"]].append(h)
    for tell in TELLS:
        group = by.get(tell)
        if not group:
            continue
        kind = "check" if tell in CHECK_ONLY else "fix"
        print(f"\n== {tell} [{kind}]: {TELLS[tell]}  [{len(group)}]")
        for h in group:
            note = f"  ({h['note']})" if h["note"] else ""
            print(f"  {h['file']}:{h['line']}  {h['text']}{note}")
    print("\nSummary")
    for tell in TELLS:
        print(f"  {tell:16} {len(by.get(tell, []))}")
    print(f"  {'total':16} {len(hits)}  (fix: {len(fixes)}, check: {len(hits) - len(fixes)})")
    print("\nPASS: no fix-level tells left" if not fixes else "\nFAIL: fix-level tells remain")
    return 1 if fixes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
