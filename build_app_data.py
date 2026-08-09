"""Build assets/data.js for the Delta Hunting Season web app.

Reads the four hunt CSVs in data/, enriches each hunt with moon phase, rut
window, drive time from camp, and a composite score, then writes a single
JavaScript module the static site loads directly (no fetch, so it works from
file:// as well as GitHub Pages).

Run:  python build_app_data.py
"""

from __future__ import annotations

import csv
import json
import os
import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "assets" / "data.js"

# --------------------------------------------------------------------------
# Camp + WMA geography
# --------------------------------------------------------------------------
# Camp: 1149 Watertower Rd, Bentonia, MS 39040 (Yazoo County).
CAMP = {
    "label": "Camp — 1149 Watertower Rd, Bentonia, MS",
    "lat": 32.6455,
    "lon": -90.3820,
}

# WMA access points. Coordinates are the public entrance / permit station area,
# not the property centroid — that is what actually matters for drive time.
# Sources: MDWFP WMA pages (county + directions from nearest highway).
WMAS = {
    "Mahannah": {
        "lat": 32.5750, "lon": -90.8600,
        "county": "Warren / Issaquena",
        "access": "~18 mi N of Vicksburg on Hwy 61, west at WMA sign on Floweree Rd",
    },
    "Phil Bryant (Backwoods Unit)": {
        "lat": 32.6100, "lon": -90.9300,
        "county": "Warren / Issaquena",
        "access": "Floweree Rd to Anderson-Tully Rd, ~6 mi to Backwoods Unit 1 campsite",
    },
    "Phil Bryant (Buck Bayou Unit)": {
        "lat": 32.6400, "lon": -90.9100,
        "county": "Warren / Issaquena",
        "access": "Floweree Rd to Anderson-Tully Rd",
    },
    "Phil Bryant (Ten Point Unit)": {
        "lat": 32.5950, "lon": -90.9000,
        "county": "Warren / Issaquena",
        "access": "~18 mi N of Vicksburg on Hwy 61, west on Floweree Rd",
    },
    "Phil Bryant (Goose Lake Unit)": {
        "lat": 32.6600, "lon": -90.9500,
        "county": "Warren / Issaquena",
        "access": "Largest portion is boat-access only — no roads or public easements",
    },
    "Twin Oaks": {
        "lat": 32.8700, "lon": -90.8500,
        "county": "Sharkey",
        "access": "~2 mi S of Rolling Fork on Hwy 61, east on Fork Creek Rd",
    },
    "Sky Lake": {
        "lat": 33.2400, "lon": -90.4400,
        "county": "Humphreys / Leflore",
        "access": "~8 mi N of Belzoni on Hwy 7, left on Four Mile Rd ~3 mi to permit station",
    },
    "Riverfront": {
        "lat": 33.8500, "lon": -91.0300,
        "county": "Bolivar",
        "access": "Batture land between the Mississippi River and the mainline levee, near Rosedale",
    },
    "Calling Panther": {
        "lat": 31.9900, "lon": -90.4400,
        "county": "Copiah",
        "access": "~5 mi W of Crystal Springs off New Zion Rd",
    },
    "Yockanookany": {
        "lat": 33.0600, "lon": -89.4000,
        "county": "Attala",
        "access": "Hwy 12 east from Kosciusko ~11.2 mi to WMA entrance on the right, near McCool",
    },
    "Canemount": {
        "lat": 31.9300, "lon": -91.1300,
        "county": "Claiborne",
        "access": "Hwy 552 west from Hwy 61, then north past Alcorn State ~3.8 mi to check station",
    },
    "Natchez State Park": {
        "lat": 31.6350, "lon": -91.2400,
        "county": "Adams",
        "access": "~10 mi N of Natchez off US-61 at Stanton",
    },
    "Alligator": {
        "lat": 34.1000, "lon": -90.7800,
        "county": "Bolivar / Coahoma",
        "access": "New in 2026 — bottomland hardwood near the town of Alligator; archery and permit PW only",
    },
    "Charles Ray Nix": {
        "lat": 34.4400, "lon": -89.8000,
        "county": "Panola",
        "access": "Near Sardis Lake, north Mississippi hills",
    },
    "Cossar State Park": {
        "lat": 34.1400, "lon": -89.8900,
        "county": "Yalobusha",
        "access": "George P. Cossar State Park on Enid Lake, near Oakland",
    },
    "Black Prairie": {
        "lat": 33.3100, "lon": -88.6400,
        "county": "Lowndes",
        "access": "Black Prairie belt near Crawford, east Mississippi",
    },
    "Hell Creek": {
        "lat": 34.8500, "lon": -88.9000,
        "county": "Tippah",
        "access": "Far north Mississippi, near Walnut",
    },
    "Tuscumbia": {
        "lat": 34.8800, "lon": -88.5800,
        "county": "Alcorn",
        "access": "Harvey Moss at Tuscumbia, near Corinth",
    },
    "Pascagoula River (LBTC Unit)": {
        "lat": 30.7500, "lon": -88.6300,
        "county": "Jackson / George",
        "access": "Lower Pascagoula River bottom, coastal Mississippi",
    },
    "Muscadine Farms": {
        "lat": 33.2200, "lon": -90.9700,
        "county": "Washington",
        "access": "Hwy 12/61 at Hollandale, N 3.5 mi to Avon Darlove Rd, W 7.6 mi to Muscadine Rd",
    },
    # --- Theodore Roosevelt NWR Complex (USFWS, separate lottery) ---
    "Panther Swamp NWR": {
        "lat": 32.8400, "lon": -90.5500,
        "county": "Yazoo / Humphreys",
        "access": "South on River Rd from Hwy 49W west of Yazoo City, 7 mi, right at Gumbo Acres sign",
    },
    "Yazoo NWR": {
        "lat": 33.0900, "lon": -90.9200,
        "county": "Washington",
        "access": "595 Yazoo Refuge Rd, Hollandale — ~25 mi S of Greenville",
    },
}

