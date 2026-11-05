# The Maine Ledger — web

Static site served by GitHub Pages from `main` (`/`) at https://themaineledger.com (`CNAME`).

**Publishing rule:** Ben explicitly approved making the Brunswick Edition live (Nov 5, 2026, 1:47 PM ET). That approval covered that release only (Ben separately approved the follow-up that removed the sample section); every future commit/push/deploy still needs Ben's explicit approval.

## Files
- `index.html` — **live homepage**: the Brunswick Edition page (formerly the local concept `statewide-map.html`).
- `coastal-map.html` + `map.jpg` — previous coastal (Midcoast) homepage, kept byte-for-byte as a separate unlinked preview. Do not edit or delete.
- Regeneration sources live outside the repo in `/workspace/statewide-map-build/` (`gen.py` → `build.py` → `assemble.py` writes `index.html`; template `tpl.html`; tests `test.py`, screenshots `final.py`/`zoom.py`).

## Current decisions (index.html)
- Beta notice: exactly one, at the top: “Still in beta — not ready for the public yet, but email signup still works.”
- Masthead: “The Maine Ledger” in Source Serif 4 (modern, classy, authoritative); “Brunswick Edition” as a small, centered, letterspaced edition line directly beneath the nameplate (hairlines either side); the date sits alone in the ruled date line.
- Layout: newspaper rules, minimal words, no card UI. Mobile: signup before the map.
- Signup: Brunswick only. Same Buttondown form and tag behavior as the coastal page (`zip-04011` default; `?src=flyer` → `flyer` unless `?zip=04011`). Never test-submit the real form.
- Tagline (all widths) exactly: “Town business & good news from Brunswick.”
- “Current edition” section directly below signup with “Read the current edition” shown underlined but not a link (no href, no click behavior, no pointer cursor).
- Map: accurate Maine outline plus the actual Brunswick town boundary (U.S. Census Bureau 2023 cartographic boundary files: state/county `500k`, county subdivision `cb_2023_23_cousub_500k`, “Brunswick town”, Cumberland County, GEOID 2300508430; public domain). Calm sage fill, restrained palette, enlargement inset. No other towns, no fake trees/compass/waves, no rings or animation.
- Above the fold only: beta notice, masthead, signup, Current edition link, map, short footer. No sample newsletter section.

## Superseded (do not reinstate)
- “Read the current edition →” as a link to the Buttondown archive → underlined, non-clickable text at Ben’s request.
- Blurred “Sample only.” newsletter frame below the fold → removed at Ben’s request (Nov 5, 2026, after launch).
- Local-only / no-push rule for the Brunswick page → superseded by Ben's approval to go live (future pushes still need approval).
- Coastal page as `index.html` → moved to `coastal-map.html`; Brunswick Edition is the homepage.
- Portland and Bangor shown as disabled/grayed areas → removed at Ben's request; show Brunswick only.
- Region radio picker, area cards, “By Region”/“Statewide”/“Brunswick Edition” title → removed.
- Red “blast radius” rings / pulsing animation, soft illustrative blob → replaced by the actual town boundary.
- Separate desktop tagline (“Town hall, schools, housing and business. Free, daily.”) and mobile-only tagline → one tagline at all widths.
- “Brunswick edition” inside the date line → moved under the nameplate.
- Beta line without the signup clause → now ends “…, but email signup still works.”
- Blackletter nameplate, beta box beside masthead, second Notice box → removed.
- Vintage illustration (pine trees, compass rose, wave hatching) → replaced by restrained cartography.
