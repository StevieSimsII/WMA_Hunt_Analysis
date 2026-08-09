"""Turn MDWFP draw-hunt PDF tables into the CSVs that build_app_data.py reads.

MDWFP publishes each deer draw category as a PDF of `Hunt | Dates | Quota`
rows. Extract those tables to markdown under data/raw/ (one file per category,
named <category>_<season>.md), then run this to emit the CSVs.

Run:  python parse_mdwfp_draws.py 2026
      (the argument is the season's opening year; defaults to the newest
       season found in data/raw/)
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data"

CATEGORIES = {
    "archery": ("Deer Archery", "deer_archery_hunts_{season}.csv"),
    "primitive_weapon": ("Deer Primitive Weapon", "deer_primitive_weapon_hunts_{season}.csv"),
    "gun": ("Deer Gun", "deer_gun_hunts_{season}.csv"),
    "group": ("Deer Group", "deer_group_hunts_{season}.csv"),
}

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# Splits "Twin Oaks-PW Hunt3" into area and the rest. The weapon keyword is the
# anchor, since the separator and spacing are inconsistent across the PDFs.
HUNT_RE = re.compile(
    r"^(?P<wma>.+?)\s*-\s*(?P<rest>(?:Archery|PW|Primitive Weapon|Limited Weapon|Gun)\b.*)$"
)

# "4 groups(up to4 hunters/group)" / "1 group(up to3 hunters)"
GROUP_RE = re.compile(r"(?P<groups>\d+)\s*groups?\s*\(\s*up\s*to\s*(?P<size>\d+)", re.I)


def normalize_wma(name: str) -> str:
    """MDWFP's PDFs drop spaces around unit names — put them back."""
    name = name.strip()
    name = re.sub(r"\s*\(\s*", " (", name)          # "Phil Bryant(Ten" -> "Phil Bryant (Ten"
    name = re.sub(r"\s*\)", ")", name)
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)  # "Ten PointUnit" -> "Ten Point Unit"
    return re.sub(r"\s+", " ", name).strip()


def normalize_hunt_name(wma: str, rest: str) -> str:
    rest = re.sub(r"\s+", " ", rest.strip())
    rest = re.sub(r"\s*\(\s*", " (", rest)               # "Gun(Bucks Only)" -> "Gun (Bucks Only)"
    rest = re.sub(r"\s*\)", ")", rest)
    rest = re.sub(r"(?<=[a-z)])(?=Hunt\b)", " ", rest)   # "...(Bucks Only)Hunt1" -> "... Hunt1"
    rest = re.sub(r"(Hunt)\s*(\d)", r"\1 \2", rest)      # "Hunt1" -> "Hunt 1"
    return f"{wma} - {rest}"


def parse_dates(spec: str, season_year: int) -> tuple[date, date]:
    """`Oct.29-Nov.1`, `Dec.31-Jan.3`, `Nov.5-6` -> (start, end).

    Months Jan-Jun belong to the calendar year after the season opens.
    """
    spec = spec.replace(" ", "")
    m = re.match(
        r"^(?P<m1>[A-Za-z]{3})\.?(?P<d1>\d{1,2})-(?:(?P<m2>[A-Za-z]{3})\.?)?(?P<d2>\d{1,2})$",
        spec,
    )
    if not m:
        raise ValueError(f"Unparseable date range: {spec!r}")

    def build(month_abbr: str, day: int) -> date:
        month = MONTHS[month_abbr[:3].title()]
        year = season_year + 1 if month <= 6 else season_year
        return date(year, month, day)

    start = build(m.group("m1"), int(m.group("d1")))
    end = build(m.group("m2") or m.group("m1"), int(m.group("d2")))
    if end < start:
        raise ValueError(f"End before start in {spec!r}: {start} > {end}")
    return start, end


def parse_quota(raw: str) -> tuple[int, int | None]:
    """Return (permits, group_size). Group rows read `4 groups(up to4 hunters...)`."""
    m = GROUP_RE.search(raw)
    if m:
        groups, size = int(m.group("groups")), int(m.group("size"))
        return groups * size, size
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        raise ValueError(f"Unparseable quota: {raw!r}")
    return int(digits), None


def parse_table(path: Path, hunt_type: str, season_year: int) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        hunt_raw, dates_raw, quota_raw = cells[0], cells[1], cells[2]
        if hunt_raw.lower() == "hunt" or set(hunt_raw) <= {"-", " "}:
            continue
        if hunt_raw.lower().startswith("total permits") or not dates_raw:
            continue

        m = HUNT_RE.match(hunt_raw)
        if not m:
            raise ValueError(f"{path.name}: cannot split area from hunt: {hunt_raw!r}")

        wma = normalize_wma(m.group("wma"))
        start, end = parse_dates(dates_raw, season_year)
        permits, group_size = parse_quota(quota_raw)

        row = {
            "hunt_name": normalize_hunt_name(wma, m.group("rest")),
            "hunt_type": hunt_type,
            "wma_location": wma,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "permits_available": permits,
            "duration_days": (end - start).days + 1,
        }
        if group_size is not None:
            row["group_size"] = group_size
        rows.append(row)
    return rows


def main():
    if not RAW_DIR.exists():
        raise SystemExit(f"Missing {RAW_DIR}. Extract the MDWFP PDFs there first.")

    seasons = sorted({
        m.group(1)
        for p in RAW_DIR.glob("*.md")
        if (m := re.search(r"_(\d{4}_\d{2})\.md$", p.name))
    })
    if not seasons:
        raise SystemExit(f"No <category>_<season>.md files in {RAW_DIR}")

    season = sys.argv[1] if len(sys.argv) > 1 else seasons[-1]
    if "_" not in season:                       # allow "2026" shorthand
        season = f"{season}_{str(int(season) + 1)[-2:]}"
    season_year = int(season.split("_")[0])

    total = 0
    for key, (hunt_type, out_name) in CATEGORIES.items():
        src = RAW_DIR / f"{key}_{season}.md"
        if not src.exists():
            print(f"  skip {key}: no {src.name}")
            continue

        rows = parse_table(src, hunt_type, season_year)
        cols = ["hunt_name", "hunt_type", "wma_location", "start_date", "end_date",
                "permits_available", "duration_days"]
        if any("group_size" in r for r in rows):
            cols.append("group_size")

        out = OUT_DIR / out_name.format(season=season)
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)

        permits = sum(r["permits_available"] for r in rows)
        areas = len({r["wma_location"] for r in rows})
        print(f"  {out.name}: {len(rows)} hunts, {permits} permits, {areas} areas")
        total += len(rows)

    print(f"Parsed {total} hunts for season {season_year}-{str(season_year + 1)[-2:]}")


if __name__ == "__main__":
    main()
