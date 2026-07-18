#!/usr/bin/env python3
"""
Parse official 2026-27 MDWFP deer draw hunt PDFs, score opportunities using
Yazoo-region rut timing, 2026-27 moon phases, and 2025 draw competition stats,
then emit CSVs + decision JSON for the web app.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_2026"
OUT_DATA = ROOT / "data"
OUT_REPORTS = ROOT / "reports"
WEB_DATA = ROOT / "web" / "data"

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

PDF_MAP = {
    "archery": ("archery_2026.pdf", "Deer Archery"),
    "gun": ("gun_2026.pdf", "Deer Gun"),
    "primitive_weapon": ("primitive_2026.pdf", "Deer Primitive Weapon"),
    "group": ("group_2026.pdf", "Deer Group"),
    "youth": ("youth_2026.pdf", "Deer Youth"),
    "senior": ("senior_2026.pdf", "Deer Senior"),
}

# Official major phases for the 2026-27 deer season window (UTC-adjacent calendar dates).
MOON_PHASES = [
    {"date": datetime(2026, 10, 3), "phase": "Last Quarter", "impact": 1},
    {"date": datetime(2026, 10, 10), "phase": "New", "impact": 3},
    {"date": datetime(2026, 10, 18), "phase": "First Quarter", "impact": 1},
    {"date": datetime(2026, 10, 26), "phase": "Full", "impact": -1},
    {"date": datetime(2026, 11, 1), "phase": "Last Quarter", "impact": 1},
    {"date": datetime(2026, 11, 9), "phase": "New", "impact": 3},
    {"date": datetime(2026, 11, 17), "phase": "First Quarter", "impact": 1},
    {"date": datetime(2026, 11, 24), "phase": "Full", "impact": -1},
    {"date": datetime(2026, 12, 1), "phase": "Last Quarter", "impact": 1},
    {"date": datetime(2026, 12, 9), "phase": "New", "impact": 3},
    {"date": datetime(2026, 12, 17), "phase": "First Quarter", "impact": 1},
    {"date": datetime(2026, 12, 24), "phase": "Full", "impact": -1},
    {"date": datetime(2026, 12, 30), "phase": "Last Quarter", "impact": 1},
    {"date": datetime(2027, 1, 7), "phase": "New", "impact": 3},
    {"date": datetime(2027, 1, 15), "phase": "First Quarter", "impact": 1},
    {"date": datetime(2027, 1, 22), "phase": "Full", "impact": -1},
    {"date": datetime(2027, 1, 29), "phase": "Last Quarter", "impact": 1},
]

# Yazoo County / Delta region biological window (same regional timing as prior analysis).
RUT_PERIODS = [
    {
        "id": "pre_rut",
        "start": datetime(2026, 10, 1),
        "end": datetime(2026, 12, 15),
        "score": 3,
        "label": "Pre-Rut (Building Activity)",
    },
    {
        "id": "pre_peak_rut",
        "start": datetime(2026, 12, 16),
        "end": datetime(2026, 12, 28),
        "score": 4,
        "label": "Pre-Peak Rut (Chasing Activity)",
    },
    {
        "id": "peak_rut",
        "start": datetime(2026, 12, 29),
        "end": datetime(2027, 1, 4),
        "score": 5,
        "label": "Peak Rut (Prime Time)",
    },
    {
        "id": "post_rut",
        "start": datetime(2027, 1, 5),
        "end": datetime(2027, 1, 20),
        "score": 3,
        "label": "Post-Rut (Recovery Period)",
    },
    {
        "id": "late_season",
        "start": datetime(2027, 1, 21),
        "end": datetime(2027, 1, 31),
        "score": 2,
        "label": "Late Season (Food Focus)",
    },
]


def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def parse_date_token(token: str, default_year: int, default_month: int | None = None) -> datetime:
    token = token.strip().replace("  ", " ")
    token = re.sub(r"\s+", " ", token)
    m = re.match(
        r"(?P<mon>[A-Za-z]+)\.?\s*(?P<day>\d{1,2})",
        token,
        re.IGNORECASE,
    )
    if m:
        month = MONTHS[m.group("mon")[:3].lower()]
        day = int(m.group("day"))
        year = default_year
        if month < 6:
            year = default_year + 1
        return datetime(year, month, day)

    m = re.match(r"(?P<day>\d{1,2})$", token)
    if not m or default_month is None:
        raise ValueError(f"Cannot parse date token: {token!r}")
    day = int(m.group("day"))
    month = default_month
    year = default_year
    if month < 6:
        year = default_year + 1
    return datetime(year, month, day)


def parse_date_range(date_str: str, season_start_year: int = 2026) -> tuple[datetime, datetime]:
    """Parse ranges like 'Oct. 1 - 4', 'Oct. 29 - Nov. 1', 'Dec. 31 - Jan. 3', or single days."""
    cleaned = date_str.strip()
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s*-\s*", " - ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    parts = [p.strip() for p in cleaned.split(" - ") if p.strip()]
    if len(parts) == 1:
        start = parse_date_token(parts[0], season_start_year)
        return start, start
    if len(parts) != 2:
        raise ValueError(f"Bad date range: {date_str!r}")

    start = parse_date_token(parts[0], season_start_year)
    end = parse_date_token(parts[1], season_start_year, default_month=start.month)
    if end < start:
        end = datetime(end.year + 1, end.month, end.day)
    return start, end


def extract_location_and_hunt(name: str) -> tuple[str, str | None]:
    hunt_num = None
    m = re.search(r"Hunt\s+(\d+)\s*$", name)
    if m:
        hunt_num = m.group(1)
    # Location is text before the last " - "
    if " - " in name:
        location = name.rsplit(" - ", 1)[0].strip()
    else:
        location = name
    # Normalize LBTC naming between schedule/stats
    location = location.replace("Pascagoula River - LBTC", "Pascagoula River (LBTC Unit)")
    location = location.replace("Pascagoula River (LBTC Unit)", "Pascagoula River (LBTC Unit)")
    location = location.replace("Calling Panther Lake", "Calling Panther")
    return location, hunt_num


def infer_group_quota(name: str) -> int:
    """Convert group-slot language into max hunter seats for scoring."""
    lower = name.lower()
    if "cossar" in lower:
        return 3  # 1 group up to 3
    if "natchez" in lower:
        return 4  # 1 group up to 4
    if "phil bryant" in lower or "backwoods" in lower:
        return 16  # 4 groups up to 4
    return 4


def parse_schedule_lines(text: str, hunt_type: str, category: str) -> list[dict]:
    hunts = []
    # Skip headers / footers
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or line.startswith("Hunt Dates") or line.startswith("Total Permits"):
            continue
        if line.startswith("WMA ") or re.fullmatch(r"\d+", line):
            continue
        if "groups" in line.lower() and "hunt" not in line.lower():
            continue
        if line.startswith("*") or line.startswith("Group hunts") or line.startswith("Winners"):
            continue
        if "Minimum of two" in line or "for each hunt" in line:
            continue

        # Pattern with trailing quota integer (supports single-day youth/senior hunts)
        m = re.match(
            r"^(?P<name>.+?)\s+(?P<dates>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}(?:\s*-\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+)?\d{1,2})?)\s+(?P<quota>\d+)\s*$",
            line,
            re.IGNORECASE,
        )
        if m:
            name = m.group("name").strip()
            # Fix double spaces in names like "Gun (Bucks Only)  Hunt"
            name = re.sub(r"\s+", " ", name)
            start, end = parse_date_range(m.group("dates"))
            location, hunt_num = extract_location_and_hunt(name)
            hunts.append(
                {
                    "hunt_name": name,
                    "hunt_type": hunt_type,
                    "category": category,
                    "wma_location": location,
                    "hunt_number": hunt_num,
                    "start_date": start,
                    "end_date": end,
                    "permits_available": int(m.group("quota")),
                    "duration_days": (end - start).days + 1,
                }
            )
            continue

        # Group hunts without inline numeric quota
        if category == "group":
            m2 = re.match(
                r"^(?P<name>.+?)\s+(?P<dates>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}\s*-\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+)?\d{1,2})\s*$",
                line,
                re.IGNORECASE,
            )
            if m2:
                name = re.sub(r"\s+", " ", m2.group("name").strip())
                start, end = parse_date_range(m2.group("dates"))
                location, hunt_num = extract_location_and_hunt(name)
                seats = infer_group_quota(name)
                hunts.append(
                    {
                        "hunt_name": name,
                        "hunt_type": hunt_type,
                        "category": category,
                        "wma_location": location,
                        "hunt_number": hunt_num,
                        "start_date": start,
                        "end_date": end,
                        "permits_available": seats,
                        "duration_days": (end - start).days + 1,
                        "is_group": True,
                    }
                )
    return hunts


def parse_stats(text: str) -> dict[str, dict]:
    """Index 2025 stats by normalized hunt name for competition lookup."""
    stats = {}
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        m = re.match(
            r"^(?P<name>.+?)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}.+?\s+(?P<quota>\d+|1 group.+?|4 groups.+?)\s+(?P<apps>\d+)\s*$",
            line,
            re.IGNORECASE,
        )
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name").strip())
        name = name.replace("Calling Panther Lake", "Calling Panther")
        name = name.replace("Pascagoula River - LBTC", "Pascagoula River (LBTC Unit)")
        apps = int(m.group("apps"))
        quota_raw = m.group("quota")
        if "group" in quota_raw.lower():
            if "4 groups" in quota_raw.lower():
                quota = 4  # applications are for groups
            else:
                quota = 1
        else:
            quota = int(re.search(r"\d+", quota_raw).group())
        ratio = apps / quota if quota else None
        stats[name] = {
            "applications_2025": apps,
            "quota_2025": quota,
            "apps_per_permit_2025": round(ratio, 2) if ratio is not None else None,
        }
        # Also index by location + hunt number for fuzzy match across year date shifts
        location, hunt_num = extract_location_and_hunt(name)
        method_key = classify_method_key(name)
        if hunt_num and method_key:
            stats[f"{location}|{method_key}|{hunt_num}"] = stats[name]
    return stats


def classify_method_key(name: str) -> str | None:
    lower = name.lower()
    if "group" in lower or "backwoods unit) - archery" in lower or "backwoods unit) - gun" in lower:
        # group schedule names omit the word Group sometimes
        if "backwoods" in lower:
            if "archery" in lower:
                return "group_archery"
            if "gun" in lower:
                return "group_gun"
        if "limited weapon" in lower:
            return "group_limited"
        if "primitive" in lower:
            return "group_pw"
    if "youth" in lower:
        return "youth"
    if "senior" in lower:
        return "senior"
    if "pw hunt" in lower or "primitive" in lower:
        return "pw"
    if "gun" in lower:
        return "gun"
    if "archery" in lower:
        return "archery"
    return None


def moon_score_for(start: datetime, end: datetime) -> dict:
    midpoint = start + (end - start) / 2
    best_score = -2
    closest = None
    for phase in MOON_PHASES:
        days = abs((midpoint - phase["date"]).days)
        if days <= 2:
            score = phase["impact"]
        elif days <= 4:
            score = phase["impact"] * 0.7
        elif days <= 7:
            score = phase["impact"] * 0.4
        else:
            score = 0
        if score > best_score:
            best_score = score
            closest = phase["phase"]
    if best_score >= 2.5:
        desc = "Excellent (New Moon Period)"
    elif best_score >= 1:
        desc = "Good (Quarter Moon)"
    elif best_score >= 0:
        desc = "Fair (Neutral)"
    else:
        desc = "Poor (Full Moon Period)"
    return {
        "score": round(best_score, 2),
        "closest_phase": closest,
        "description": desc,
    }


def rut_score_for(start: datetime, end: datetime) -> dict:
    midpoint = start + (end - start) / 2
    for period in RUT_PERIODS:
        if period["start"] <= midpoint <= period["end"]:
            return {
                "score": period["score"],
                "period": period["id"],
                "description": period["label"],
            }
    return {"score": 1, "period": "transition", "description": "Transition Period"}


def competition_score(ratio: float | None) -> dict:
    if ratio is None:
        return {
            "label": "Unknown (new or unmatched)",
            "score": 2.5,
            "apps_per_permit_2025": None,
        }
    # Lower apps/permit => higher odds score (0-5)
    if ratio <= 2:
        label, score = "Very Low", 5.0
    elif ratio <= 5:
        label, score = "Low", 4.0
    elif ratio <= 10:
        label, score = "Moderate", 3.0
    elif ratio <= 20:
        label, score = "High", 2.0
    elif ratio <= 40:
        label, score = "Very High", 1.0
    else:
        label, score = "Extreme", 0.5
    return {
        "label": label,
        "score": score,
        "apps_per_permit_2025": ratio,
    }


def lookup_stats(hunt: dict, stats: dict) -> dict | None:
    name = hunt["hunt_name"]
    # Direct-ish name match after normalizing Group wording differences
    candidates = [
        name,
        name.replace(" - Archery Hunt", " - Group Archery Hunt"),
        name.replace(" - Gun Hunt", " - Group Gun Hunt"),
        name.replace("Limited Weapon Hunt", "Group Limited Weapon Hunt"),
        name.replace("Primitive Weapon Hunt", "Group Primitive Weapon Hunt"),
        name.replace("Calling Panther", "Calling Panther Lake"),
    ]
    for c in candidates:
        if c in stats and "applications_2025" in stats[c]:
            return stats[c]
        # strip Group word variants
        c2 = c.replace(" Group ", " ")
        if c2 in stats and "applications_2025" in stats[c2]:
            return stats[c2]

    method = classify_method_key(name)
    location, hunt_num = hunt["wma_location"], hunt["hunt_number"]
    if method and hunt_num:
        key = f"{location}|{method}|{hunt_num}"
        if key in stats and "applications_2025" in stats[key]:
            return stats[key]
        # Calling Panther Lake alias
        if location == "Calling Panther":
            key = f"Calling Panther Lake|{method}|{hunt_num}"
            if key in stats and "applications_2025" in stats[key]:
                return stats[key]
    return None


def score_hunt(hunt: dict, stats: dict) -> dict:
    moon = moon_score_for(hunt["start_date"], hunt["end_date"])
    rut = rut_score_for(hunt["start_date"], hunt["end_date"])
    hist = lookup_stats(hunt, stats)
    ratio = hist["apps_per_permit_2025"] if hist else None
    apps = hist["applications_2025"] if hist else None
    comp = competition_score(ratio)

    permit_score = min(hunt["permits_available"] / 10, 5)  # 50 permits => max
    duration_score = min(hunt["duration_days"] / 2, 5)  # 10-day hunt => max
    moon_component = max(moon["score"], 0)
    rut_component = rut["score"]

    # Decision score balances quality and realistic draw odds.
    quality = (
        rut_component * 0.35
        + moon_component * 0.20
        + duration_score * 0.15
        + permit_score * 0.10
    )
    # Normalize quality roughly onto 0-5 then blend with competition.
    decision = round(quality * 0.70 + comp["score"] * 0.30, 2)

    return {
        **hunt,
        "moon": moon,
        "rut": rut,
        "applications_2025": apps,
        "apps_per_permit_2025": ratio,
        "competition_label": comp["label"],
        "competition_score": comp["score"],
        "quality_score": round(quality, 2),
        "decision_score": decision,
        "start_date_iso": hunt["start_date"].strftime("%Y-%m-%d"),
        "end_date_iso": hunt["end_date"].strftime("%Y-%m-%d"),
        "date_label": format_date_label(hunt["start_date"], hunt["end_date"]),
    }


def format_date_label(start: datetime, end: datetime) -> str:
    if start.month == end.month and start.year == end.year:
        return f"{start.strftime('%b')} {start.day}-{end.day}, {start.year}"
    if start.year == end.year:
        return f"{start.strftime('%b')} {start.day} – {end.strftime('%b')} {end.day}, {start.year}"
    return f"{start.strftime('%b')} {start.day}, {start.year} – {end.strftime('%b')} {end.day}, {end.year}"


def dates_overlap(a_start, a_end, b_start, b_end) -> bool:
    return a_start <= b_end and b_start <= a_end


def build_strategy(scored: list[dict], n: int = 5, max_drive_miles: float = 120) -> list[dict]:
    """Build a diversified 5-hunt slate near The Camp when possible."""
    adult = [
        h
        for h in scored
        if h["category"] in {"archery", "gun", "primitive_weapon", "group"}
    ]
    nearby = [h for h in adult if (h.get("miles_drive") or 999) <= max_drive_miles]
    pool = nearby if len(nearby) >= n else adult

    def conflicts(hunt: dict, picks: list[dict]) -> bool:
        return any(
            dates_overlap(hunt["start_date"], hunt["end_date"], p["start_date"], p["end_date"])
            for p in picks
        )

    def can_add(hunt: dict, picks: list[dict]) -> bool:
        if hunt in picks or conflicts(hunt, picks):
            return False
        if any(p["wma_location"] == hunt["wma_location"] for p in picks):
            return False
        return True

    def ranked(rows: list[dict]) -> list[dict]:
        # Prefer higher decision score, then shorter drive from cabin.
        return sorted(
            rows,
            key=lambda h: (-h["decision_score"], h.get("miles_drive") or 999),
        )

    picks: list[dict] = []

    # 1) Best nearby peak-rut hunt
    for hunt in ranked([h for h in pool if h["rut"]["period"] == "peak_rut"]):
        if can_add(hunt, picks):
            picks.append(hunt)
            break

    # 2) Best nearby pre-peak / chasing hunt
    for hunt in ranked([h for h in pool if h["rut"]["period"] == "pre_peak_rut"]):
        if can_add(hunt, picks):
            picks.append(hunt)
            break

    # 3) Best nearby sleeper (known low competition)
    sleepers = sorted(
        [
            h
            for h in pool
            if h["apps_per_permit_2025"] is not None and h["apps_per_permit_2025"] <= 6
        ],
        key=lambda h: (h["apps_per_permit_2025"], -h["decision_score"], h.get("miles_drive") or 999),
    )
    for hunt in sleepers:
        if can_add(hunt, picks):
            picks.append(hunt)
            break

    # 4) Fill remaining with decision score while diversifying methods
    remaining = ranked(pool)
    for hunt in remaining:
        if len(picks) >= n:
            break
        if not can_add(hunt, picks):
            continue
        methods = {p["category"] for p in picks}
        if hunt["category"] in methods and len(methods) < 3:
            continue
        if (
            hunt["apps_per_permit_2025"] is not None
            and hunt["apps_per_permit_2025"] > 25
            and len(picks) < n - 1
        ):
            continue
        picks.append(hunt)

    # Final fill from nearby, then statewide if still short
    for source in (remaining, ranked(adult)):
        for hunt in source:
            if len(picks) >= n:
                break
            if can_add(hunt, picks):
                picks.append(hunt)
        if len(picks) >= n:
            break

    return picks[:n]


def load_cabin_locations() -> dict:
    path = OUT_DATA / "locations_from_cabin.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def attach_distance(hunt: dict, cabin_data: dict) -> dict:
    locs = cabin_data.get("locations", {})
    info = locs.get(hunt["wma_location"])
    if not info:
        hunt["miles_drive"] = None
        hunt["minutes_drive"] = None
        hunt["miles_straight"] = None
        return hunt
    hunt["miles_drive"] = info.get("miles_drive")
    hunt["minutes_drive"] = info.get("minutes_drive")
    hunt["miles_straight"] = info.get("miles_straight")
    return hunt


def serialize_hunt(h: dict) -> dict:
    return {
        "id": f"{h['category']}-{h['hunt_name']}".lower().replace(" ", "-"),
        "hunt_name": h["hunt_name"],
        "hunt_type": h["hunt_type"],
        "category": h["category"],
        "wma_location": h["wma_location"],
        "hunt_number": h["hunt_number"],
        "start_date": h["start_date_iso"],
        "end_date": h["end_date_iso"],
        "date_label": h["date_label"],
        "permits_available": h["permits_available"],
        "duration_days": h["duration_days"],
        "decision_score": h["decision_score"],
        "quality_score": h["quality_score"],
        "rut_period": h["rut"]["period"],
        "rut_label": h["rut"]["description"],
        "rut_score": h["rut"]["score"],
        "moon_phase": h["moon"]["closest_phase"],
        "moon_label": h["moon"]["description"],
        "moon_score": h["moon"]["score"],
        "competition_label": h["competition_label"],
        "competition_score": h["competition_score"],
        "applications_2025": h["applications_2025"],
        "apps_per_permit_2025": h["apps_per_permit_2025"],
        "miles_drive": h.get("miles_drive"),
        "minutes_drive": h.get("minutes_drive"),
        "miles_straight": h.get("miles_straight"),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = [
        "hunt_name",
        "hunt_type",
        "wma_location",
        "start_date",
        "end_date",
        "permits_available",
        "duration_days",
        "decision_score",
        "quality_score",
        "rut_label",
        "moon_label",
        "competition_label",
        "apps_per_permit_2025",
        "applications_2025",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for h in rows:
            writer.writerow(
                {
                    "hunt_name": h["hunt_name"],
                    "hunt_type": h["hunt_type"],
                    "wma_location": h["wma_location"],
                    "start_date": h["start_date_iso"],
                    "end_date": h["end_date_iso"],
                    "permits_available": h["permits_available"],
                    "duration_days": h["duration_days"],
                    "decision_score": h["decision_score"],
                    "quality_score": h["quality_score"],
                    "rut_label": h["rut"]["description"],
                    "moon_label": h["moon"]["description"],
                    "competition_label": h["competition_label"],
                    "apps_per_permit_2025": h["apps_per_permit_2025"],
                    "applications_2025": h["applications_2025"],
                }
            )


def main() -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_REPORTS.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    all_hunts: list[dict] = []
    for category, (filename, hunt_type) in PDF_MAP.items():
        text = pdf_text(RAW / filename)
        parsed = parse_schedule_lines(text, hunt_type=hunt_type, category=category)
        print(f"Parsed {category}: {len(parsed)} hunts")
        all_hunts.extend(parsed)

    stats_text = pdf_text(RAW / "stats_2025.pdf")
    stats = parse_stats(stats_text)
    print(f"Parsed historical stats entries: {len(stats)}")

    cabin_data = load_cabin_locations()
    scored = [attach_distance(score_hunt(h, stats), cabin_data) for h in all_hunts]
    scored.sort(key=lambda h: h["decision_score"], reverse=True)

    # Category CSVs
    for category in PDF_MAP:
        rows = [h for h in scored if h["category"] == category]
        write_csv(OUT_DATA / f"deer_{category}_hunts_2026_27.csv", rows)

    write_csv(OUT_DATA / "deer_all_hunts_2026_27_scored.csv", scored)

    adult = [h for h in scored if h["category"] in {"archery", "gun", "primitive_weapon", "group"}]
    strategy = build_strategy(adult, n=5)

    by_category = {}
    for cat in ["archery", "gun", "primitive_weapon", "group", "youth", "senior"]:
        subset = [h for h in scored if h["category"] == cat]
        by_category[cat] = [serialize_hunt(h) for h in subset[:8]]

    peak = [h for h in adult if h["rut"]["period"] == "peak_rut"]
    peak.sort(key=lambda h: h["decision_score"], reverse=True)

    sleeper = [
        h
        for h in adult
        if h["apps_per_permit_2025"] is not None
        and h["apps_per_permit_2025"] <= 8
        and h["rut"]["score"] >= 3
        and h["decision_score"] >= 3.2
    ]
    sleeper.sort(key=lambda h: (h["apps_per_permit_2025"], -h["decision_score"]))

    premium = [
        h
        for h in adult
        if h["rut"]["score"] >= 4 and h["permits_available"] >= 12
    ][:12]

    locations = sorted({h["wma_location"] for h in scored})
    home = cabin_data.get(
        "home",
        {
            "name": "The Camp",
            "address": "1149 Watertower Rd, Bentonia, MS",
            "lat": 32.6505,
            "lon": -90.3648,
        },
    )
    summary = {
        "brand": "Delta Draw Hunts",
        "season": "2026-27",
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "home_base": home,
        "application_window": {
            "opens": "2026-07-15",
            "closes": "2026-08-15",
            "note": "Apply online via MDWFP license system; up to 5 ranked hunt selections.",
        },
        "sources": {
            "schedules": [
                "WMA Archery Deer Draw Hunts (2026)",
                "WMA Gun Deer Draw Hunts (2026)",
                "WMA Primitive Weapon Deer Draw Hunts (2026)",
                "WMA Group Deer Draw Hunts (2026)",
                "WMA Youth Deer Draw Hunts (2026)",
                "WMA Senior Deer Draw Hunts (2026)",
            ],
            "competition": "WMA Deer Draw Stats (2025)",
            "rut_region": "Yazoo County / Mississippi Delta peak rut Dec 29 – Jan 4",
            "distances": "Driving miles/minutes from The Camp via OSRM road network",
        },
        "totals": {
            "hunts": len(scored),
            "permits": sum(h["permits_available"] for h in scored),
            "locations": len(locations),
            "by_category": {
                cat: len([h for h in scored if h["category"] == cat]) for cat in PDF_MAP
            },
        },
        "nearby": {
            "within_60": len([h for h in scored if (h.get("miles_drive") or 999) <= 60]),
            "within_90": len([h for h in scored if (h.get("miles_drive") or 999) <= 90]),
            "within_120": len([h for h in scored if (h.get("miles_drive") or 999) <= 120]),
        },
        "peak_rut": {
            "window": "Dec 29, 2026 – Jan 4, 2027",
            "hunt_count": len(peak),
            "top": [serialize_hunt(h) for h in peak[:6]],
        },
        "key_moons": [
            {"date": "2026-10-10", "phase": "New Moon"},
            {"date": "2026-11-09", "phase": "New Moon"},
            {"date": "2026-12-09", "phase": "New Moon"},
            {"date": "2027-01-07", "phase": "New Moon"},
        ],
        "strategy": [serialize_hunt(h) for h in strategy],
        "top_overall": [serialize_hunt(h) for h in adult[:15]],
        "top_by_category": by_category,
        "premium_window": [serialize_hunt(h) for h in premium],
        "sleeper_picks": [serialize_hunt(h) for h in sleeper[:10]],
        "locations": locations,
        "hunts": [serialize_hunt(h) for h in scored],
    }

    decision_path = WEB_DATA / "decision_2026_27.json"
    decision_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Also mirror for GitHub Pages root convenience
    (ROOT / "decision_2026_27.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Markdown report
    lines = [
        "# Mississippi WMA Deer Draw Analysis — 2026-27",
        "",
        f"**Generated:** {summary['generated_at']}",
        f"**Application window:** July 15 – August 15, 2026",
        f"**Hunts scored:** {summary['totals']['hunts']} across {summary['totals']['locations']} locations",
        f"**Permit seats represented:** {summary['totals']['permits']}",
        "",
        "## Scoring model",
        "",
        "- **Rut timing (35%)** — Yazoo/Delta peak rut Dec 29 – Jan 4",
        "- **Moon phase (20%)** — New moon preferred; full moon penalized",
        "- **Duration (15%)** — Longer hunts score higher",
        "- **Permit volume (10%)** — More seats help absolute access",
        "- **Historical draw odds (30%)** — Inverse of 2025 apps-per-permit",
        "",
        "## Recommended 5-hunt application slate",
        "",
    ]
    for i, h in enumerate(strategy, 1):
        odds = (
            f"{h['apps_per_permit_2025']} apps/permit in 2025"
            if h["apps_per_permit_2025"] is not None
            else "no 2025 match (new/unmatched)"
        )
        lines.append(
            f"{i}. **{h['hunt_name']}** — {h['date_label']} · {h['permits_available']} permits · "
            f"score {h['decision_score']} · {h['rut']['description']} · {h['competition_label']} competition ({odds})"
        )

    lines += ["", "## Peak rut opportunities", ""]
    for h in peak[:8]:
        lines.append(
            f"- {h['hunt_name']} ({h['date_label']}) — score {h['decision_score']}, "
            f"{h['competition_label']} competition"
        )

    lines += ["", "## Notable changes vs prior curated set", ""]
    lines.append("- **Alligator WMA** added with six primitive weapon draws (36 permits each).")
    lines.append("- Statewide inventory expanded (Canemount, Natchez, Hell Creek, Charles Ray Nix, Yockanookany, etc.).")
    lines.append("- December 9, 2026 new moon falls in pre-peak chasing window — strong mid-December quality.")
    lines.append("- Peak rut sits between Dec 24 full moon and Jan 7 new moon (last-quarter conditions).")

    report_path = OUT_REPORTS / "analysis_2026_27.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n=== TOP 10 DECISION SCORES (adult) ===")
    for h in adult[:10]:
        print(
            f"{h['decision_score']:4.2f} | {h['date_label']:28} | {h['competition_label']:12} | {h['hunt_name']}"
        )
    print("\n=== STRATEGY ===")
    for i, h in enumerate(strategy, 1):
        print(f"{i}. {h['hunt_name']} | {h['date_label']} | {h['decision_score']}")
    print(f"\nWrote {decision_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
