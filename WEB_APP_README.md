# South Delta Szn — WMA Draw Planner

A static single-page app for picking Mississippi WMA deer draw hunts. No build
step, no dependencies, no server — open `index.html` or push to GitHub Pages.

```
index.html            page shell
assets/app.css        design system (dark default, light toggle)
assets/app.js         filtering, scoring display, calendar, shortlist, exports
assets/data.js        GENERATED — do not edit by hand
assets/hunters.js     hunter roster (mirrors hunters.csv)
parse_mdwfp_draws.py  MDWFP PDF tables -> data/*.csv
build_app_data.py     data/*.csv -> assets/data.js
data/raw/*.md         PDF tables as extracted, kept for re-parsing
```

Currently loaded: **2026-27**, 232 hunts across 19 WMAs.

## Refreshing for a new season

1. On the [MDWFP WMA Draw Hunts page](https://www.mdwfp.com/wildlife-hunting/wma-draw-hunts),
   grab the four deer PDFs (Archery, Gun, Primitive Weapon, Group). Extract each
   one's `Hunt | Dates | Quota` table to markdown and save it as
   `data/raw/<category>_<year>_<yy>.md` — e.g. `data/raw/archery_2027_28.md`.
   Categories: `archery`, `gun`, `primitive_weapon`, `group`.
2. Parse and build:
   ```powershell
   Push-Location "C:\Documents\GitHubCode\DeltaHuntingSeason"; python parse_mdwfp_draws.py 2027; python build_app_data.py; Pop-Location
   ```

That's it. The season label, rut windows, month filters, and calendar all derive
from the dates in the data — nothing in the app is pinned to a year, and
`build_app_data.py` always picks the newest season present in `data/`, so older
CSVs can stay on disk for reference.

**Check the parser's permit totals against the totals printed at the bottom of
each MDWFP PDF.** They matched exactly for 2026-27 (1548 / 610 / 1577), which is
the cheapest proof the tables came across intact.

If a CSV names a WMA that isn't in the `WMAS` table in `build_app_data.py`, the
build stops and tells you which one. Add its entrance coordinates and re-run.

The app shows a red **"Past season data"** banner whenever the loaded season has
already ended, so a stale build can't quietly pass for the current one.

## The 1.5-hour camp filter

Camp is **1149 Watertower Rd, Bentonia, MS**. Every WMA carries an estimated
drive time from there; the toggle in the header hides anything past the
threshold, and the slider moves it between 30 and 240 minutes. The setting
persists in the browser.

Drive time is estimated, not routed: straight-line distance from camp × 1.45
road factor at 47 mph, plus 10 minutes for gravel WMA access roads. All three
constants live at the top of `build_app_data.py`. Each hunt's detail panel has a
**Route it** link that opens the real drive in Google Maps — use that before you
commit to anything.

The model is tuned for Delta county roads and **overestimates routes that run
mostly on interstate**. To pin a real number, measure it in Maps and add
`"drive_minutes": 65` to that WMA's entry in the `WMAS` table; the estimate is
then ignored for that area.

At the default 90 minutes, 7 of 19 areas are in range — 127 of 232 hunts.

| WMA | Drive | Miles | |
|---|---|---|---|
| Mahannah | 1h 02m | 41.0 | ✅ |
| Phil Bryant (Ten Point Unit) | 1h 06m | 44.0 | ✅ |
| Phil Bryant (Buck Bayou Unit) | 1h 07m | 44.5 | ✅ |
| Twin Oaks | 1h 08m | 45.4 | ✅ |
| Phil Bryant (Backwoods Unit) | 1h 09m | 46.4 | ✅ |
| Phil Bryant (Goose Lake Unit) | 1h 11m | 47.9 | ✅ |
| Sky Lake | 1h 26m | 59.8 | ✅ |
| Calling Panther | 1h 34m | 65.8 | borderline — mostly I-55, likely closer |
| Yockanookany | 2h 08m | 92.6 | |
| Canemount | 2h 12m | 95.9 | |
| Natchez State Park | 2h 49m | 125.1 | |
| Riverfront | 2h 59m | 132.3 | |
| Alligator | 3h 21m | 149.7 | |
| Cossar State Park | 3h 28m | 155.4 | |
| Black Prairie | 3h 35m | 160.6 | |
| Charles Ray Nix | 4h 08m | 186.7 | |
| Pascagoula River (LBTC Unit) | 5h 18m | 241.2 | |
| Hell Creek | 5h 33m | 253.2 | |
| Tuscumbia | 5h 54m | 269.7 | |

## Scoring

Each hunt gets a 0–10 score. Multi-day hunts are scored on their **best** day,
not the opener.

| Factor | Weight | Basis |
|---|---|---|
| Rut | 40% | Delta-region timing — peak breeding Dec 26 – Jan 8, chase phase Dec 10 – Dec 25 |
| Moon | 25% | New moon scores highest; smaller bump near the full moon |
| Season | 15% | Cold-front probability by month (Dec > Jan > Nov > Oct) |
| Permits | 10% | Draw-odds proxy — more permits offered, better odds |
| Duration | 10% | Longer hunts give more chances |

Rut windows and weights are in `RUT_WINDOW_TEMPLATE` and `WEIGHTS` in
`build_app_data.py`. Change them there and re-run; the app reads the weights
from the generated data and redraws the "How hunts are scored" panel to match.

## Shortlist

Mississippi allows **5 deer draw choices**. Star hunts to build a shortlist —
it saves to the browser, warns past 5, and exports to `.ics` for your calendar.
The Hunts tab also exports whatever is currently filtered to CSV.

## Local preview

```powershell
Push-Location "C:\Documents\GitHubCode\DeltaHuntingSeason"; python -m http.server 8899; Pop-Location
```

Then open http://127.0.0.1:8899. Opening `index.html` directly from disk works
too — the data is a plain script, not a fetch.
