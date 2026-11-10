# Tools

## publish_issue.py

Publish a sent issue into the self-hosted archive at `/archive/`.

The script writes a cleaned copy of the email, a site-chrome wrapper page, updates `archive/issues.json`, and regenerates `archive/index.html`. It is idempotent: publishing the same town and date again replaces that issue.

It uses only the Python standard library. It never reads environment variables or API keys, and it never talks to Buttondown.

### Usage

```
python3 tools/publish_issue.py <issue.html or directory> <town> <yyyy-mm-dd> [--title "Issue title"] [--subject "Display subject"]
```

- `<issue.html or directory>`: path to the sent email HTML, or a directory that contains one `.html` file (or one `em_*.html` file). JSON sidecars in that directory are ignored.
- `<town>`: one of `brunswick`, `topsham`, `harpswell`, `bath`, `freeport`.
- `<yyyy-mm-dd>`: the real send date, not the usual edition weekday.
- `--title`: required if the HTML has no `<title>`. Use the email subject. This is stored as `title`.
- `--subject`: optional display subject for the archive listing and the issue page header. Stored as `display_subject`.

Examples:

```
python3 tools/publish_issue.py path/to/em_example.html freeport 2026-11-12 --title "Freeport: 52 new apartments planned"
python3 tools/publish_issue.py path/to/em_example.html brunswick 2026-11-10 --title "The Maine Ledger · Brunswick · Tue., Nov. 10" --subject "Brunswick: Data-center hearing set for Nov. 16"
```

### Display subjects

Each archive row shows the date first (`Tue., Nov. 10, 2026`), then the display subject as the link. The issue page keeps the back link, then uses the same date-then-subject pattern above the email. If a town heading already names the town, keep a `<Town>:` prefix on the subject anyway when that is the sent wording.

If `--subject` is not passed:

1. If the sent subject (`--title`) is already `<Town>: <top story>` (for example `Freeport: 52 new apartments planned`), use it as-is. Future sends use this syntax, usually under about 50 characters.
2. If the title is an older style such as `The Maine Ledger · ...`, strip the brand, town name, and any trailing weekday or date. If nothing meaningful remains, use the first story headline in the email HTML after the masthead (a real headline, not a date or section label). If no headline can be read reliably, use `<Town> edition`.

`--subject` always overrides. The script does not invent wording. The original email subject stays in `title`.

### What it strips

- Unsubscribe, update-preferences, and manage-subscription links, and the paragraph that holds them
- Leftover `{{ }}` and `{% %}` template tags
- 1x1 tracking pixels, if present
- Buttondown bars, "powered by" marks, and login or sign-in elements, if present
- A distinct testing banner whose only text is "Still in testing, please do not forward."

Editorial copy is left as sent. Images may stay on `assets.buttondown.email`.

### After each send

The daily build should export the sent email HTML and run this script with the town slug, the send date, and the sent subject as `--title`. Future subjects already look like `<Town>: <top story>`, so they become the listing text on their own. Pass `--subject` only when an older title needs a listing line. Then commit the updated `archive/` files with the rest of the site.

Do not pass API keys to this script. It only needs the exported HTML file.