# Our applications this season, by exact hunt_name. "applied" is confirmed and
# paid for; "planned" is still intent. Both are flagged in the app and checked
# against each other for date overlap.
# The application log lives in applications_local.py, which is gitignored — it
# carries hunter names, Group IDs, and transaction numbers. Set PUBLIC_BUILD=1
# to omit the plan layer entirely when building the version that gets pushed.
APPLICATIONS = []
if not os.environ.get("PUBLIC_BUILD"):
    try:
        from applications_local import APPLICATIONS
    except ImportError:
        pass

# Delta backroads wander; straight-line distance badly understates the drive.
ROAD_FACTOR = 1.45      # driven miles per straight-line mile
AVG_MPH = 47.0          # blended highway + county road speed
ACCESS_MINUTES = 10     # gravel WMA access road / permit station


def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def drive_estimate(geo):
    """Estimated (miles, minutes) from camp.

    The model is tuned for Delta county roads and overestimates routes that run
    mostly on interstate. Measure a route in Maps and set `drive_minutes` on the
    WMA entry to pin the real number; the estimate is then ignored.
    """
    straight = haversine_miles(CAMP["lat"], CAMP["lon"], geo["lat"], geo["lon"])
    miles = straight * ROAD_FACTOR
    minutes = miles / AVG_MPH * 60 + ACCESS_MINUTES
    return round(miles, 1), int(round(geo.get("drive_minutes", minutes)))


# --------------------------------------------------------------------------
# Moon
# --------------------------------------------------------------------------
SYNODIC = 29.530588853
NEW_MOON_EPOCH = datetime(2000, 1, 6, 18, 14)


def moon_age(d: date) -> float:
    """Days since the most recent new moon (0 = new, ~14.8 = full)."""
    delta = datetime(d.year, d.month, d.day, 12) - NEW_MOON_EPOCH
    return (delta.total_seconds() / 86400.0) % SYNODIC


