"""
Top 5 Hunt Rankings by Category
Analyzes hunts based on moon phases, deer movement, and rut timing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_hunt_data():
    """Load all hunt data from CSV files."""
    hunt_files = {
        'Archery': 'data/deer_archery_hunts_2025_26.csv',
        'Gun': 'data/deer_gun_hunts_2025_26.csv',
        'Primitive Weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
        'Group': 'data/deer_group_hunts_2025_26.csv'
    }
    
    all_hunts = []
    
    for hunt_type, file_path in hunt_files.items():
        try:
            df = pd.read_csv(file_path)
            df['hunt_method'] = hunt_type
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            all_hunts.append(df)
            print(f"Loaded {len(df)} {hunt_type} hunts")
        except Exception as e:
            print(f"Error loading {hunt_type} data: {e}")
    
    if all_hunts:
        combined_df = pd.concat(all_hunts, ignore_index=True)
        return combined_df
    return pd.DataFrame()

def calculate_enhanced_deer_scores(df):
    """Calculate enhanced scores focusing on deer movement, moon phases, and rut."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Key moon phases (new moons are best for deer movement)
    moon_phases = {
        datetime(2025, 10, 21): 5,  # New Moon - Excellent
        datetime(2025, 11, 20): 5,  # New Moon - Excellent
        datetime(2025, 12, 19): 5,  # New Moon - Excellent
        datetime(2026, 1, 20): 5,   # New Moon - Excellent
        # Full moons (less ideal but still active)
        datetime(2025, 10, 6): 3,   # Full Moon
        datetime(2025, 11, 5): 3,   # Full Moon
        datetime(2025, 12, 4): 3,   # Full Moon
        datetime(2026, 1, 3): 3,    # Full Moon
    }
    
    # Enhanced rut scoring based on Yazoo County timing
    def get_enhanced_rut_score(date):
        # Peak Rut - Best deer movement and breeding activity
        if datetime(2025, 12, 29) <= date <= datetime(2026, 1, 4):
            return 10  # Maximum score for peak rut
        # Pre-Peak Rut - Increased movement, bucks starting to chase
        elif datetime(2025, 12, 20) <= date <= datetime(2025, 12, 28):
            return 8   # Very good activity
        # Early Rut - Bucks making scrapes, increasing activity
        elif datetime(2025, 12, 10) <= date <= datetime(2025, 12, 19):
            return 7   # Good activity
        # Pre-Rut - Velvet shedding, bachelor groups breaking up
        elif datetime(2025, 11, 15) <= date <= datetime(2025, 12, 9):
            return 6   # Moderate activity
        # Post-Peak Rut - Some activity continues
        elif datetime(2026, 1, 5) <= date <= datetime(2026, 1, 15):
            return 5   # Decent activity
        # Early Season - Predictable patterns
        elif datetime(2025, 10, 1) <= date <= datetime(2025, 11, 14):
            return 4   # Predictable movement
        # Late Season - Weather dependent
        elif datetime(2026, 1, 16) <= date <= datetime(2026, 1, 31):
            return 3   # Weather dependent
        else:
            return 2   # Off-season
    
    def get_enhanced_moon_score(date):
        """Enhanced moon scoring based on deer movement research."""
        best_score = 0
        for moon_date, base_score in moon_phases.items():
            days_diff = abs((date - moon_date).days)
            
            # New moon periods (most active)
            if base_score == 5:  # New moon
                if days_diff == 0:
                    phase_score = 5.0  # Peak new moon
                elif days_diff <= 1:
                    phase_score = 4.5  # Day before/after new moon
                elif days_diff <= 2:
                    phase_score = 4.0  # 2 days from new moon
                elif days_diff <= 3:
                    phase_score = 3.0  # 3 days from new moon
                else:
                    phase_score = 0
            # Full moon periods (moderate activity)
            elif base_score == 3:  # Full moon
                if days_diff <= 1:
                    phase_score = 3.0  # Full moon period
                elif days_diff <= 2:
                    phase_score = 2.0  # Near full moon
                else:
                    phase_score = 0
            else:
                phase_score = 0
                
            best_score = max(best_score, phase_score)
        
        return best_score
    
    # Weather/Temperature score (cold fronts increase movement)
    def get_weather_score(date):
        """Score based on typical weather patterns for deer movement."""
        month = date.month
        if month == 12:  # December - prime cold weather
            return 5
        elif month == 1:  # January - continued cold
            return 4
        elif month == 11:  # November - cooling temperatures
            return 4
        elif month == 10:  # October - mild temperatures
            return 3
        else:
            return 2
    
    # Calculate all scores
    df['rut_score'] = df['start_date'].apply(get_enhanced_rut_score)
    df['moon_score'] = df['start_date'].apply(get_enhanced_moon_score)
    df['weather_score'] = df['start_date'].apply(get_weather_score)
    
    # Permit availability score (more permits = better odds)
    df['permit_score'] = np.minimum(df['permits_available'] / 10, 5.0)
    
    # Duration score (longer hunts = more opportunities)
    df['duration_score'] = np.minimum(df['duration_days'], 5.0)
    
    # Combined deer movement score (weighted for optimal deer activity)
    df['deer_movement_score'] = (
        df['rut_score'] * 0.4 +        # 40% - Rut is most important
        df['moon_score'] * 0.3 +       # 30% - Moon phases critical
        df['weather_score'] * 0.2 +    # 20% - Weather influences movement
        df['permit_score'] * 0.05 +    # 5% - Permit availability
        df['duration_score'] * 0.05    # 5% - Hunt duration
    ).round(2)
    
    return df

