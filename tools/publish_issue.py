#!/usr/bin/env python3
"""Publish a sent Maine Ledger issue into the self-hosted /archive/."""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive"
MANIFEST = ARCHIVE / "issues.json"

TOWNS = {
    "brunswick": "Brunswick",
    "topsham": "Topsham",
    "harpswell": "Harpswell",
    "bath": "Bath",
    "freeport": "Freeport",
}
TOWN_ORDER = ["brunswick", "topsham", "harpswell", "bath", "freeport"]

MONTHS_SHORT = {
    1: "Jan.",
    2: "Feb.",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug.",
    9: "Sept.",
    10: "Oct.",
    11: "Nov.",
    12: "Dec.",
}
MONTHS_LONG = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}
WEEKDAYS_SHORT = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
WEEKDAY_RE = (
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|"
    r"Thursday|Friday|Saturday|Sunday)\.?"
)
MONTH_RE = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?)\.?"
)
DATE_CHUNK_RE = re.compile(
    rf"^(?:{WEEKDAY_RE}\s*,?\s*)?{MONTH_RE}\s+\d{{1,2}}"
    rf"(?:st|nd|rd|th)?(?:,\s*\d{{4}})?$",
    re.I,
)
STORY_CELL_RE = re.compile(
    r'<td\b[^>]*class="[^"]*\bml-story\b[^"]*"[^>]*>([\s\S]*?)</td>',
    re.I,
)

TEST_BANNER_TEXT = re.compile(r"^still in testing,\s*please do not forward\.?$", re.I)
UNSUB_TEMPLATE = re.compile(
    r"\{\{\s*(unsubscribe_url|manage_subscription_url|preferences_url)\s*\}\}"
)
UNSUB_HREF = re.compile(
    r"""href=["'][^"']*(unsubscribe|manage_subscription|preferences)[^"']*["']""",
    re.I,
)
UNSUB_TEXT = re.compile(
    r"^(unsubscribe|update preferences|manage (?:your )?(?:preferences|subscription))"
    r"(?:[\s·|,/-]+(unsubscribe|update preferences|manage (?:your )?(?:preferences|subscription)))*$",
    re.I,
)
POWERED_TEXT = re.compile(r"^powered\s+by\s+buttondown\.?$", re.I)
LOGIN_TEXT = re.compile(r"^(log\s*in|sign\s*in)(?:\s+to\s+buttondown)?\.?$", re.I)
BUTTONDOWN_LINK = re.compile(
    r"""<a\b[^>]*href=["']https?://(?:www\.)?buttondown\.(?:com|email)(?:/[^"']*)?["'][^>]*>[\s\S]*?</a>""",
    re.I,
)
BUTTONDOWN_COMMENT = re.compile(
    r"<!--(?:(?!-->).)*buttondown(?:(?!-->).)*-->\s*",
    re.I | re.S,
)
P_TAG = re.compile(r"<p\b[^>]*>[\s\S]*?</p>", re.I)
IMG_TAG = re.compile(r"<img\b[^>]*/?>", re.I)
STYLE_TAG = re.compile(r"<style\b[^>]*>[\s\S]*?</style>", re.I)
META_TAG = re.compile(r"<meta\b[^>]*>", re.I)
TITLE_TAG = re.compile(r"<title\b[^>]*>([\s\S]*?)</title>", re.I)
TEMPLATE_TAG = re.compile(r"\{\{[^}]*\}\}|\{%[^%]*%\}")
TRACK_SRC = re.compile(
    r"track(?:ing)?|pixel|/open(?:\.gif|/)|open-tracking|email-track",
    re.I,
)

CHROME_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#f6f2e8">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/site.css">
</head>
<body>
<div class="notice-strip" role="status"><b>Still in beta</b>, not ready for the public yet.</div>
<header class="w masthead">
  <div class="mast-row">
    <p class="nameplate"><a href="/">The Maine Ledger</a></p>
  </div>
  <div class="edition">Midcoast Editions</div>
  <div class="dateline"><span class="dl-date" id="today"></span></div>
</header>
<nav class="site-nav" aria-label="Site">
  <div class="w">
    <ul>
      <li><a href="/">Subscribe</a></li>
      <li><a href="/archive/" aria-current="page">Archive</a></li>
      <li><a href="/trackers/">Trackers</a></li>
      <li><a href="/advertise/">Advertise</a></li>
      <li><a href="/about/">About</a></li>
    </ul>
  </div>