def moon_phase_name(age: float) -> str:
    if age < 1.85 or age >= 27.68:
        return "New Moon"
    if age < 5.54:
        return "Waxing Crescent"
    if age < 9.23:
        return "First Quarter"
    if age < 12.91:
        return "Waxing Gibbous"
    if age < 16.61:
        return "Full Moon"
    if age < 20.30:
        return "Waning Gibbous"
    if age < 23.99:
        return "Last Quarter"
    return "Waning Crescent"


def moon_illumination(age: float) -> float:
    return round((1 - math.cos(2 * math.pi * age / SYNODIC)) / 2, 3)


def moon_score(age: float) -> float:
    """0-10. Deer move best around the new moon (dark nights push daylight
    feeding) and secondarily around the full moon (midday movement)."""
    dist_new = min(age, SYNODIC - age)
    dist_full = abs(age - SYNODIC / 2)
    if dist_new <= 3:
        return 10.0 - (dist_new / 3) * 1.5      # 10.0 -> 8.5
    if dist_full <= 3:
        return 8.0 - (dist_full / 3) * 1.5      # 8.0 -> 6.5
    return 5.5


# --------------------------------------------------------------------------
# Rut (South Delta / Mississippi Delta region timing)
# --------------------------------------------------------------------------
# Windows are (month, day) pairs anchored to the season's opening calendar year,
# so the same model applies to whichever season's CSVs are dropped into data/.
# `+1` marks a date that falls in the following calendar year.
RUT_WINDOW_TEMPLATE = [
    ((12, 26), (1, 8, "+1"), 10.0, "Peak Rut",
     "Peak breeding — bucks on their feet all day"),
    ((12, 10), (12, 25), 8.5, "Pre-Rut Chase",
     "Chase phase ramping up, scrapes hot"),
    ((1, 9, "+1"), (1, 22, "+1"), 7.5, "Post-Rut",
     "Second estrus and hungry, recovering bucks"),
    ((11, 15), (12, 9), 7.0, "Early Rut Build",
     "Rubs and scrapes appearing, movement climbing"),
    ((11, 1), (11, 14), 6.0, "Pre-Rut",
     "Bachelor groups breaking up"),
    ((10, 1), (10, 31), 5.0, "Early Season",
     "Food-source pattern hunting"),
]

_rut_windows: list = []


def build_rut_windows(season_year: int):
    """Materialize RUT_WINDOW_TEMPLATE against the season's opening year."""
    out = []
    for start, end, score, label, note in RUT_WINDOW_TEMPLATE:
        def resolve(spec):
            month, day = spec[0], spec[1]
            year = season_year + 1 if len(spec) > 2 else season_year
            return date(year, month, day)
        out.append((resolve(start), resolve(end), score, label, note))
    return out


def rut_info(d: date):
    for start, end, score, label, note in _rut_windows:
        if start <= d <= end:
            return score, label, note
    return 4.5, "Late Season", "Food-driven movement, pressured deer"


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
WEIGHTS = {"rut": 0.40, "moon": 0.25, "season": 0.15, "permits": 0.10, "duration": 0.10}


def season_score(d: date) -> float:
    """Cold-front probability / weather quality by month."""
    return {12: 10.0, 1: 9.0, 11: 7.5, 10: 5.0, 2: 6.5}.get(d.month, 5.0)


def permit_score(permits: int | None) -> float:
    # More permits = better draw odds. 24 is the largest offering in the data.
    # Refuge lotteries don't publish quotas — score those neutrally rather than
    # guessing, and let the UI say the quota is unpublished.
    if permits is None:
        return 5.0
    return min(10.0, 3.0 + permits / 24 * 7.0)


def duration_score(days: int) -> float:
    return min(10.0, 4.0 + (days - 1) * 1.5)


