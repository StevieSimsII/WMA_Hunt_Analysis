# Mississippi WMA Draw Hunt Analysis Project

This project helps analyze and track Mississippi Wildlife Management Area (WMA) draw hunt opportunities to make informed decisions about which hunts to apply for. **Enhanced with moon phase and deer rut timing analysis for Yazoo County, Mississippi region.**

## Project Overview

The Mississippi Department of Wildlife, Fisheries & Parks offers draw hunts on various WMAs across the state. These limited-entry hunts provide quality hunting opportunities while managing hunter numbers and wildlife populations.

**UPDATED**: Advanced scoring system that factors in:
- 🌙 **Moon Phase Impact** - Optimal timing for deer movement
- 🦌 **Deer Rut Periods** - Peak breeding activity windows (Dec 29 - Jan 4 for Yazoo County)
- 📊 **Traditional Metrics** - Permits available, duration, competition
- 🎯 **Combined Scoring** - Weighted analysis for best opportunities

## Key Information

### Application Periods (2025-26 Season)
- **Deer**: July 15 - August 15 ⚠️ **DEADLINE: 29 DAYS FROM TODAY**
- **Early Teal**: July 15 - August 15
- **Rabbit**: July 15 - August 15
- **Dove**: July 15 - August 15
- **Youth Dove**: July 15 - August 15
- **Turkey**: January 1 - January 31
- **Waterfowl**: October 1 - October 15

### Enhanced Analysis Features
- **Moon Phase Scoring**: New Moon = Best, Full Moon = Challenging
- **Rut Period Analysis**: Peak Rut timing verified for Yazoo County (Dec 29 - Jan 4)
- **Combined Rankings**: Multi-factor scoring for optimal hunt selection
- **Comprehensive Coverage**: All hunt types (Archery, Gun, Primitive Weapon, Group)

### Requirements
- Valid WMA User Permit, lifetime hunting license, or youth/senior exempt license
- Hunter Education certification (for those born after January 1, 1972)

### Important Notes
- Draw results released within a week of application deadline
- Permits are non-transferable
- Email and system notifications for results

## Project Structure

- `data/` - Raw and processed hunt data with enhanced scoring
- `analysis/` - Scripts and notebooks for data analysis
  - `enhanced_hunt_analyzer.py` - Moon phase & rut analysis tool
  - `moon_rut_analysis.md` - Detailed moon/rut timing guide
- `reports/` - Generated reports and summaries
- `docs/` - Documentation and rules
- `QUICK_REFERENCE.md` - Fast lookup with moon/rut recommendations

## Getting Started

1. **Check the enhanced recommendations** in `QUICK_REFERENCE.md`
2. **Review moon phase analysis** in `analysis/moon_rut_analysis.md`  
3. **Run the enhanced analyzer**: `python analysis/enhanced_hunt_analyzer.py`
4. **Use the decision matrix** to finalize your choices

## 🏆 Top Recommendations (Comprehensive Analysis - All Weapon Types)

**TIER 1 - MAXIMUM SUCCESS OPPORTUNITIES:**
1. **Charles Ray Nix PW Hunt 4** - Dec 15-21, 2025 (Score: 4.70) 🥇
2. **Yockanookany PW Hunt 3** - Dec 15-28, 2025 (Score: 4.70) 🥇
3. **Phil Bryant Gun/Archery** - Dec 18, 2025 (Score: 4.64) 🥈

**PEAK RUT CHAMPION:**
- **Charles Ray Nix PW Hunt 6** - Dec 29-Jan 4, 2026 (Score: 4.48) 🦌

*Analysis includes 203 hunt opportunities across Archery, Gun, Primitive Weapon, and Group hunts. Primitive Weapon hunts offer the best combination of timing, duration, and success probability for Yazoo County rut patterns.*

## Resources

- [MDWFP WMA Draw Hunts](https://www.mdwfp.com/wildlife-hunting/wma-draw-hunts)
- [General Hunting Rules](https://www.mdwfp.com/wildlife-hunting/general-hunting-rules-regulations)
- [Wildlife Management Areas](https://www.mdwfp.com/wildlife-hunting/wildlife-management-areas)
