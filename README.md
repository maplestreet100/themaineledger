# The Maine Ledger — web

Static site served by GitHub Pages from `main` (`/`) at https://themaineledger.com (`CNAME`).

**Publishing rule:** Ben explicitly approved making the Brunswick Edition live (Nov 5, 2026, 1:47 PM ET). That approval covered that release only (Ben separately approved the follow-up that removed the sample section); every future commit/push/deploy still needs Ben's explicit approval.

## Files
- `index.html` — **live homepage**: the Statewide Edition page (was the Brunswick Edition until Nov 19, 2026; formerly the local concept `statewide-map.html`).
- Regeneration sources live outside the repo in `/workspace/statewide-map-build/` (`gen.py` → `build.py` → `assemble.py` writes `index.html`; template `tpl.html`; tests `test.py`, screenshots `final.py`/`zoom.py`).

## Current decisions (index.html)
- Beta notice: exactly one, at the top: “Now in beta. Full launch in December.” (Ben, Nov 17 2026)
- Masthead: “The Maine Ledger” in Source Serif 4 (modern, classy, authoritative); “Statewide Edition” as a small, centered, letterspaced edition line directly beneath the nameplate (hairlines either side); the date sits alone in the ruled date line.
- Layout: newspaper rules, minimal words, no card UI. Mobile: signup before the map.
- Signup: statewide. Buttondown embed form sends the email only, no tag (Nov 19, 2026). Never test-submit the real form.
- Signup heading: “Maine, every Friday morning.” Deck: “Business, development and real estate across Maine.”
- “Current edition” section directly below signup with “Read the current edition” shown underlined but not a link (no href, no click behavior, no pointer cursor).
- Map: accurate Maine outline with county lines (U.S. Census Bureau 2023 cartographic boundary files, state/county `500k`; public domain), Gulf of Maine label, scale and north mark. Caption: “Maine. Map: U.S. Census Bureau.” No town shading, pins or inset. Never OSM outlines or `map.jpg`.
- Above the fold only: beta notice, masthead, signup, Current edition link, map, short footer. No sample newsletter section.

## Superseded (do not reinstate)
- Brunswick Edition masthead, Brunswick tagline and deck, Brunswick town shading, pin and enlargement inset → replaced by the statewide edition (Ben, Nov 19, 2026). Past Brunswick issues stay in the archive with their “Brunswick: ” prefix.
- “Read the current edition →” as a link to the Buttondown archive → underlined, non-clickable text at Ben’s request.
- Blurred “Sample only.” newsletter frame below the fold → removed at Ben’s request (Nov 5, 2026, after launch).
- Local-only / no-push rule for the Brunswick page → superseded by Ben's approval to go live (future pushes still need approval).
- Coastal page (`coastal-map.html` + `map.jpg`) → removed from the site at Ben's request (Nov 14, 2026).
- Portland and Bangor shown as disabled/grayed areas → removed at Ben's request; show Brunswick only.
- Region radio picker, area cards, “By Region” title → removed. (A big “Statewide”/“Brunswick Edition” title was also removed; the small edition line now reads “Statewide Edition”.)
- Red “blast radius” rings / pulsing animation, soft illustrative blob → replaced by the actual town boundary.
- Separate desktop tagline (“Town hall, schools, housing and business. Free, daily.”) and mobile-only tagline → one tagline at all widths.
- “Brunswick edition” inside the date line → moved under the nameplate.
- Beta line ending “…, but email signup still works.” → clause removed at Ben’s request; notice is back to “Still in beta — not ready for the public yet.”
- Blackletter nameplate, beta box beside masthead, second Notice box → removed.
- Vintage illustration (pine trees, compass rose, wave hatching) → replaced by restrained cartography.
