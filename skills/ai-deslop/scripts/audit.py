#!/usr/bin/env python3
"""
AI de-slop audit. Scans CSS, SCSS, HTML, JSX/TSX, Vue, Svelte, Astro and
JS/TS content files for the 20 AI design tells, the copy tells (C1 to C11)
and the honesty gate (H1 to H6), and prints every hit with file:line,
grouped by tell, plus a count summary.

Usage:
  python3 audit.py PATH [PATH ...] [--keep-caps SEL,SEL] [--json] [--only TELLS]

  PATH          files or folders (node_modules, .next, dist, build are skipped)
  --keep-caps   selectors allowed to keep text-transform: uppercase
                (wordmarks, real signage, condensed display heads)
  --only        comma list of tell ids to report, e.g. caps,tracking,period
  --json        machine-readable output

Exit code: 0 when no fix-level hits remain, 1 otherwise. "check" tells
(see CHECK_ONLY) never fail the run; read each one and apply the keep
rules in SKILL.md. Honesty checks (stat, proof, fake-live) pass only with
a source the user gave.
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
    "stock-word": "stock AI words and vague fillers: seamless, elevate, unlock, peace of mind (C1)",
    "hype": "hype openers, reaction prompts, chatbot closers (C2)",
    "staccato": "staccato or triad headings: Fast. Simple. Reliable. (C3)",
    "not-but": "not just X, it's Y contrasts (C4)",
    "title-case": "Title Case in headings, buttons and list items (C7)",
    "emoji": "emoji in copy, headings or buttons (C8)",
    "exclaim": "exclamation marks in UI copy (C9)",
    "em-dash": "em dashes in copy (C10)",
    "bold": "several bold phrases in one paragraph (C11)",
    "stat": "numbers that need a source: 10,000+, 99.9% uptime, 5-star, since 1998 (H1)",
    "proof": "testimonials, ratings, logo bars, awards, certifications, compliance claims (H2)",
    "fake-live": "fake live signals and urgency: people viewing, spots left (H4)",
    "dead-end": "links and controls that go nowhere: href=\"#\", javascript:, empty onClick (H5)",
    "placeholder": "placeholder left in: lorem ipsum, Your Company, John Doe, TODO (H6)",
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

# Copy and honesty patterns run on visible text only (see text_segments).
COPY_RX = {
    "stock-word": re.compile(r"\b(?:seamless(?:ly)?|elevat(?:e|es|ed|ing)|unlock(?:s|ed|ing)?|empower(?:s|ed|ing|ment)?|leverag(?:e|es|ed|ing)|cutting[- ]edge|game[- ]?chang(?:er|ers|ing)|revolutioni[sz](?:e|es|ed|ing)|next[- ]gen(?:eration)?|world[- ]class|best[- ]in[- ]class|state[- ]of[- ]the[- ]art|supercharg(?:e|es|ed|ing)|unleash(?:es|ed|ing)?|transformative|holistic|unparalleled|delv(?:e|es|ing)|tapestry|synerg(?:y|ies|istic)|ever[- ]evolving|fast[- ]paced|countless|a wide (?:range|variety|array) of|all (?:of )?your [\w ]{0,20}needs|one[- ]stop[- ]shop|peace of mind|hassle[- ]free|tailored to (?:your|fit your) (?:unique |specific )?needs|look no further|to the next level)\b", re.I),
    "hype": re.compile(r"\b(?:in today's [\w -]{1,30}(?:world|landscape|age|era)|imagine a world|say goodbye to|let that sink in|read that again|here's the (?:thing|kicker|catch|truth)|the best part\?|but wait|why wait\?|what if (?:you|we) could|ready to (?:take|get|transform|elevate|start|level|unlock|begin)\b[^?<]{0,50}\?|don't just take our word)", re.I),
    "not-but": re.compile(r"\b(?:it's|it is|this is|we're|we are|isn't|is) not just (?:a|an|about|another)\b|\bnot just [\w -]{1,40}(?:,|;|\u2014| -) (?:it's|it is|but|we're)\b|\bmore than just (?:a|an)\b", re.I),
    "emoji": re.compile("[\U0001F300-\U0001FAFF\u2600-\u2604\u2607-\u26FF\u2700-\u2712\u2715-\u27BF\u2B50]"),  # stars and check marks excluded
    "exclaim": re.compile(r"[A-Za-z0-9)][!](?=\s|$|[\"'`<])"),
    "em-dash": re.compile("\u2014|&mdash;"),
    "stat": re.compile(r"\b\d[\d,.]*[kKM]?\+(?=\s+[A-Za-z]{2,}|\s*$)(?!\s+[a-z_]+\.)|\b(?:99(?:\.\d+)?|100)\s?%\s*(?:uptime|satisfaction|satisfied|guarantee|of (?:our )?(?:customers|clients))|#1\b|\b(?:5|five)[- ]stars?\b|\b[34]\.\d\s*(?:/\s*5|stars?|rating|out of 5)|\brated\s+\d|\b\d{2,}\+?\s+years? (?:of )?(?:experience|in business)|\bsince (?:19|20)\d\d\b|\bfounded in (?:19|20)\d\d\b", re.I),
    "proof": re.compile(r"\u2605{3,}|\btrusted by\b|\bas (?:seen|featured) (?:on|in)\b|\bfeatured in\b|\baward[- ]winning\b|\bSOC ?2\b|\bHIPAA\b|\bISO ?27001\b|\bPCI[- ]DSS\b|\bGDPR[- ]compliant\b|\blicensed (?:and|&) insured\b|\bbonded (?:and|&) insured\b|\bcertified (?:experts|professionals|technicians)\b|\bhappy (?:customers|clients)\b", re.I),
    "fake-live": re.compile(r"\b\d+ (?:people|others|users|customers) (?:are )?(?:viewing|watching|looking|booked)\b|\bonly \d+ (?:spots?|seats?|slots?|left)\b|\b(?:spots?|seats?) left\b|\bselling fast\b|\blimited[- ]time offer\b|\boffer ends\b|\bhurry[,!]|\bact now\b", re.I),
    # case-sensitive on purpose: "your company" is ordinary copy, "Your Company" is a placeholder
    "placeholder": re.compile(r"\b[Ll]orem ipsum\b|\bdolor sit amet\b|\bYour Company(?: Name)?\b|\b[Cc]ompany Name\b|\bAcme (?:Inc|Corp)\b|\b(?:John|Jane) Doe\b|\bTODO\b|\bTBD\b|\b[Ii]nsert [\w ]{1,20} here\b"),
}
COPY_TELLS = set(COPY_RX) | {"staccato", "title-case", "dead-end", "bold"}
DEAD_END_RX = re.compile(r"href\s*=\s*(?:[\"']#?[\"']|\{\s*[\"']#?[\"']\s*\}|[\"']javascript:)|on[Cc]lick\s*=\s*\{\s*\(\s*\)\s*=>\s*\{\s*\}\s*\}|onclick\s*=\s*[\"']\s*[\"']|action\s*=\s*[\"']#?[\"']")
STACCATO_RX = re.compile(r"^(?:[A-Za-z][\w'-]*(?: [\w'-]+){0,3}[.!] ){2,}[A-Za-z][\w'-]*(?: [\w'-]+){0,3}[.!]?$")
SMALL_WORDS = {"a", "an", "the", "and", "or", "but", "of", "in", "on", "to", "for", "at", "by", "with", "from", "as", "is", "vs", "per", "&"}
CLASS_ATTR_RX = re.compile(r"(?:class|className|class:list|id|href|src|type|name|rel|as|key|variant|size|role|for|htmlFor|style|d|viewBox|fill|stroke|xmlns|lang|charset|content|property|media|sizes|srcSet|srcset|target|method|loading|decoding|fetchPriority|autoComplete|inputMode)\s*=\s*\{?\s*$")


def text_segments(text, ext):
    """Visible text: text nodes in markup, and prose-like string literals."""
    seen = set()
    if ext in MARKUP_EXT:
        for m in re.finditer(r">([^<>]{2,})<", text):
            seg = m.group(1)
            if re.search(r"[A-Za-z]{2,}", seg) and not re.search(r"^\s*[\w.]+\s*(?:=>|[(){};=]|&&|\|\|)", seg):
                seen.add(m.start(1))
                yield m.start(1), seg, text[max(0, text.rfind("<", 0, m.start())): m.start()]
    if ext in MARKUP_EXT | DATA_EXT:
        for m in re.finditer(r"([\"'`])((?:(?!\1)[^\\\n]|\\.){6,400}?)\1", text):
            seg = m.group(2)
            if m.start(2) in seen or " " not in seg.strip() or not re.search(r"[A-Za-z]{3,} [A-Za-z]", seg):
                continue
            if CLASS_ATTR_RX.search(text[max(0, m.start() - 40): m.start()]):
                continue  # class lists, paths and other non-copy attributes
            if re.fullmatch(r"[\w:/\[\]#().,%-]+(?: [\w:/\[\]#().,%-]+)*", seg) and not re.search(r"[A-Z][a-z]+ [a-z]+", seg) and "-" in seg:
                continue  # looks like a utility class list
            yield m.start(2), seg, text[max(0, m.start() - 40): m.start()]


def is_title_case(plain):
    words = re.findall(r"[A-Za-z][\w'-]*", plain)
    if len(words) < 3 or len(words) > 10:
        return False
    big = [w for w in words if w.lower() not in SMALL_WORDS]
    return len(big) >= 3 and all(w[0].isupper() for w in big) and not all(w.isupper() for w in big)


ABBR = re.compile(r"\b(?:Co|Inc|Ltd|LLC|St|Jr|Sr|Dr|Mr|Mrs|Ms|No|vs|etc|a\.m|p\.m)\.$")

# Tells where a hit needs judgment; everything else is fixed unless on a keep list.
CHECK_ONLY = {"gradient", "glow", "counter-css", "eyebrow", "stripe", "em-heading", "shape",
              "not-but", "title-case", "emoji", "exclaim", "em-dash", "bold", "stat", "proof", "fake-live"}

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
    seen_hits = set()
    keep_lines = {i + 1 for i, l in enumerate(lines) if "deslop-keep" in l}
    # deslop-keep-start ... deslop-keep-end covers a whole block, such as a table of examples
    in_block = False
    for i, l in enumerate(lines):
        if "deslop-keep-start" in l:
            in_block = True
        if in_block:
            keep_lines.add(i + 1)
        if "deslop-keep-end" in l:
            in_block = False

    def add(tell, pos, extra=""):
        ln = line_of(text, pos)
        if ln in keep_lines or (ln - 1) in keep_lines:
            return
        if tell in COPY_TELLS and (tell, ln, extra) in seen_hits:
            return
        seen_hits.add((tell, ln, extra))
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

        heads = []
        for m in HEADING_RX.finditer(text):
            plain = re.sub(r"<[^>]+>|\{\"\s*\"\}|\{[^}]*\}|\s+", " ", m.group(2)).strip()
            heads.append((m.start(), plain))
        n_markup_heads = len(heads)
        for m in re.finditer(r"\b(?:title|heading|headline|tagline)\s*[:=]\s*([\"'`])([^\"'`\n]{3,160})\1", text):
            heads.append((m.start(), m.group(2).strip()))
        for i, (pos, plain) in enumerate(heads):
            if STACCATO_RX.match(plain):
                add("staccato", pos, plain[:100])
                continue
            # data title fields are often business names, so only markup headings count here
            if i < n_markup_heads and is_title_case(plain):
                add("title-case", pos, plain[:100])

        for pos, seg, before in text_segments(text, ext):
            for tell, rx in COPY_RX.items():
                for m in rx.finditer(seg):
                    if tell == "exclaim" and re.search(r"(?:!=|!\w)", seg[m.start(): m.end() + 1]):
                        continue
                    add(tell, pos + m.start(), m.group(0).strip()[:60])
            if re.search(r"<(?:button|a|Link|li|h[4-6])\b[^<]*$", before.strip()) and is_title_case(seg.strip()):
                add("title-case", pos, seg.strip()[:100])

        for m in DEAD_END_RX.finditer(text):
            add("dead-end", m.start(), m.group(0)[:60])

        for m in re.finditer(r"\b(?:testimonials?|reviews?|ratings?|clientLogos|logos)\s*[:=]\s*\[", text):
            add("proof", m.start(), "proof data: confirm every entry is real")

        for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", text, re.S):
            if len(re.findall(r"<(?:strong|b)\b", m.group(1))) >= 2:
                add("bold", m.start(), "several bold phrases in one paragraph")

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
