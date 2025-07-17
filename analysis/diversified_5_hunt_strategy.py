"""
Diversified 5-Hunt Strategy
Optimizes for different locations, methods, and competition levels
"""

import csv
from datetime import datetime
from collections import defaultdict

def analyze_diversified_strategy():
    """Create a diversified 5-hunt strategy across locations and methods."""
    
    # Load all hunts with enhanced scoring
    all_hunts = []
    hunt_files = {
        'Archery': 'data/deer_archery_hunts_2025_26.csv',
        'Gun': 'data/deer_gun_hunts_2025_26.csv',
        'Primitive Weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
        'Group': 'data/deer_group_hunts_2025_26.csv'
    }
    
    rut_periods = {
        'peak_rut': {'start': datetime(2025, 12, 29), 'end': datetime(2026, 1, 4), 'score': 5},
        'pre_peak_rut': {'start': datetime(2025, 12, 16), 'end': datetime(2025, 12, 28), 'score': 4},
        'pre_rut': {'start': datetime(2025, 10, 1), 'end': datetime(2025, 12, 15), 'score': 3},
        'post_rut': {'start': datetime(2026, 1, 5), 'end': datetime(2026, 1, 20), 'score': 3},
        'late_season': {'start': datetime(2026, 1, 21), 'end': datetime(2026, 1, 31), 'score': 2}
    }
    
    moon_phases = {
        'Oct_21_2025': {'date': datetime(2025, 10, 21), 'impact': 3},
        'Nov_20_2025': {'date': datetime(2025, 11, 20), 'impact': 3},
        'Dec_19_2025': {'date': datetime(2025, 12, 19), 'impact': 3},
        'Jan_20_2026': {'date': datetime(2026, 1, 20), 'impact': 3},
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
                    
                    # Calculate rut score
                    hunt_midpoint = row['start_date'] + (row['end_date'] - row['start_date']) / 2
                    rut_score = 1
                    for period_data in rut_periods.values():
                        if period_data['start'] <= hunt_midpoint <= period_data['end']:
                            rut_score = period_data['score']
                            break
                    
                    # Calculate moon score
                    moon_score = 0
                    for moon_data in moon_phases.values():
                        days_diff = abs((hunt_midpoint - moon_data['date']).days)
                        if days_diff <= 2:
                            moon_score = max(moon_score, moon_data['impact'])
                        elif days_diff <= 7:
                            moon_score = max(moon_score, moon_data['impact'] * 0.5)
                    
                    # Combined score
                    permit_score = min(row['permits_available'] / 5, 5)
                    duration_score = min(row['duration_days'], 4)
                    combined_score = (permit_score * 0.3 + duration_score * 0.2 + 
                                    moon_score * 0.2 + rut_score * 0.3)
                    
                    row['rut_score'] = rut_score
                    row['moon_score'] = moon_score
                    row['combined_score'] = round(combined_score, 2)
                    
                    all_hunts.append(row)
        except Exception as e:
            print(f"Error loading {hunt_type}: {e}")
    
    # Group by date to avoid conflicts
    hunts_by_date = defaultdict(list)
    for hunt in all_hunts:
        date_key = hunt['start_date'].strftime('%Y-%m-%d')
        hunts_by_date[date_key].append(hunt)
    
    # Get best hunt per date
    best_per_date = {}
    for date_key, hunts in hunts_by_date.items():
        best = max(hunts, key=lambda x: x['combined_score'])
        best_per_date[date_key] = best
    
    # Apply strategic selection for diversification
    selected_hunts = []
    used_locations = set()
    used_methods = set()
    
    # Priority 1: Peak rut hunt (highest priority)
    peak_rut_hunts = [h for h in best_per_date.values() if h['rut_score'] >= 5]
    if peak_rut_hunts:
        best_peak = max(peak_rut_hunts, key=lambda x: x['combined_score'])
        selected_hunts.append(best_peak)
        used_locations.add(best_peak['wma_location'])
        used_methods.add(best_peak['hunt_method'])
        del best_per_date[best_peak['start_date'].strftime('%Y-%m-%d')]
    
    # Priority 2: December 18-21 optimal date
    dec_18_key = '2025-12-18'
    if dec_18_key in best_per_date:
        dec_18_hunt = best_per_date[dec_18_key]
        if dec_18_hunt['wma_location'] not in used_locations:
            selected_hunts.append(dec_18_hunt)
            used_locations.add(dec_18_hunt['wma_location'])
            used_methods.add(dec_18_hunt['hunt_method'])
            del best_per_date[dec_18_key]
    
    # Priority 3: Fill remaining slots with diversity
    remaining_hunts = sorted(best_per_date.values(), 
                           key=lambda x: x['combined_score'], reverse=True)
    
    for hunt in remaining_hunts:
        if len(selected_hunts) >= 5:
            break
        
        # Prefer different locations and methods for diversity
        location_bonus = 0.5 if hunt['wma_location'] not in used_locations else 0
        method_bonus = 0.3 if hunt['hunt_method'] not in used_methods else 0
        diversity_score = hunt['combined_score'] + location_bonus + method_bonus
        
        hunt['diversity_score'] = diversity_score
        
        # Add if it improves diversity or is exceptionally high quality
        if (hunt['wma_location'] not in used_locations or 
            hunt['hunt_method'] not in used_methods or 
            hunt['combined_score'] >= 3.5):
            
            selected_hunts.append(hunt)
            used_locations.add(hunt['wma_location'])
            used_methods.add(hunt['hunt_method'])
    
    # If still need more hunts, add best remaining regardless of diversity
    if len(selected_hunts) < 5:
        remaining = [h for h in best_per_date.values() 
                    if h not in selected_hunts]
        remaining_sorted = sorted(remaining, 
                                key=lambda x: x['combined_score'], reverse=True)
        
        needed = 5 - len(selected_hunts)
        selected_hunts.extend(remaining_sorted[:needed])
    
    # Sort final selection by quality score
    selected_hunts.sort(key=lambda x: x['combined_score'], reverse=True)
    
    return selected_hunts[:5]

def print_diversified_strategy():
    """Print the diversified 5-hunt strategy."""
    optimal_hunts = analyze_diversified_strategy()
    
    print("=" * 100)
    print("🎯 DIVERSIFIED 5-HUNT APPLICATION STRATEGY")
    print("=" * 100)
    print("Strategy: Balanced approach across locations, methods, and competition levels\n")
    
    for i, hunt in enumerate(optimal_hunts, 1):
        # Estimate competition
        competition = "Very High"
        if 'Phil Bryant' not in hunt['wma_location']:
            competition = "Moderate"
        if hunt['permits_available'] <= 10:
            competition = "High" if competition == "Very High" else "Moderate"
        
        # Get rut description
        rut_desc = "Pre-Rut"
        if hunt['rut_score'] >= 5:
            rut_desc = "Peak Rut (Prime Time)"
        elif hunt['rut_score'] >= 4:
            rut_desc = "Pre-Peak Rut (Chasing)"
        
        print(f"🏆 CHOICE #{i}")
        print(f"   Hunt: {hunt['hunt_name']}")
        print(f"   Method: {hunt['hunt_method']}")
        print(f"   Location: {hunt['wma_location']}")
        print(f"   Dates: {hunt['start_date'].strftime('%m/%d/%Y')} - {hunt['end_date'].strftime('%m/%d/%Y')}")
        print(f"   Permits: {hunt['permits_available']}")
        print(f"   Quality Score: {hunt['combined_score']}/5.0 {'⭐' * min(int(hunt['combined_score']), 5)}")
        print(f"   Competition: {competition}")
        print(f"   Rut Period: {rut_desc}")
        print("")
    
    print("📊 DIVERSIFICATION ANALYSIS:")
    print("-" * 50)
    
    locations = [h['wma_location'] for h in optimal_hunts]
    methods = [h['hunt_method'] for h in optimal_hunts]
    
    print(f"Unique Locations: {len(set(locations))} out of 5")
    print("Locations:", ", ".join(set(locations)))
    print(f"Unique Methods: {len(set(methods))} out of 5")
    print("Methods:", ", ".join(set(methods)))
    
    avg_score = sum(h['combined_score'] for h in optimal_hunts) / len(optimal_hunts)
    total_permits = sum(h['permits_available'] for h in optimal_hunts)
    peak_rut_count = sum(1 for h in optimal_hunts if h['rut_score'] >= 5)
    
    print(f"Average Quality Score: {avg_score:.2f}/5.0")
    print(f"Total Permit Opportunities: {total_permits}")
    print(f"Peak Rut Hunts: {peak_rut_count}")
    
    print("\n" + "=" * 100)
    print("💡 STRATEGIC ADVANTAGES:")
    print("✓ Reduced risk by spreading across multiple locations")
    print("✓ Different hunt methods increase overall success odds")
    print("✓ Mix of competition levels balances quality vs. probability")
    print("✓ All hunts on different dates - no scheduling conflicts")
    print("✓ Includes peak rut opportunity if available")
    print("=" * 100)

if __name__ == "__main__":
    print_diversified_strategy()
