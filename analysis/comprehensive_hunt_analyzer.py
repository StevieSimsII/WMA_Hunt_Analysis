"""
Comprehensive Mississippi WMA Draw Hunt Analysis Tool
Compares Archery, Gun, Primitive Weapon, and Group hunts for Yazoo County timing
"""

import csv
from datetime import datetime
from collections import defaultdict

class ComprehensiveHuntAnalyzer:
    def __init__(self):
        """Initialize the analyzer."""
        self.hunts = {
            'archery': [],
            'gun': [],
            'primitive_weapon': [],
            'group': []
        }
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
    
    def load_hunt_data(self, hunt_type, file_path):
        """Load hunt data from CSV file for specific hunt type."""
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
                    
                    self.hunts[hunt_type].append(row)
            print(f"Loaded {len(self.hunts[hunt_type])} {hunt_type} hunt opportunities")
        except Exception as e:
            print(f"Error loading {hunt_type} data: {e}")
    
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
                phase_score = 0  # Neutral impact
            
            if phase_score > best_score:
                best_score = phase_score
                closest_phase = phase_data['phase']
        
        return best_score, closest_phase
    
    def _calculate_rut_score(self, start_date, end_date):
        """Calculate rut timing score for hunt dates."""
        hunt_midpoint = start_date + (end_date - start_date) / 2
        
        for period_name, period_data in self.rut_periods.items():
            if period_data['start'] <= hunt_midpoint <= period_data['end']:
                return period_data['score'], period_data['description']
        
        return 1, 'Unknown Period'  # Default for dates outside defined periods
    
    def _calculate_combined_score(self, hunt):
        """Calculate weighted combined score for hunt opportunity."""
        moon_score, _ = hunt['moon_score']
        rut_score, _ = hunt['rut_score']
        
        # Normalize permits (higher is better, cap at reasonable maximum)
        permit_score = min(hunt['permits_available'] / 25.0 * 5, 5)
        
        # Duration score (longer hunts get slight bonus, but cap benefit)
        duration_score = min(hunt['duration_days'] / 4.0 * 3 + 2, 5)
        
        # Weighted combination: 30% rut, 30% permits, 20% moon, 20% duration
        combined = (rut_score * 0.3 + permit_score * 0.3 + 
                   (moon_score + 2) * 0.2 + duration_score * 0.2)
        
        return round(combined, 2)
    
    def get_all_hunts_combined(self):
        """Get all hunts from all types combined and sorted by score."""
        all_hunts = []
        for hunt_type, hunts in self.hunts.items():
            all_hunts.extend(hunts)
        
        return sorted(all_hunts, key=lambda x: x['combined_score'], reverse=True)
    
    def get_peak_rut_hunts(self):
        """Get hunts during peak rut period (Dec 29 - Jan 4)."""
        peak_hunts = []
        for hunt_type, hunts in self.hunts.items():
            for hunt in hunts:
                _, rut_period = hunt['rut_score']
                if 'Peak Rut' in rut_period:
                    peak_hunts.append(hunt)
        
        return sorted(peak_hunts, key=lambda x: x['combined_score'], reverse=True)
    
    def get_pre_peak_hunts(self):
        """Get hunts during pre-peak rut period (Dec 16-28)."""
        pre_peak_hunts = []
        for hunt_type, hunts in self.hunts.items():
            for hunt in hunts:
                _, rut_period = hunt['rut_score']
                if 'Pre-Peak Rut' in rut_period:
                    pre_peak_hunts.append(hunt)
        
        return sorted(pre_peak_hunts, key=lambda x: x['combined_score'], reverse=True)
    
    def analyze_by_method(self):
        """Analyze hunt opportunities by method type."""
        method_analysis = {}
        
        for hunt_type, hunts in self.hunts.items():
            if not hunts:
                continue
                
            scores = [hunt['combined_score'] for hunt in hunts]
            permits = [hunt['permits_available'] for hunt in hunts]
            
            # Find peak and pre-peak opportunities
            peak_hunts = [h for h in hunts if 'Peak Rut' in h['rut_score'][1]]
            pre_peak_hunts = [h for h in hunts if 'Pre-Peak Rut' in h['rut_score'][1]]
            
            method_analysis[hunt_type] = {
                'total_hunts': len(hunts),
                'avg_score': round(sum(scores) / len(scores), 2),
                'max_score': max(scores),
                'total_permits': sum(permits),
                'avg_permits': round(sum(permits) / len(permits), 1),
                'peak_rut_hunts': len(peak_hunts),
                'pre_peak_hunts': len(pre_peak_hunts),
                'top_hunt': max(hunts, key=lambda x: x['combined_score'])
            }
        
        return method_analysis