def rank_hunts_by_category(df):
    """Rank top 5 hunts in each category based on deer movement."""
    categories = ['Gun', 'Group', 'Primitive Weapon', 'Archery']
    rankings = {}
    
    for category in categories:
        category_hunts = df[df['hunt_method'] == category].copy()
        if not category_hunts.empty:
            # Sort by deer movement score (descending)
            top_hunts = category_hunts.nlargest(5, 'deer_movement_score')
            rankings[category] = top_hunts
        else:
            rankings[category] = pd.DataFrame()
    
    return rankings

def display_hunt_details(hunt, rank):
    """Display detailed hunt information."""
    print(f"\n#{rank} - {hunt['hunt_name']}")
    print(f"📍 Location: {hunt['wma_location']}")
    print(f"📅 Dates: {hunt['start_date'].strftime('%m/%d/%Y')} - {hunt['end_date'].strftime('%m/%d/%Y')}")
    print(f"🎯 Permits Available: {hunt['permits_available']}")
    print(f"📊 DEER MOVEMENT SCORE: {hunt['deer_movement_score']:.2f}/10.0")
    print(f"   └─ Rut Score: {hunt['rut_score']}/10 (40% weight)")
    print(f"   └─ Moon Score: {hunt['moon_score']:.1f}/5 (30% weight)")
    print(f"   └─ Weather Score: {hunt['weather_score']}/5 (20% weight)")
    print(f"   └─ Permit Score: {hunt['permit_score']:.1f}/5 (5% weight)")
    print(f"   └─ Duration Score: {hunt['duration_score']:.1f}/5 (5% weight)")
    
    # Special indicators
    if hunt['rut_score'] >= 10:
        print("🦌 *** PEAK RUT PERIOD - MAXIMUM DEER ACTIVITY ***")
    elif hunt['rut_score'] >= 8:
        print("🔥 ** PRE-PEAK RUT - VERY HIGH ACTIVITY **")
    elif hunt['rut_score'] >= 7:
        print("⭐ * EARLY RUT - HIGH ACTIVITY *")
    
    if hunt['moon_score'] >= 4.5:
        print("🌑 *** OPTIMAL NEW MOON PERIOD ***")
    elif hunt['moon_score'] >= 4.0:
        print("🌙 ** EXCELLENT MOON PHASE **")
    elif hunt['moon_score'] >= 3.0:
        print("🌗 * GOOD MOON PHASE *")
    
    print("-" * 50)

def main():
    print("=" * 60)
    print("MISSISSIPPI WMA TOP 5 HUNT RANKINGS BY CATEGORY")
    print("Based on Moon Phases, Deer Movement, and Rut Timing")
    print("=" * 60)
    
    # Load data
    df = load_hunt_data()
    if df.empty:
        print("No hunt data available!")
        return
    
    # Calculate enhanced scores
    df = calculate_enhanced_deer_scores(df)
    
    # Get rankings
    rankings = rank_hunts_by_category(df)
    
    # Display results for each category
    categories = ['Gun', 'Group', 'Primitive Weapon', 'Archery']
    
    for category in categories:
        print(f"\n🏆 TOP 5 {category.upper()} HUNTS")
        print("=" * 50)
        
        if rankings[category].empty:
            print(f"No {category} hunts available.")
            continue
        
        for idx, (_, hunt) in enumerate(rankings[category].iterrows(), 1):
            display_hunt_details(hunt, idx)
    
    # Overall best hunts across all categories
    print(f"\n🥇 OVERALL TOP 10 HUNTS (ALL CATEGORIES)")
    print("=" * 60)
    
    top_overall = df.nlargest(10, 'deer_movement_score')
    for idx, (_, hunt) in enumerate(top_overall.iterrows(), 1):
        print(f"#{idx} - {hunt['hunt_name']} ({hunt['hunt_method']}) - Score: {hunt['deer_movement_score']:.2f}")
        print(f"     {hunt['start_date'].strftime('%m/%d/%Y')} at {hunt['wma_location']}")
    
    print(f"\n📊 SCORING METHODOLOGY:")
    print("─" * 30)
    print("• Rut Score (40%): Peak rut = 10, Pre-peak = 8, Early rut = 7")
    print("• Moon Score (30%): New moon = 5, Near new moon = 4-4.5")
    print("• Weather Score (20%): December = 5, January/November = 4")
    print("• Permit Score (5%): Based on permits available")
    print("• Duration Score (5%): Based on hunt length")
    print("\n🦌 Peak Rut Period: December 29, 2025 - January 4, 2026")
    print("🌑 Key New Moons: Oct 21, Nov 20, Dec 19, 2025; Jan 20, 2026")

if __name__ == "__main__":
    main()
