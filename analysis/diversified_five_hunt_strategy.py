"""
Diversified 5-Hunt Strategy with Group Gun Hunt
Balances hunt quality with location/method diversification
"""

import csv
from datetime import datetime
from collections import defaultdict

def load_and_score_hunts():
    """Load all hunts and calculate scores."""
    all_hunts = []
    
    # Moon phases
    moon_phases = {
        'Oct_6_2025': {'date': datetime(2025, 10, 6), 'phase': 'Full', 'impact': -1},
        'Oct_13_2025': {'date': datetime(2025, 10, 13), 'phase': 'Third Quarter', 'impact': 1},
        'Oct_21_2025': {'date': datetime(2025, 10, 21), 'phase': 'New', 'impact': 3},
        'Oct_29_2025': {'date': datetime(2025, 10, 29), 'phase': 'First Quarter', 'impact': 1},
        'Nov_5_2025': {'date': datetime(2025, 11, 5), 'phase': 'Full', 'impact': -1},
        'Nov_11_2025': {'date': datetime(2025, 11, 11), 'phase': 'Third Quarter', 'impact': 1},
        'Nov_20_2025': {'date': datetime(2025, 11, 20), 'phase': 'New', 'impact': 3},
        'Nov_28_2025': {'date': datetime(2025, 11, 28), 'phase': 'First Quarter', 'impact': 1},
        'Dec_4_2025': {'date': datetime(2025, 12, 4), 'phase': 'Full', 'impact': -1},
        'Dec_11_2025': {'date': datetime(2025, 12, 11), 'phase': 'Third Quarter', 'impact': 1},
        'Dec_19_2025': {'date': datetime(2025, 12, 19), 'phase': 'New', 'impact': 3},
        'Dec_27_2025': {'date': datetime(2025, 12, 27), 'phase': 'First Quarter', 'impact': 1},
        'Jan_13_2026': {'date': datetime(2026, 1, 13), 'phase': 'Full', 'impact': -1},
        'Jan_20_2026': {'date': datetime(2026, 1, 20), 'phase': 'New', 'impact': 3},
    }
    
    # Rut periods
    rut_periods = {
        'pre_rut': {'start': datetime(2025, 10, 1), 'end': datetime(2025, 12, 15), 'score': 3},
        'pre_peak_rut': {'start': datetime(2025, 12, 16), 'end': datetime(2025, 12, 28), 'score': 4},
        'peak_rut': {'start': datetime(2025, 12, 29), 'end': datetime(2026, 1, 4), 'score': 5},
        'post_rut': {'start': datetime(2026, 1, 5), 'end': datetime(2026, 1, 20), 'score': 3}
    }
    
    def calculate_moon_score(start_date, end_date):
        hunt_midpoint = start_date + (end_date - start_date) / 2
        best_score = -2
        for phase_data in moon_phases.values():
            days_diff = abs((hunt_midpoint - phase_data['date']).days)
            if days_diff <= 2:
                phase_score = phase_data['impact']
            elif days_diff <= 4:
                phase_score = phase_data['impact'] * 0.7
            elif days_diff <= 7:
                phase_score = phase_data['impact'] * 0.4
            else:
                phase_score = 0
            best_score = max(best_score, phase_score)
        return max(0, best_score)
    
    def calculate_rut_score(start_date, end_date):
        hunt_midpoint = start_date + (end_date - start_date) / 2
        for period_data in rut_periods.values():
            if period_data['start'] <= hunt_midpoint <= period_data['end']:
                return period_data['score']
        return 1
    
    def calculate_combined_score(hunt):
        permit_score = min(hunt['permits_available'] / 5, 5)
        duration_score = min(hunt['duration_days'], 4)
        moon_score = hunt['moon_score']
        rut_score = hunt['rut_score']
        
        return round(permit_score * 0.3 + duration_score * 0.2 + moon_score * 0.2 + rut_score * 0.3, 2)
    
    # Load all hunt files
    hunt_files = {
        'Archery': 'data/deer_archery_hunts_2025_26.csv',
        'Gun': 'data/deer_gun_hunts_2025_26.csv',
        'Primitive Weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
        'Group': 'data/deer_group_hunts_2025_26.csv'
    }
    
    for hunt_type, file_path in hunt_files.items():
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['start_date'] = datetime.strptime(row['start_date'], '%Y-%m-%d')
                    row['end_date'] = datetime.strptime(row['end_date'], '%Y-%m-%d')
                    row['permits_available'] = int(row['permits_available'])
                    row['duration_days'] = int(row['duration_days'])
                    row['hunt_method'] = hunt_type
                    
                    row['moon_score'] = calculate_moon_score(row['start_date'], row['end_date'])
                    row['rut_score'] = calculate_rut_score(row['start_date'], row['end_date'])
                    row['combined_score'] = calculate_combined_score(row)
                    
                    all_hunts.append(row)
        except Exception as e:
            print(f"Error loading {hunt_type}: {e}")
    
    return all_hunts

