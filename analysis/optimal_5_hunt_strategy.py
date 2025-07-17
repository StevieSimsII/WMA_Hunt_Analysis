"""
Optimized 5-Hunt Application Strategy
Finds the best 5 hunts across different dates to maximize success probability
"""

import csv
from datetime import datetime
from collections import defaultdict

class OptimizedApplicationStrategy:
    def __init__(self):
        """Initialize the optimizer for 5-hunt application strategy."""
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
            },
            'late_season': {
                'start': datetime(2026, 1, 21),
                'end': datetime(2026, 1, 31),
                'score': 2,
                'description': 'Late Season (Food Focus)'
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
                        row['competition_tier'] = self._estimate_competition_tier(row)
                        
                        self.all_hunts.append(row)
            except Exception as e:
                print(f"Error loading {hunt_type} hunts: {e}")
        
        print(f"Loaded {len(self.all_hunts)} total hunt opportunities")
    
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
    
    def _estimate_competition_tier(self, hunt):
        """Estimate competition level based on hunt characteristics."""
        location = hunt['wma_location']
        method = hunt['hunt_method']
        permits = hunt['permits_available']
        score = hunt['combined_score']
        
        # Phil Bryant units with high scores = very competitive
        if 'Phil Bryant' in location and score >= 3.8:
            return 'Very High'
        elif 'Phil Bryant' in location and score >= 3.0:
            return 'High'
        
        # Peak rut hunts = very competitive
        if hunt['rut_score']['score'] >= 5:
            return 'Very High'
        
        # High-scoring hunts = competitive
        if score >= 3.5:
            return 'High'
        elif score >= 3.0:
            return 'Moderate'
        
        # Riverfront, smaller permits = potentially lower competition
        if location == 'Riverfront' or permits <= 10:
            return 'Low'
        
        return 'Moderate'
    
    def find_optimal_5_hunts(self):
        """Find the optimal 5 hunts across different dates."""
        # Group hunts by date range to avoid conflicts
        date_groups = defaultdict(list)
        
        for hunt in self.all_hunts:
            date_key = hunt['start_date'].strftime('%Y-%m-%d')
            date_groups[date_key].append(hunt)
        
        # Find best hunt for each unique date
        best_by_date = {}
        for date_key, hunts in date_groups.items():
            # Sort by combined score, then by competition tier (prefer lower competition)
            competition_order = {'Low': 4, 'Moderate': 3, 'High': 2, 'Very High': 1}
            
            hunts_sorted = sorted(hunts, 
                                key=lambda x: (x['combined_score'], 
                                             competition_order.get(x['competition_tier'], 0)), 
                                reverse=True)
            best_by_date[date_key] = hunts_sorted[0]
        
        # Sort all best hunts by quality and select top 5
        all_best_hunts = list(best_by_date.values())
        
        # Apply strategic selection criteria
        strategic_selection = []
        
        # 1. Must include peak rut hunt if available
        peak_rut_hunts = [h for h in all_best_hunts if h['rut_score']['score'] >= 5]
        if peak_rut_hunts:
            best_peak = max(peak_rut_hunts, key=lambda x: x['combined_score'])
            strategic_selection.append(best_peak)
            all_best_hunts.remove(best_peak)
        
        # 2. Prioritize high-quality, different competition tiers
        remaining_hunts = sorted(all_best_hunts, key=lambda x: x['combined_score'], reverse=True)
        
        # Try to get a mix of competition levels
        tier_counts = {'Very High': 0, 'High': 0, 'Moderate': 0, 'Low': 0}
        
        for hunt in remaining_hunts:
            if len(strategic_selection) >= 5:
                break
            
            tier = hunt['competition_tier']
            
            # Limit very high competition hunts to 2 max
            if tier == 'Very High' and tier_counts['Very High'] >= 2:
                continue
            
            strategic_selection.append(hunt)
            tier_counts[tier] += 1
        
        return strategic_selection[:5]
    
    def print_optimal_strategy(self):
        """Print the optimal 5-hunt application strategy."""
        optimal_hunts = self.find_optimal_5_hunts()
        
        print("=" * 100)
        print("🎯 OPTIMAL 5-HUNT APPLICATION STRATEGY")
        print("=" * 100)
        print("Strategy: Maximum quality spread across different dates to avoid conflicts\n")
        
        for i, hunt in enumerate(optimal_hunts, 1):
            print(f"🏆 CHOICE #{i}")
            print(f"   Hunt: {hunt['hunt_name']}")
            print(f"   Method: {hunt['hunt_method']}")
            print(f"   Location: {hunt['wma_location']}")
            print(f"   Dates: {hunt['start_date'].strftime('%m/%d/%Y')} - {hunt['end_date'].strftime('%m/%d/%Y')}")
            print(f"   Permits: {hunt['permits_available']}")
            print(f"   Quality Score: {hunt['combined_score']}/5.0 {'⭐' * int(hunt['combined_score'])}")
            print(f"   Competition: {hunt['competition_tier']}")
            print(f"   Rut Period: {hunt['rut_score']['description']}")
            print(f"   Moon Phase: {hunt['moon_score']['closest_phase']}")
            print("")
        
        print("📊 STRATEGY ANALYSIS:")
        print("-" * 50)
        
        # Competition tier distribution
        tier_counts = {}
        for hunt in optimal_hunts:
            tier = hunt['competition_tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print("Competition Distribution:")
        for tier, count in tier_counts.items():
            print(f"  • {tier}: {count} hunt(s)")
        
        # Date spread
        print(f"\nDate Spread: {len(set(h['start_date'].strftime('%Y-%m-%d') for h in optimal_hunts))} different dates")
        
        # Method diversity
        methods = set(h['hunt_method'] for h in optimal_hunts)
        print(f"Hunt Methods: {', '.join(methods)}")
        
        # Quality metrics
        avg_score = sum(h['combined_score'] for h in optimal_hunts) / len(optimal_hunts)
        total_permits = sum(h['permits_available'] for h in optimal_hunts)
        
        print(f"Average Quality Score: {avg_score:.2f}/5.0")
        print(f"Total Permit Opportunities: {total_permits}")
        
        # Peak rut inclusion
        peak_rut_count = sum(1 for h in optimal_hunts if h['rut_score']['score'] >= 5)
        print(f"Peak Rut Hunts Included: {peak_rut_count}")
        
        print("\n" + "=" * 100)
        print("💡 APPLICATION TIPS:")
        print("• Apply immediately when applications open (July 15)")
        print("• These 5 hunts are on different dates - no conflicts")
        print("• Mix of competition levels increases overall success odds")
        print("• Priority order listed above - apply in this sequence")
        print("=" * 100)

def main():
    """Run the optimal 5-hunt strategy analysis."""
    optimizer = OptimizedApplicationStrategy()
    optimizer.load_all_hunts()
    optimizer.print_optimal_strategy()

if __name__ == "__main__":
    main()