def print_hunt_table(hunts, title, limit=10):
    """Print formatted table of hunt opportunities."""
    print(f"\n🎯 {title}")
    print("=" * 120)
    
    headers = ['hunt_name', 'method', 'location', 'start_date', 'permits', 'score', 'rut_period']
    
    # Print header
    print(f"{'Hunt Name':<35} | {'Method':<8} | {'Location':<25} | {'Date':<10} | {'Permits':<7} | {'Score':<5} | {'Rut Period':<25}")
    print("-" * 120)
    
    # Print rows
    for i, hunt in enumerate(hunts[:limit]):
        hunt_name = hunt['hunt_name'][:34]
        method = hunt['hunt_method'].title()[:7]
        location = hunt['wma_location'][:24]
        date = hunt['start_date'].strftime('%m/%d')
        permits = str(hunt['permits_available'])
        score = str(hunt['combined_score'])
        rut_period = hunt['rut_score'][1][:24]
        
        print(f"{hunt_name:<35} | {method:<8} | {location:<25} | {date:<10} | {permits:<7} | {score:<5} | {rut_period:<25}")

def main():
    """Main analysis function."""
    print("=== COMPREHENSIVE MISSISSIPPI WMA DRAW HUNT ANALYSIS ===")
    print("Yazoo County Rut Timing: Peak Dec 29 - Jan 4\n")
    
    analyzer = ComprehensiveHuntAnalyzer()
    
    # Load all hunt types
    data_files = {
        'archery': 'data/deer_archery_hunts_2025_26.csv',
        'gun': 'data/deer_gun_hunts_2025_26.csv', 
        'primitive_weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
        'group': 'data/deer_group_hunts_2025_26.csv'
    }
    
    for hunt_type, file_path in data_files.items():
        analyzer.load_hunt_data(hunt_type, file_path)
    
    # Overall top opportunities
    all_hunts = analyzer.get_all_hunts_combined()
    print_hunt_table(all_hunts, "TOP 15 OPPORTUNITIES - ALL HUNT TYPES", 15)
    
    # Peak rut analysis
    peak_hunts = analyzer.get_peak_rut_hunts()
    print_hunt_table(peak_hunts, "PEAK RUT HUNTS (Dec 29 - Jan 4)", 10)
    
    # Pre-peak rut analysis
    pre_peak_hunts = analyzer.get_pre_peak_hunts()
    print_hunt_table(pre_peak_hunts, "PRE-PEAK RUT HUNTS (Dec 16-28)", 10)
    
    # Method comparison
    method_analysis = analyzer.analyze_by_method()
    
    print(f"\n📊 HUNT METHOD COMPARISON")
    print("=" * 100)
    print(f"{'Method':<15} | {'Hunts':<6} | {'Avg Score':<9} | {'Max Score':<9} | {'Total Permits':<13} | {'Peak Rut':<9} | {'Pre-Peak':<9}")
    print("-" * 100)
    
    for method, data in method_analysis.items():
        print(f"{method.title():<15} | {data['total_hunts']:<6} | {data['avg_score']:<9} | {data['max_score']:<9} | {data['total_permits']:<13} | {data['peak_rut_hunts']:<9} | {data['pre_peak_hunts']:<9}")
    
    # Top recommendation by method
    print(f"\n🏆 BEST OPPORTUNITY BY METHOD")
    print("=" * 120)
    
    for method, data in method_analysis.items():
        top_hunt = data['top_hunt']
        print(f"\n{method.upper()}:")
        print(f"  Hunt: {top_hunt['hunt_name']}")
        print(f"  Location: {top_hunt['wma_location']}")
        print(f"  Date: {top_hunt['start_date'].strftime('%B %d, %Y')}")
        print(f"  Score: {top_hunt['combined_score']}")
        print(f"  Permits: {top_hunt['permits_available']}")
        print(f"  Rut Period: {top_hunt['rut_score'][1]}")

if __name__ == "__main__":
    main()
