# Tools

## publish_issue.py

Publish a sent issue into the self-hosted archive at `/archive/`.

The script writes a cleaned copy of the email, a site-chrome wrapper page, updates `archive/issues.json`, and regenerates `archive/index.html`. It is idempotent: publishing the same town and date again replaces that issue.

It uses only the Python standard library. It never reads environment variables or API keys, and it never talks to Buttondown.

### Usage

```
python3 tools/publish_issue.py <issue.html or directory> <town> <yyyy-mm-dd> [--title "Issue title"]
```

- `<issue.html or directory>`: path to the sent email HTML, or a directory that contains one `.html` file (or one `em_*.html` file). JSON sidecars in that directory are ignored.
- `<town>`: one of `brunswick`, `topsham`, `harpswell`, `bath`, `freeport`.
- `<yyyy-mm-dd>`: the real send date, not the usual edition weekday.
- `--title`: required if the HTML has no `<title>`. Use the email subject.

Example:

```
python3 tools/publish_issue.py path/to/em_example.html brunswick 2026-11-10 --title "The Maine Ledger · Brunswick · Tue., Nov. 10"
```

### What it strips

- Unsubscribe, update-preferences, and manage-subscription links, and the paragraph that holds them
- Leftover `{{ }}` and `{% %}` template tags
- 1x1 tracking pixels, if present
- Buttondown bars, "powered by" marks, and login or sign-in elements, if present
- A distinct testing banner whose only text is "Still in testing, please do not forward."

Editorial copy is left as sent. Images may stay on `assets.buttondown.email`.

### After each send

The daily build should export the sent email HTML and run this script with the town slug, the send date, and the subject as `--title`. Then commit the updated `archive/` files with the rest of the site.

Do not pass API keys to this script. It only needs the exported HTML file.
