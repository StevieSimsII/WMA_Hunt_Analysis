"""
Optimized 5-Hunt Application Strategy with Group Gun Hunt Requirement
Finds the best 5 hunts on different dates with at least one group gun hunt
"""

import csv
from datetime import datetime
from collections import defaultdict

class FiveHuntOptimizer:
    def __init__(self):
        """Initialize the 5-hunt optimizer."""
        self.all_hunts = []
        self.moon_phases = self._load_moon_phases()
        self.rut_periods = self._load_rut_periods()
        
    def _load_moon_phases(self):
        """Load 2025-2026 moon phase data for analysis."""
        return {
            # October 2025
            'Oct_6_2025': {'date': datetime(2025, 10, 6), 'phase': 'Full', 'impact': -1},
            'Oct_13_2025': {'date': datetime(2025, 10, 13), 'phase': 'Third Quarter', 'impact': 1},
            'Oct_21_2025': {'date': datetime(2025, 10, 21), 'phase': 'New', 'impact': 3},
            'Oct_29_2025': {'date': datetime(2025, 10, 29), 'phase': 'First Quarter', 'impact': 1},
            
            # November 2025
            'Nov_5_2025': {'date': datetime(2025, 11, 5), 'phase': 'Full', 'impact': -1},
            'Nov_11_2025': {'date': datetime(2025, 11, 11), 'phase': 'Third Quarter', 'impact': 1},
            'Nov_20_2025': {'date': datetime(2025, 11, 20), 'phase': 'New', 'impact': 3},
            'Nov_28_2025': {'date': datetime(2025, 11, 28), 'phase': 'First Quarter', 'impact': 1},
            
            # December 2025
            'Dec_4_2025': {'date': datetime(2025, 12, 4), 'phase': 'Full', 'impact': -1},
            'Dec_11_2025': {'date': datetime(2025, 12, 11), 'phase': 'Third Quarter', 'impact': 1},
            'Dec_19_2025': {'date': datetime(2025, 12, 19), 'phase': 'New', 'impact': 3},
            'Dec_27_2025': {'date': datetime(2025, 12, 27), 'phase': 'First Quarter', 'impact': 1},
            
            # January 2026
            'Jan_13_2026': {'date': datetime(2026, 1, 13), 'phase': 'Full', 'impact': -1},
            'Jan_20_2026': {'date': datetime(2026, 1, 20), 'phase': 'New', 'impact': 3},
        }
    
    def _load_rut_periods(self):
        """Load Yazoo County, Mississippi deer rut timing data."""
        return {
            'pre_rut': {
                'start': datetime(2025, 10, 1),
                'end': datetime(2025, 12, 15),
                'score': 3,
                'description': 'Pre-Rut (Building Activity)'
            },
            'pre_peak_rut': {
                'start': datetime(2025, 12, 16),
                'end': datetime(2025, 12, 28),
                'score': 4,
                'description': 'Pre-Peak Rut (Chasing Activity)'
            },
            'peak_rut': {
                'start': datetime(2025, 12, 29),
                'end': datetime(2026, 1, 4),
                'score': 5,
                'description': 'Peak Rut (Prime Time)'
            },
            'post_rut': {
                'start': datetime(2026, 1, 5),
                'end': datetime(2026, 1, 20),
                'score': 3,
                'description': 'Post-Rut (Recovery Period)'
            }
        }
    
    def load_all_hunts(self):
        """Load all hunt data from CSV files."""
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
                        
                        # Add enhanced scoring
                        row['moon_score'] = self._calculate_moon_score(row['start_date'], row['end_date'])
                        row['rut_score'] = self._calculate_rut_score(row['start_date'], row['end_date'])
                        row['combined_score'] = self._calculate_combined_score(row)
                        
                        self.all_hunts.append(row)
                        
                print(f"Loaded {hunt_type} hunts from {file_path}")
            except Exception as e:
                print(f"Error loading {hunt_type} hunts: {e}")
        
        print(f"Total hunts loaded: {len(self.all_hunts)}")
    
    def _calculate_moon_score(self, start_date, end_date):
        """Calculate moon phase impact score for hunt dates."""
        hunt_midpoint = start_date + (end_date - start_date) / 2
        
        best_score = -2  # Worst case (full moon)
        closest_phase = None
        
        for phase_key, phase_data in self.moon_phases.items():
            moon_date = phase_data['date']
            days_diff = abs((hunt_midpoint - moon_date).days)
            
            # Moon phase impact decreases with distance
            if days_diff <= 2:
                phase_score = phase_data['impact']
            elif days_diff <= 4:
                phase_score = phase_data['impact'] * 0.7
            elif days_diff <= 7:
                phase_score = phase_data['impact'] * 0.4
            else:
                phase_score = 0
            
            if phase_score > best_score:
                best_score = phase_score
                closest_phase = phase_data['phase']
        
        return {
            'score': round(best_score, 1),
            'closest_phase': closest_phase
        }
    
    def _calculate_rut_score(self, start_date, end_date):
        """Calculate rut timing score for hunt dates."""
        hunt_midpoint = start_date + (end_date - start_date) / 2
        
        for period_name, period_data in self.rut_periods.items():
            if period_data['start'] <= hunt_midpoint <= period_data['end']:
                return {
                    'score': period_data['score'],
                    'period': period_name,
                    'description': period_data['description']
                }
        
        return {
            'score': 1,
            'period': 'transition',
            'description': 'Transition Period'
        }
    
    def _calculate_combined_score(self, hunt):
        """Calculate overall hunt quality score."""
        # Base factors
        permit_score = min(hunt['permits_available'] / 5, 5)  # Max 5 points for permits
        duration_score = min(hunt['duration_days'], 4)  # Max 4 points for duration
        
        # Enhanced factors
        moon_score = hunt['moon_score']['score'] if hunt['moon_score']['score'] > 0 else 0
        rut_score = hunt['rut_score']['score']
        
        # Weights
        total_score = (
            permit_score * 0.3 +  # 30% permits
            duration_score * 0.2 +  # 20% duration
            moon_score * 0.2 +  # 20% moon phase
            rut_score * 0.3  # 30% rut timing
        )
        
        return round(total_score, 2)
    
    def find_optimal_5_hunts_with_group_gun(self):
        """Find the optimal 5 hunts with at least one group gun hunt."""
        
        # First, identify group gun hunts
        group_gun_hunts = [h for h in self.all_hunts 
                          if h['hunt_method'] == 'Group' and 'Gun' in h['hunt_name']]
        
        if not group_gun_hunts:
            print("❌ No group gun hunts found!")
            return []
        
        # Sort group gun hunts by score
        group_gun_hunts.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Select the best group gun hunt
        best_group_gun = group_gun_hunts[0]
        selected_hunts = [best_group_gun]
        used_dates = {best_group_gun['start_date'].strftime('%Y-%m-%d')}
        
        print(f"🎯 Selected Group Gun Hunt: {best_group_gun['hunt_name']}")
        print(f"   Date: {best_group_gun['start_date'].strftime('%Y-%m-%d')}")
        print(f"   Score: {best_group_gun['combined_score']}")
        
        # Now find 4 more hunts on different dates
        other_hunts = [h for h in self.all_hunts if h != best_group_gun]
        other_hunts.sort(key=lambda x: x['combined_score'], reverse=True)
        
        for hunt in other_hunts:
            if len(selected_hunts) >= 5:
                break
                
            hunt_date = hunt['start_date'].strftime('%Y-%m-%d')
            if hunt_date not in used_dates:
                selected_hunts.append(hunt)
                used_dates.add(hunt_date)
        
        return selected_hunts
    
    def print_optimal_strategy(self):
        """Print the optimal 5-hunt strategy."""
        optimal_hunts = self.find_optimal_5_hunts_with_group_gun()
        
        if not optimal_hunts:
            print("❌ Could not find optimal hunt combination")
            return
        
        print("\n" + "="*80)
        print("🎯 OPTIMAL 5-HUNT APPLICATION STRATEGY")
        print("Requirement: At least 1 Group Gun Hunt + Different Dates")
        print("="*80)
        
        total_score = 0
        for i, hunt in enumerate(optimal_hunts, 1):
            total_score += hunt['combined_score']
            
            print(f"\n#{i} CHOICE - {hunt['hunt_method'].upper()}")
            print(f"Hunt: {hunt['hunt_name']}")
            print(f"Location: {hunt['wma_location']}")
            print(f"Date: {hunt['start_date'].strftime('%B %d, %Y')} - {hunt['end_date'].strftime('%B %d, %Y')}")
            print(f"Permits: {hunt['permits_available']} | Duration: {hunt['duration_days']} days")
            print(f"Score: {hunt['combined_score']}/5.0 ⭐")
            print(f"Rut Period: {hunt['rut_score']['description']}")
            print(f"Moon Phase: {hunt['moon_score']['closest_phase']}")
            
            # Strategy notes
            if hunt['hunt_method'] == 'Group':
                print("📝 Note: Group hunt - apply with hunting partners")
            if hunt['rut_score']['score'] >= 5:
                print("🦌 Note: PEAK RUT PERIOD - Highest priority!")
            if hunt['combined_score'] >= 4.0:
                print("⭐ Note: Premium hunt - expect high competition")
            elif hunt['combined_score'] >= 3.5:
                print("👍 Note: High-quality hunt - good balance")
            else:
                print("💡 Note: Strategic choice - potentially lower competition")
        
        avg_score = total_score / len(optimal_hunts)
        print(f"\n📊 STRATEGY SUMMARY:")
        print(f"Average Hunt Score: {avg_score:.2f}/5.0")
        print(f"Total Permits: {sum(h['permits_available'] for h in optimal_hunts)}")
        print(f"Hunt Methods: {', '.join(set(h['hunt_method'] for h in optimal_hunts))}")
        print(f"Locations: {', '.join(set(h['wma_location'] for h in optimal_hunts))}")
        
        # Date spread analysis
        dates = [h['start_date'] for h in optimal_hunts]
        date_range = max(dates) - min(dates)
        print(f"Date Range: {date_range.days} days")
        
        peak_rut_hunts = len([h for h in optimal_hunts if h['rut_score']['score'] >= 5])
        pre_peak_hunts = len([h for h in optimal_hunts if h['rut_score']['score'] == 4])
        
        print(f"\n🦌 RUT TIMING COVERAGE:")
        print(f"Peak Rut Hunts: {peak_rut_hunts}")
        print(f"Pre-Peak Rut Hunts: {pre_peak_hunts}")
        print(f"Other Periods: {5 - peak_rut_hunts - pre_peak_hunts}")
        
        print("\n✅ APPLICATION CHECKLIST:")
        print("1. Apply on July 15 when applications open")
        print("2. Ensure WMA User Permit is current")
        print("3. Coordinate with hunting partners for group hunt")
        print("4. Have backup gear for different hunt methods")
        print("5. Mark all hunt dates on calendar")

def main():
    """Run the 5-hunt optimizer with group gun requirement."""
    print("Mississippi WMA Draw Hunt - Optimal 5-Hunt Strategy")
    print("Requirement: At least 1 Group Gun Hunt + All Different Dates\n")
    
    optimizer = FiveHuntOptimizer()
    optimizer.load_all_hunts()
    optimizer.print_optimal_strategy()

if __name__ == "__main__":
    main()