def build_hunt(row: dict) -> dict:
    start = datetime.strptime(row["start_date"], "%Y-%m-%d").date()
    end = datetime.strptime(row["end_date"], "%Y-%m-%d").date()
    permits = int(row["permits_available"]) if row.get("permits_available") else None
    days = int(row["duration_days"])
    group_size = int(row["group_size"]) if row.get("group_size") else None

    # How many people can go in on one application. MDWFP caps the individual
    # deer draws at 2 and the Group draw at its group size; the refuge lotteries
    # publish their own cap per hunt.
    if row.get("max_party"):
        max_party = int(row["max_party"])
    elif group_size:
        max_party = group_size
    else:
        max_party = 2

    # Score the hunt on its best single day rather than only the opener.
    best = None
    for i in range(days):
        d = start + timedelta(days=i)
        age = moon_age(d)
        r_score, r_label, r_note = rut_info(d)
        combined = r_score * WEIGHTS["rut"] + moon_score(age) * WEIGHTS["moon"]
        if best is None or combined > best[0]:
            best = (combined, d, age, r_score, r_label, r_note)
    _, best_day, age, r_score, r_label, r_note = best

    m_score = moon_score(age)
    s_score = season_score(best_day)
    p_score = permit_score(permits)
    d_score = duration_score(days)
    total = (
        r_score * WEIGHTS["rut"]
        + m_score * WEIGHTS["moon"]
        + s_score * WEIGHTS["season"]
        + p_score * WEIGHTS["permits"]
        + d_score * WEIGHTS["duration"]
    )

    # Rut timing is meaningless for waterfowl, so non-deer hunts carry no
    # composite score rather than a fabricated one.
    species = row.get("species") or "Deer"
    if species != "Deer":
        r_score = m_score = s_score = p_score = d_score = None
        r_label = r_note = ""
        total = None

    wma = row["wma_location"]
    geo = WMAS.get(wma)
    if geo is None:
        raise SystemExit(f"No coordinates recorded for WMA: {wma!r}")
    miles, minutes = drive_estimate(geo)

    return {
        "id": row["hunt_name"].lower().replace(" ", "-").replace("(", "").replace(")", ""),
        "name": row["hunt_name"],
        "type": row["hunt_type"],
        "species": species,
        "wma": wma,
        "county": geo["county"],
        "start": row["start_date"],
        "end": row["end_date"],
        "days": days,
        "permits": permits,
        "groupSize": group_size,
        "agency": row.get("agency") or "MDWFP",
        "maxParty": max_party,
        "restriction": row.get("restriction") or "",
        "notes": row.get("notes") or "",
        "driveMinutes": minutes,
        "driveMiles": miles,
        "bestDay": best_day.isoformat(),
        "moonPhase": moon_phase_name(age),
        "moonIllum": moon_illumination(age),
        "rutPhase": r_label,
        "rutNote": r_note,
        "scores": None if total is None else {
            "rut": round(r_score, 2),
            "moon": round(m_score, 2),
            "season": round(s_score, 2),
            "permits": round(p_score, 2),
            "duration": round(d_score, 2),
        },
        "score": None if total is None else round(total, 2),
    }


def discover_csvs():
    """Use the newest season present in data/, so last year's CSVs can stay on
    disk for reference without being picked up."""
    found = sorted(p for pat in ("deer_*hunts_*.csv", "refuge_hunts_*.csv",
                                 "waterfowl_hunts_*.csv")
                   for p in DATA_DIR.glob(pat))
    if not found:
        return []
    seasons = {m.group(1) for p in found if (m := re.search(r"_(\d{4}_\d{2})\.csv$", p.name))}
    if not seasons:
        return found
    newest = max(seasons)
    return [p for p in found if p.name.endswith(f"_{newest}.csv")]