</nav>
"""

CHROME_FOOT = """<footer class="site-foot"><div class="w">© 2026 The Maine Ledger · <a href="mailto:ben@themaineledger.com">ben@themaineledger.com</a></div></footer>
<script>
(function(){
  try{document.getElementById('today').textContent=new Date().toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric',timeZone:'America/New_York'})}catch(e){}
})();
</script>
</body>
</html>
"""


def visible_text(markup: str) -> str:
    text = re.sub(r"<[^>]+>", " ", markup)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def format_list_date(send_date: date) -> str:
    weekday = WEEKDAYS_SHORT[send_date.weekday()]
    month = MONTHS_SHORT[send_date.month]
    return f"{weekday}, {month} {send_date.day}, {send_date.year}"


def looks_like_headline(text: str) -> bool:
    if not text or len(text) < 8:
        return False
    if DATE_CHUNK_RE.match(text):
        return False
    if re.fullmatch(r"The\s+Maine\s+Ledger", text, re.I):
        return False
    if text.lower() in {name.lower() for name in TOWNS.values()}:
        return False
    if text.isupper() and len(text) < 40:
        return False
    if re.search(r"\btop story\b", text, re.I) and len(text) < 40:
        return False
    if re.fullmatch(r"[\d$,.%]+", text.replace(",", "").replace(" ", "")):
        return False
    words = text.split()
    if len(words) < 3:
        return False
    return True


def derive_subject_from_title(title: str, town_label: str) -> str | None:
    text = title.strip()
    text = re.sub(r"^The\s+Maine\s+Ledger(?:\s*[·|:–—-]+\s*|\s+)", "", text, flags=re.I)
    text = re.sub(
        rf"(?:^|(?<=[·|:–—-])\s*){re.escape(town_label)}\s*(?:[·|:–—-]\s*|$)",
        "",
        text,
        flags=re.I,
    )
    leftover = re.sub(r"[\s·|:–—,]+", " ", text).strip()
    leftover = leftover.strip(" \t·|:–—,")
    if not leftover or DATE_CHUNK_RE.match(leftover):
        return None
    leftover = re.sub(
        rf"(?:[·|:–—-]\s*)?(?:{WEEKDAY_RE}\s*,?\s*)?{MONTH_RE}\s+\d{{1,2}}"
        rf"(?:st|nd|rd|th)?(?:,\s*\d{{4}})?\s*$",
        "",
        leftover,
        flags=re.I,
    ).strip(" \t·|:–—,")
    leftover = re.sub(r"\s+", " ", leftover).strip()
    if not leftover or DATE_CHUNK_RE.match(leftover):
        return None
    if re.fullmatch(r"The\s+Maine\s+Ledger", leftover, re.I):
        return None
    if leftover.lower() == town_label.lower():
        return None
    if len(leftover) < 3:
        return None
    return leftover


def extract_headline_from_html(html: str) -> str | None:
    cells = STORY_CELL_RE.findall(html)
    regions = cells if cells else [html]
    for region in regions:
        for match in P_TAG.finditer(region):
            block = match.group(0)
            if re.search(
                r'class="[^"]*\b(?:ml-label|ml-kicker|ml-credit|ml-body)\b',
                block,
                re.I,
            ):
                continue
            opening = block.split(">", 1)[0]
            size_match = re.search(r"font-size:\s*([\d.]+)px", opening, re.I)
            if not size_match:
                continue
            size = float(size_match.group(1))
            if size < 21:
                continue
            weighted = bool(
                re.search(r"font-weight:\s*(700|bold)", opening, re.I)
            ) or bool(re.search(r"<b\b", block, re.I))
            if not weighted and size < 24:
                continue
            text = visible_text(block)
            if looks_like_headline(text):
                return text
    for match in re.finditer(r"<h[12]\b[^>]*>([\s\S]*?)</h[12]>", html, re.I):
        text = visible_text(match.group(1))
        if looks_like_headline(text):
            return text
    return None


TOWN_SUBJECT_RE = re.compile(
    r"^(?:" + "|".join(re.escape(name) for name in TOWNS.values()) + r"):\s+\S",
    re.I,
)


def is_town_subject_title(title: str) -> bool:
    return bool(TOWN_SUBJECT_RE.match(title.strip()))


def is_old_style_title(title: str) -> bool:
    return bool(re.match(r"^The\s+Maine\s+Ledger\b", title.strip(), re.I))


def choose_display_subject(
    title: str,
    town: str,
    html: str,
    override: str | None = None,
) -> tuple[str, str]:
    if override and override.strip():
        return override.strip(), "from --subject"
    stripped = title.strip()
    if is_town_subject_title(stripped):
        return stripped, "from title"
    if is_old_style_title(stripped):
        from_title = derive_subject_from_title(stripped, TOWNS[town])
        if from_title:
            return from_title, "from title"
        headline = extract_headline_from_html(html)
        if headline:
            return headline, "from first story headline"
        return f"{TOWNS[town]} edition", "fallback"
    return stripped, "from title"


def is_tracking_img(tag: str) -> bool:
    width = re.search(r"""\bwidth\s*=\s*["']?(\d+)""", tag, re.I)
    height = re.search(r"""\bheight\s*=\s*["']?(\d+)""", tag, re.I)
    style_w = re.search(r"width\s:\s*1(?:px)?\b", tag, re.I)
    style_h = re.search(r"height\s:\s*1(?:px)?\b", tag, re.I)
    if width and height and width.group(1) == "1" and height.group(1) == "1":
        return True
    if style_w and style_h:
        return True
    src = re.search(r"""\bsrc\s*=\s*["']([^"']+)""", tag, re.I)
    if src and TRACK_SRC.search(src.group(1)):
        return True
    return False


def clean_email(raw: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    html = raw

    if BUTTONDOWN_COMMENT.search(html):
        html = BUTTONDOWN_COMMENT.sub("", html)
        notes.append(
            "stripped Buttondown HTML comments (editor-mode / product notes; not visible)"
        )

    stripped: list[str] = []

    def replace_p(match: re.Match[str]) -> str:
        block = match.group(0)
        text = visible_text(block)
        kind = None
        if TEST_BANNER_TEXT.match(text):
            kind = "test-banner"
        elif UNSUB_TEMPLATE.search(block) or (
            UNSUB_HREF.search(block) and UNSUB_TEXT.match(text)
        ):
            kind = "unsubscribe"
        elif POWERED_TEXT.match(text):
            kind = "powered-by"
        elif LOGIN_TEXT.match(text):
            kind = "login"
        elif UNSUB_TEXT.match(text) and re.search(
            r"unsubscribe|preferences|manage", block, re.I
        ):
            kind = "unsubscribe"
        if kind:
            stripped.append(kind)
            return ""
        return block

    html = P_TAG.sub(replace_p, html)

    if BUTTONDOWN_LINK.search(html):
        html = BUTTONDOWN_LINK.sub("", html)
        stripped.append("buttondown-link")

    pixels: list[str] = []

    def replace_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        if is_tracking_img(tag):
            pixels.append(tag)
            return ""
        return tag

    html = IMG_TAG.sub(replace_img, html)
    if pixels:
        notes.append(f"stripped {len(pixels)} tracking pixel(s)")
    else:
        notes.append("no tracking pixels found")

    leftovers = TEMPLATE_TAG.findall(html)
    if leftovers:
        html = TEMPLATE_TAG.sub("", html)
        notes.append(f"stripped {len(leftovers)} leftover template tag(s)")

    labels = {
        "test-banner": (
            "stripped the distinct testing banner "
            '("Still in testing, please do not forward.")'
        ),
        "unsubscribe": "stripped unsubscribe / update-preferences paragraph",
        "powered-by": "stripped a Powered by Buttondown element",
        "login": "stripped a Buttondown login / sign-in element",
        "buttondown-link": "stripped Buttondown.com branding link(s)",
    }
    seen: set[str] = set()
    for kind in stripped:
        if kind not in seen:
            notes.append(labels[kind])
            seen.add(kind)
    if not {"powered-by", "login", "buttondown-link"} & seen:
        notes.append(
            "no Buttondown bar, powered-by, or login elements found in the email HTML"
        )

    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip() + "\n", notes


def wrap_email_document(fragment: str, title: str) -> str:
    styles = STYLE_TAG.findall(fragment)
    metas = [m for m in META_TAG.findall(fragment) if not re.search(r"charset=", m, re.I)]
    rest = fragment
    for block in styles:
        rest = rest.replace(block, "", 1)
    for block in metas:
        rest = rest.replace(block, "", 1)
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{html_lib.escape(title)}</title>",
        *metas,
        *styles,
        "<style>html,body{margin:0;padding:0;background:#f3efe6;}</style>",
        "</head>",
        "<body>",
        rest.strip(),
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def extract_title(raw: str) -> str | None:
    match = TITLE_TAG.search(raw)
    if not match:
        return None
    title = visible_text(match.group(1))
    return title or None


def resolve_source(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Source not found: {path}")
    if path.is_file():
        if path.suffix.lower() != ".html":
            raise SystemExit(f"Source must be an HTML file, not {path.name}")
        return path
    html_files = sorted(
        item for item in path.iterdir() if item.is_file() and item.suffix.lower() == ".html"
    )
    if not html_files:
        raise SystemExit(f"No HTML files in {path}")
    named = [item for item in html_files if item.name.startswith("em_")]
    candidates = named or html_files
    if len(candidates) > 1:
        names = ", ".join(item.name for item in candidates)
        raise SystemExit(f"Multiple HTML files in {path}: {names}")
    return candidates[0]


def load_manifest() -> list[dict]:
    if not MANIFEST.exists():
        return []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    raw_issues = data.get("issues", data if isinstance(data, list) else [])
    issues = []
    for item in raw_issues:
        if not isinstance(item, dict):
            continue
        town = item.get("town")
        send_date = item.get("date")
        title = item.get("title")
        if town in TOWNS and send_date and title:
            entry = {"town": town, "date": send_date, "title": title}
            display = item.get("display_subject")
            if display:
                entry["display_subject"] = display
            issues.append(entry)
    return issues


def save_manifest(issues: list[dict]) -> None:
    ordered = sorted(
        issues,
        key=lambda item: (
            TOWN_ORDER.index(item["town"]) if item["town"] in TOWN_ORDER else 99,
            item["date"],
        ),
    )
    MANIFEST.write_text(
        json.dumps({"issues": ordered}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def upsert_issue(
    issues: list[dict],
    town: str,
    send_date: str,
    title: str,
    display_subject: str,
) -> list[dict]:
    kept = [
        item
        for item in issues
        if not (item["town"] == town and item["date"] == send_date)
    ]
    kept.append(
        {
            "town": town,
            "date": send_date,
            "title": title,
            "display_subject": display_subject,
        }
    )
    return kept


def render_index(issues: list[dict]) -> str:
    by_town = {slug: [] for slug in TOWN_ORDER}
    for item in issues:
        if item["town"] in by_town:
            by_town[item["town"]].append(item)
    for slug in by_town:
        by_town[slug].sort(key=lambda item: item["date"], reverse=True)

    sections: list[str] = []
    for slug in TOWN_ORDER:
        sections.append(f"    <h2>{html_lib.escape(TOWNS[slug])}</h2>")
        items = by_town[slug]
        if not items:
            sections.append('    <p class="archive-empty">No issues yet.</p>')
            continue
        sections.append('    <ul class="archive-list">')
        for item in items:
            parsed = date.fromisoformat(item["date"])
            when = format_list_date(parsed)
            href = f"/archive/{slug}/{item['date']}/"
            subject = item.get("display_subject") or derive_subject_from_title(
                item["title"], TOWNS[slug]
            ) or f"{TOWNS[slug]} edition"
            subject = html_lib.escape(subject)
            sections.append(
                f'      <li>'
                f'<time datetime="{item["date"]}">{when}</time>'
                f'<a href="{href}">{subject}</a></li>'
            )
        sections.append("    </ul>")

    head = CHROME_HEAD.format(
        title="Archive · The Maine Ledger",
        og_title="Archive · The Maine Ledger",
        description="Sent editions of The Maine Ledger, arranged by town.",
        canonical="https://themaineledger.com/archive/",
    )
    return (
        head
        + """<main class="w">
  <article class="page">
    <p class="kicker">Archive</p>
    <h1>Past issues</h1>
    <p class="lede">Sent editions of The Maine Ledger, arranged by town.</p>
"""
        + "\n".join(sections)
        + """
  </article>
</main>
"""
        + CHROME_FOOT
    )


def render_issue_page(
    town: str, send_date: date, title: str, display_subject: str
) -> str:
    town_label = TOWNS[town]
    long_date = f"{MONTHS_LONG[send_date.month]} {send_date.day}, {send_date.year}"
    description = html_lib.escape(f"The {town_label} edition sent {long_date}.")
    escaped_subject = html_lib.escape(display_subject)
    page_title = html_lib.escape(f"{display_subject} · The Maine Ledger")
    when = format_list_date(send_date)
    canonical = f"https://themaineledger.com/archive/{town}/{send_date.isoformat()}/"
    head = CHROME_HEAD.format(
        title=page_title,
        og_title=page_title,
        description=description,
        canonical=canonical,
    )
    return (
        head
        + f"""<main class="w issue-shell">
  <p class="back"><a href="/archive/">Back to the archive</a></p>
  <header class="issue-head">
    <time datetime="{send_date.isoformat()}">{when}</time>
    <h1>{escaped_subject}</h1>
  </header>
  <iframe class="issue-frame" id="issue-frame" src="body.html" title="{escaped_subject}" scrolling="no" frameborder="0" style="display:block;width:100%;max-width:600px;margin:0 auto;border:0;overflow:hidden;"></iframe>
</main>
<script>
(function(){{
  var frame = document.getElementById('issue-frame');
  if (!frame) return;
  function fit(){{
    try{{
      var doc = frame.contentDocument;
      if (!doc) return;
      var h = Math.max(
        doc.documentElement ? doc.documentElement.scrollHeight : 0,
        doc.body ? doc.body.scrollHeight : 0
      );
      if (h) frame.style.height = h + 'px';
    }}catch (e){{}}
  }}
  function bind(){{
    fit();
    try{{
      var doc = frame.contentDocument;
      if (!doc) return;
      var imgs = doc.getElementsByTagName('img');
      for (var i = 0; i < imgs.length; i++) imgs[i].addEventListener('load', fit);
    }}catch (e){{}}
    setTimeout(fit, 200);
    setTimeout(fit, 800);
    setTimeout(fit, 2000);
  }}
  frame.addEventListener('load', bind);
  try{{
    if (frame.contentDocument && frame.contentDocument.readyState === 'complete') bind();
  }}catch (e){{}}
  window.addEventListener('resize', fit);
}})();
</script>
"""
        + CHROME_FOOT
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish a sent issue into the self-hosted /archive/."
    )
    parser.add_argument("source", help="Issue HTML file, or a directory containing one")
    parser.add_argument("town", help="Town slug: " + ", ".join(TOWN_ORDER))
    parser.add_argument("date", help="Send date YYYY-MM-DD")
    parser.add_argument(
        "--title",
        help="Issue title (email subject). Required if the HTML has no title.",
    )
    parser.add_argument(
        "--subject",
        help="Display subject for the archive listing. If omitted, derived from the title or the first story headline.",
    )
    args = parser.parse_args(argv)

    town = args.town.lower().strip()
    if town not in TOWNS:
        raise SystemExit(
            f"Unknown town {args.town!r}. Use one of: {', '.join(TOWN_ORDER)}"
        )
    try:
        send_date = date.fromisoformat(args.date)
    except ValueError:
        raise SystemExit(f"Date must be YYYY-MM-DD, got {args.date!r}") from None

    source = resolve_source(Path(args.source))
    raw = source.read_text(encoding="utf-8")
    title = args.title.strip() if args.title else extract_title(raw)
    if not title:
        raise SystemExit(
            "No title found in the HTML; pass --title with the email subject."
        )

    cleaned, notes = clean_email(raw)
    display_subject, subject_source = choose_display_subject(
        title, town, raw, args.subject
    )
    dest_dir = ARCHIVE / town / send_date.isoformat()
    dest_dir.mkdir(parents=True, exist_ok=True)
    body_path = dest_dir / "body.html"
    page_path = dest_dir / "index.html"
    body_path.write_text(wrap_email_document(cleaned, title), encoding="utf-8")
    page_path.write_text(
        render_issue_page(town, send_date, title, display_subject), encoding="utf-8"
    )

    issues = upsert_issue(
        load_manifest(), town, send_date.isoformat(), title, display_subject
    )
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    save_manifest(issues)
    index_path = ARCHIVE / "index.html"
    index_path.write_text(render_index(issues), encoding="utf-8")

    def rel(path: Path) -> Path:
        return path.resolve().relative_to(ROOT)

    print(f"Wrote {rel(body_path)}")
    print(f"Wrote {rel(page_path)}")
    print(f"Updated {rel(MANIFEST)}")
    print(f"Wrote {rel(index_path)}")
    print(f"Display subject: {display_subject} ({subject_source})")
    for note in notes:
        print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
