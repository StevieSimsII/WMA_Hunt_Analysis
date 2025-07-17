# 🦌 Mississippi WMA Hunt Analysis Dashboard

## Overview
Interactive Streamlit dashboard for analyzing and reviewing Mississippi WMA draw hunt opportunities for the 2025-26 season.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
streamlit run streamlit_dashboard.py
```

### 3. Open in Browser
- Local URL: http://localhost:8501
- Network URL will be displayed in terminal

## Dashboard Features

### 📊 Overview Tab
- **Key Metrics**: Total hunts, permits, locations, average scores
- **Hunt Distribution**: Pie chart showing hunts by method
- **Location Analysis**: Bar chart of permits by WMA location

### 🏆 Top Recommendations Tab
- **Top 10 Hunts**: Highest scoring opportunities with detailed breakdowns
- **Competition Levels**: Color-coded difficulty indicators
- **Special Markers**: Peak rut period highlights

### 📈 Analysis Tab
- **Score Distribution**: Histogram of hunt quality scores
- **Timeline View**: Monthly breakdown by hunt method
- **Location Performance**: Comparative statistics table

### 📅 Calendar View Tab
- **Monthly Calendar**: Traditional calendar grid showing hunts by date
- **Timeline View**: Horizontal timeline with rut period highlighting
- **Gantt Chart**: Project-style chart grouped by WMA location
- **Date Conflict Detection**: Identify overlapping hunt dates
- **Peak Rut Visualization**: Clear marking of Dec 29 - Jan 4 period
- **Competition Levels**: Color-coded difficulty indicators
- **Special Markers**: Peak rut period highlights

### 📈 Analysis Tab
- **Score Distribution**: Histogram of hunt quality scores
- **Timeline View**: Monthly breakdown by hunt method
- **Location Performance**: Comparative statistics table

### 📅 Calendar View Tab
- **Monthly Calendar**: Traditional calendar grid showing hunts by date
- **Timeline View**: Horizontal timeline with rut period highlighting
- **Gantt Chart**: Project-style chart grouped by WMA location
- **Date Conflict Detection**: Identify overlapping hunt dates
- **Peak Rut Visualization**: Clear marking of Dec 29 - Jan 4 period

### 🎯 5-Hunt Strategy Tab
- **Optimal Strategy**: Pre-calculated best 5 hunts for application
- **Strategic Notes**: Rut timing, moon phases, competition levels
- **Application Checklist**: Step-by-step preparation guide

### 📋 Data Explorer Tab
- **Searchable Table**: Full hunt database with filtering
- **Custom Sorting**: Sort by any metric
- **Data Export**: Download filtered results as CSV

## Filtering Options

### Sidebar Controls
- **Hunt Methods**: Filter by Archery, Gun, Primitive Weapon, Group
- **WMA Locations**: Multi-select location filter
- **Date Range**: Calendar-based date filtering
- **Score Threshold**: Minimum hunt quality filter

## Scoring System

### Combined Score (0-5.0)
- **Permit Score (30%)**: Based on permits available
- **Duration Score (20%)**: Hunt length in days
- **Moon Score (20%)**: Proximity to new moon phases
- **Rut Score (30%)**: Alignment with deer rutting activity

### Special Considerations
- **Peak Rut Period**: Dec 29, 2025 - Jan 4, 2026 (Yazoo County timing)
- **New Moon Dates**: Oct 21, Nov 20, Dec 19, 2025; Jan 20, 2026
- **Premium Hunts**: Scores 4.0+ indicate very high competition

## Data Sources

### CSV Files
- `data/deer_archery_hunts_2025_26.csv`
- `data/deer_gun_hunts_2025_26.csv`
- `data/deer_primitive_weapon_hunts_2025_26.csv`
- `data/deer_group_hunts_2025_26.csv`

### Hunt Locations Included
- Phil Bryant WMA (Backwoods Unit & Goose Lake Unit)
- Mahannah WMA
- Sky Lake WMA
- Twin Oaks WMA
- Riverfront WMA

## Optimal 5-Hunt Strategy

### Selected Hunts
1. **Phil Bryant Group Gun Hunt 3** (Nov 19-23) - Required group hunt
2. **Phil Bryant Archery Hunt 14** (Jan 1-4) - Peak rut period
3. **Phil Bryant Archery Hunt 12** (Dec 18-21) - Highest scoring
4. **Mahannah PW Hunt 5** (Nov 20-21) - Method diversification
5. **Mahannah Gun Hunt 6** (Dec 21-22) - Strategic backup

### Strategy Benefits
- ✅ All hunts on different dates (no conflicts)
- ✅ Includes required group gun hunt
- ✅ Balanced across 3 WMA locations
- ✅ Covers 4 different hunt methods
- ✅ Mix of peak rut and strategic opportunities

## Usage Tips

### For Hunt Selection
1. Use **Score Threshold** slider to filter high-quality hunts
2. Check **Top Recommendations** for detailed analysis
3. Review **5-Hunt Strategy** for optimal application plan

### For Analysis
1. Filter by specific methods or locations of interest
2. Use **Data Explorer** for detailed hunt comparisons
3. Export filtered data for offline analysis

### For Planning
1. Review application checklist in Strategy tab
2. Note hunt dates and coordinate with partners
3. Mark application deadline: July 15, 2025

## Technical Notes

### Performance
- Data is cached for fast filtering and sorting
- Charts are interactive (zoom, pan, hover)
- Responsive design works on desktop and mobile

### Troubleshooting
- If CSV files are missing, check `data/` folder
- For display issues, try refreshing the browser
- Dashboard auto-updates when filters change

## Project Structure
```
DeltaHuntingSeason/
├── streamlit_dashboard.py          # Main dashboard application
├── requirements.txt                # Python dependencies
├── data/                          # Hunt data CSV files
├── docs/                          # Documentation
├── analysis/                      # Analysis scripts
└── reports/                       # Generated reports
```

## Contact & Updates
- Dashboard last updated: January 2025
- Hunt data reflects 2025-26 season as published by MDWFP
- For questions or updates, see project documentation

---

**🎯 Ready to start your hunt planning? Launch the dashboard and explore your options!**