def main():
    global _rut_windows

    paths = discover_csvs()
    if not paths:
        raise SystemExit(f"No hunt CSVs found in {DATA_DIR}")

    rows = []
    for path in paths:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            rows.extend(r for r in csv.DictReader(fh) if r.get("hunt_name"))

    # A season opens in the summer, so anything before July belongs to the
    # season that started the previous calendar year.
    earliest = min(datetime.strptime(r["start_date"], "%Y-%m-%d").date() for r in rows)
    season_year = earliest.year if earliest.month >= 7 else earliest.year - 1
    _rut_windows = build_rut_windows(season_year)
    season_label = f"{season_year}-{str(season_year + 1)[-2:]}"

    hunts = [build_hunt(r) for r in rows]

    by_name = {h["name"]: h for h in hunts}
    missing = [a["hunt"] for a in APPLICATIONS if a["hunt"] not in by_name]
    if missing:
        raise SystemExit("APPLICATIONS names not found in the data: " + ", ".join(missing))

    planned = []
    for app in APPLICATIONS:
        h = by_name[app["hunt"]]
        h["planned"] = True
        h["status"] = app["status"]
        h["hunters"] = app["hunters"]
        h["ref"] = app["ref"]
        h["todo"] = app.get("todo", "")
        h["groupId"] = app.get("groupId", "")
        h["transaction"] = app.get("transaction", "")
        planned.append(h)

    # Hunts you cannot physically attend both of. A shared hunter makes it worse:
    # the same person is committed to two places at once.
    for a in planned:
        clashes = []
        for b in planned:
            if b is a or not (a["start"] <= b["end"] and b["start"] <= a["end"]):
                continue
            shared = sorted(set(a["hunters"]) & set(b["hunters"]))
            clashes.append({"name": b["name"], "sharedHunters": shared})
        a["conflictsWith"] = clashes

    # TR Complex rule: "Applicants may apply for only one limited draw deer
    # hunt." Count each hunter's refuge applications so a violation is obvious.
    refuge_load = {}
    for h in planned:
        if h["agency"] != "USFWS":
            continue
        for who in h["hunters"]:
            refuge_load.setdefault(who, []).append(h["name"])
    over_limit = [
        {"hunter": who, "hunts": names}
        for who, names in sorted(refuge_load.items()) if len(names) > 1
    ]

    hunts.sort(key=lambda h: (h["score"] is None, -(h["score"] or 0), h["start"]))

    wmas = []
    for name, geo in WMAS.items():
        miles, minutes = drive_estimate(geo)
        wmas.append({
            "name": name,
            "county": geo["county"],
            "access": geo["access"],
            "lat": geo["lat"],
            "lon": geo["lon"],
            "driveMiles": miles,
            "driveMinutes": minutes,
            "hunts": sum(1 for h in hunts if h["wma"] == name),
        })
    wmas.sort(key=lambda w: w["driveMinutes"])

    peak = next(w for w in _rut_windows if w[3] == "Peak Rut")
    payload = {
        "season": season_label,
        "seasonYear": season_year,
        "generated": date.today().isoformat(),
        "sourceFiles": [p.name for p in paths],
        "peakRut": {"start": peak[0].isoformat(), "end": peak[1].isoformat()},
        "planned": [
            {"name": h["name"], "start": h["start"], "end": h["end"],
             "status": h["status"], "hunters": h["hunters"], "ref": h["ref"],
             "todo": h["todo"], "groupId": h["groupId"],
             "transaction": h["transaction"],
             "wma": h["wma"], "driveMinutes": h["driveMinutes"],
             "conflictsWith": h["conflictsWith"]}
            for h in sorted(planned, key=lambda h: h["start"])
        ],
        "refugeOverLimit": over_limit,
        "camp": CAMP,
        "driveModel": {
            "roadFactor": ROAD_FACTOR,
            "avgMph": AVG_MPH,
            "accessMinutes": ACCESS_MINUTES,
        },
        "weights": WEIGHTS,
        "wmas": wmas,
        "hunts": hunts,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "// Generated by build_app_data.py — do not edit by hand.\n"
        "window.HUNT_DATA = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} — season {season_label}, {len(hunts)} hunts across {len(wmas)} WMAs")
    print(f"  sources: {', '.join(p.name for p in paths)}")
    for w in wmas:
        flag = "within 1.5h" if w["driveMinutes"] <= 90 else "beyond 1.5h"
        print(f"  {w['name']:<32} {w['driveMinutes']:>4} min  ({flag})")


if __name__ == "__main__":
    main()
