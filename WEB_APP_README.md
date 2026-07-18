# Delta Draw Hunts — Mississippi WMA Deer Draw Decision App

Interactive decision desk for the **2026–27** Mississippi WMA deer draw season.

**Live (GitHub Pages):** https://steviesimsii.github.io/WMA_Hunt_Analysis/

## Home base

**The Camp** — 1149 Watertower Rd, Bentonia, MS

Browse filters include driving distance / radius from the cabin.

## What’s inside

- Recommended **5-hunt application slate** (no date conflicts, diversified locations/methods)
- Full searchable inventory of **289** scored hunts
- Peak-rut shortlist (Dec 29, 2026 – Jan 4, 2027)
- Competition lens using **2025 draw stats** (apps per permit)

## Data sources

- MDWFP official 2026 deer draw hunt PDFs (archery, gun, primitive weapon, group, youth, senior)
- MDWFP WMA Deer Draw Stats (2025)
- Yazoo/Delta peak rut window: Dec 29 – Jan 4
- 2026–27 moon phases for October–January

## Scoring

Decision score blends:

| Factor | Weight |
| --- | --- |
| Rut timing | 35% |
| 2025 draw odds | 30% |
| Moon phase | 20% |
| Hunt duration | 15% |
| Permit volume | 10% |

## Rebuild analysis locally

```bash
pip install pypdf
python analysis/build_2026_decision_data.py
```

Outputs:

- `decision_2026_27.json` (web app data)
- `data/deer_*_hunts_2026_27.csv`
- `reports/analysis_2026_27.md`

## Application window

**July 15 – August 15, 2026** via the MDWFP license system (up to five ranked selections).

Independent analysis — not affiliated with MDWFP.