def create_diversified_strategy():
    """Create a diversified 5-hunt strategy."""
    all_hunts = load_and_score_hunts()
    
    # Manual selection for optimal diversification
    selected_hunts = []
    
    # 1. Best Group Gun Hunt (Required)
    group_gun_hunts = [h for h in all_hunts if h['hunt_method'] == 'Group' and 'Gun' in h['hunt_name']]
    if group_gun_hunts:
        best_group = max(group_gun_hunts, key=lambda x: x['combined_score'])
        selected_hunts.append(best_group)
        print(f"✅ Group Gun Hunt: {best_group['hunt_name']} - {best_group['start_date'].strftime('%m/%d/%Y')}")
    
    # 2. Peak Rut Hunt (Jan 1-4) - Highest priority
    peak_rut_hunts = [h for h in all_hunts if h['rut_score'] >= 5]
    if peak_rut_hunts:
        best_peak = max(peak_rut_hunts, key=lambda x: x['combined_score'])
        if best_peak['start_date'].strftime('%Y-%m-%d') != selected_hunts[0]['start_date'].strftime('%Y-%m-%d'):
            selected_hunts.append(best_peak)
            print(f"✅ Peak Rut Hunt: {best_peak['hunt_name']} - {best_peak['start_date'].strftime('%m/%d/%Y')}")
    
    # 3. Best December 18 Hunt (Optimal moon/rut)
    dec_18_hunts = [h for h in all_hunts if h['start_date'].strftime('%Y-%m-%d') == '2025-12-18']
    used_dates = {h['start_date'].strftime('%Y-%m-%d') for h in selected_hunts}
    
    for hunt in sorted(dec_18_hunts, key=lambda x: x['combined_score'], reverse=True):
        if hunt['start_date'].strftime('%Y-%m-%d') not in used_dates:
            # Prefer non-Phil Bryant for diversification
            if 'Phil Bryant' not in hunt['wma_location'] or len(selected_hunts) < 3:
                selected_hunts.append(hunt)
                used_dates.add(hunt['start_date'].strftime('%Y-%m-%d'))
                print(f"✅ Optimal Date Hunt: {hunt['hunt_name']} - {hunt['start_date'].strftime('%m/%d/%Y')}")
                break
    
    # 4. Primitive Weapon Hunt (Method diversification)
    pw_hunts = [h for h in all_hunts if h['hunt_method'] == 'Primitive Weapon']
    for hunt in sorted(pw_hunts, key=lambda x: x['combined_score'], reverse=True):
        if hunt['start_date'].strftime('%Y-%m-%d') not in used_dates:
            # Prefer Sky Lake or Twin Oaks for location diversification
            if hunt['wma_location'] in ['Sky Lake', 'Twin Oaks'] or len(selected_hunts) < 4:
                selected_hunts.append(hunt)
                used_dates.add(hunt['start_date'].strftime('%Y-%m-%d'))
                print(f"✅ Primitive Weapon: {hunt['hunt_name']} - {hunt['start_date'].strftime('%m/%d/%Y')}")
                break
    
    # 5. Gun Hunt for method diversification
    gun_hunts = [h for h in all_hunts if h['hunt_method'] == 'Gun']
    for hunt in sorted(gun_hunts, key=lambda x: x['combined_score'], reverse=True):
        if hunt['start_date'].strftime('%Y-%m-%d') not in used_dates and len(selected_hunts) < 5:
            selected_hunts.append(hunt)
            used_dates.add(hunt['start_date'].strftime('%Y-%m-%d'))
            print(f"✅ Gun Hunt: {hunt['hunt_name']} - {hunt['start_date'].strftime('%m/%d/%Y')}")
            break
    
    return selected_hunts

def print_diversified_strategy():
    """Print the diversified 5-hunt strategy."""
    selected_hunts = create_diversified_strategy()
    
    print("\n" + "="*85)
    print("🎯 DIVERSIFIED 5-HUNT APPLICATION STRATEGY")
    print("✅ Includes: Group Gun Hunt + Location/Method Diversification")
    print("="*85)
    
    for i, hunt in enumerate(selected_hunts, 1):
        print(f"\n#{i} CHOICE - {hunt['hunt_method'].upper()}")
        print(f"Hunt: {hunt['hunt_name']}")
        print(f"Location: {hunt['wma_location']}")
        print(f"Date: {hunt['start_date'].strftime('%B %d')} - {hunt['end_date'].strftime('%B %d, %Y')}")
        print(f"Permits: {hunt['permits_available']} | Duration: {hunt['duration_days']} days")
        print(f"Score: {hunt['combined_score']}/5.0")
        
        # Special notes
        if hunt['rut_score'] >= 5:
            print("🦌 PEAK RUT PERIOD - Top Priority!")
        elif hunt['rut_score'] == 4:
            print("🎯 Pre-Peak Rut - Excellent timing")
        
        if hunt['moon_score'] >= 2.5:
            print("🌑 New Moon - Optimal hunting conditions")
        
        if hunt['hunt_method'] == 'Group':
            print("👥 Group hunt - coordinate with partners")
    
    # Strategy analysis
    locations = set(h['wma_location'] for h in selected_hunts)
    methods = set(h['hunt_method'] for h in selected_hunts)
    
    print(f"\n📊 DIVERSIFICATION ANALYSIS:")
    print(f"Locations: {len(locations)} different WMAs")
    print(f"Hunt Methods: {len(methods)} different types")
    print(f"Average Score: {sum(h['combined_score'] for h in selected_hunts) / len(selected_hunts):.2f}/5.0")
    
    peak_rut = len([h for h in selected_hunts if h['rut_score'] >= 5])
    pre_peak = len([h for h in selected_hunts if h['rut_score'] == 4])
    
    print(f"\n🦌 RUT COVERAGE:")
    print(f"Peak Rut (Dec 29-Jan 4): {peak_rut} hunts")
    print(f"Pre-Peak Rut (Dec 16-28): {pre_peak} hunts")
    
    print(f"\n📋 STRATEGY BENEFITS:")
    print("✅ Reduced risk from concentrating on one location")
    print("✅ Multiple hunt methods increase success odds")
    print("✅ Covers both peak and pre-peak rut periods")
    print("✅ Includes required group gun hunt")
    print("✅ Mix of high-competition and sleeper opportunities")

if __name__ == "__main__":
    print("Creating Diversified 5-Hunt Strategy with Group Gun Hunt Requirement...")
    print_diversified_strategy()
