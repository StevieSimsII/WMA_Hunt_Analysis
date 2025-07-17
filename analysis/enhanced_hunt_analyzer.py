"""
Enhanced Mississippi WMA Draw Hunt Analysis Tool with Moon Phase & Rut Scoring

This script analyzes WMA draw hunt opportunities factoring in moon phases,
deer rut timing, and traditional metrics for Yazoo County, Mississippi region.
"""

import csv
from datetime import datetime
from collections import defaultdict

class EnhancedDrawHuntAnalyzer:
    def __init__(self, data_file=None):
        """Initialize the analyzer with hunt data."""
        self.data_file = data_file
        self.hunts = []
        self.moon_phases = self._load_moon_phases()
        self.rut_periods = self._load_rut_periods()
        if data_file:
            self.load_data(data_file)
    
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
    
    def load_data(self, file_path):
        """Load hunt data from CSV file."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['start_date'] = datetime.strptime(row['start_date'], '%Y-%m-%d')
                    row['end_date'] = datetime.strptime(row['end_date'], '%Y-%m-%d')
                    row['permits_available'] = int(row['permits_available'])
                    row['duration_days'] = int(row['duration_days'])
                    
                    # Add enhanced scoring
                    row['moon_score'] = self._calculate_moon_score(row['start_date'], row['end_date'])
                    row['rut_score'] = self._calculate_rut_score(row['start_date'], row['end_date'])
                    row['combined_score'] = self._calculate_combined_score(row)
                    
                    self.hunts.append(row)
            print(f"Loaded {len(self.hunts)} hunt opportunities with enhanced scoring")
        except Exception as e:
            print(f"Error loading data: {e}")
    
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
            'closest_phase': closest_phase,
            'description': self._get_moon_description(best_score)
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
        
        # Default if no period matches
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
    
    def _get_moon_description(self, score):
        """Get description for moon score."""
        if score >= 2.5:
            return "Excellent (New Moon Period)"
        elif score >= 1:
            return "Good (Quarter Moon)"
        elif score >= 0:
            return "Fair (Neutral)"
        else:
            return "Poor (Full Moon Period)"
    
    def get_top_hunts_by_combined_score(self, top_n=15):
        """Get best hunts based on combined moon/rut/permit scoring."""
        if not self.hunts:
            return []
        
        sorted_hunts = sorted(self.hunts, key=lambda x: x['combined_score'], reverse=True)
        
        results = []
        for hunt in sorted_hunts[:top_n]:
            results.append({
                'hunt_name': hunt['hunt_name'],
                'location': hunt['wma_location'],
                'start_date': hunt['start_date'].strftime('%Y-%m-%d'),
                'end_date': hunt['end_date'].strftime('%Y-%m-%d'),
                'permits': hunt['permits_available'],
                'duration': hunt['duration_days'],
                'combined_score': hunt['combined_score'],
                'rut_period': hunt['rut_score']['description'],
                'moon_impact': hunt['moon_score']['description'],
                'closest_moon': hunt['moon_score']['closest_phase']
            })
        
        return results
    
    def get_rut_analysis(self):
        """Analyze hunts by rut periods."""
        rut_analysis = defaultdict(lambda: {'hunts': [], 'total_permits': 0, 'avg_score': 0})
        
        for hunt in self.hunts:
            period = hunt['rut_score']['period']
            rut_analysis[period]['hunts'].append(hunt)
            rut_analysis[period]['total_permits'] += hunt['permits_available']
        
        results = []
        for period, data in rut_analysis.items():
            if data['hunts']:
                avg_score = sum(h['combined_score'] for h in data['hunts']) / len(data['hunts'])
                results.append({
                    'rut_period': period,
                    'hunt_count': len(data['hunts']),
                    'total_permits': data['total_permits'],
                    'avg_combined_score': round(avg_score, 2),
                    'description': data['hunts'][0]['rut_score']['description']
                })
        
        results.sort(key=lambda x: x['avg_combined_score'], reverse=True)
        return results
    
    def get_moon_analysis(self):
        """Analyze hunts by moon phase timing."""
        moon_analysis = defaultdict(lambda: {'hunts': [], 'total_permits': 0})
        
        for hunt in self.hunts:
            moon_desc = hunt['moon_score']['description']
            moon_analysis[moon_desc]['hunts'].append(hunt)
            moon_analysis[moon_desc]['total_permits'] += hunt['permits_available']
        
        results = []
        for moon_desc, data in moon_analysis.items():
            if data['hunts']:
                avg_score = sum(h['combined_score'] for h in data['hunts']) / len(data['hunts'])
                results.append({
                    'moon_condition': moon_desc,
                    'hunt_count': len(data['hunts']),
                    'total_permits': data['total_permits'],
                    'avg_combined_score': round(avg_score, 2)
                })
        
        results.sort(key=lambda x: x['avg_combined_score'], reverse=True)
        return results
    
    def get_premium_recommendations(self):
        """Get tier-1 premium hunt recommendations."""
        premium_hunts = []
        
        for hunt in self.hunts:
            # Premium criteria: High rut score + good moon score + decent permits
            if (hunt['rut_score']['score'] >= 4 and 
                hunt['moon_score']['score'] >= 1 and 
                hunt['permits_available'] >= 12):
                
                premium_hunts.append({
                    'hunt_name': hunt['hunt_name'],
                    'location': hunt['wma_location'],
                    'start_date': hunt['start_date'].strftime('%Y-%m-%d'),
                    'permits': hunt['permits_available'],
                    'combined_score': hunt['combined_score'],
                    'why_premium': f"Rut: {hunt['rut_score']['description']}, Moon: {hunt['moon_score']['description']}"
                })
        
        premium_hunts.sort(key=lambda x: x['combined_score'], reverse=True)
        return premium_hunts[:10]

def print_enhanced_table(data, headers):
    """Print data in a formatted table."""
    if not data:
        print("No data to display")
        return
    
    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = len(header)
        for row in data:
            if header in row:
                widths[header] = max(widths[header], len(str(row[header])))
    
    # Print header
    header_row = " | ".join(header.ljust(widths[header]) for header in headers)
    print(header_row)
    print("-" * len(header_row))
    
    # Print data rows
    for row in data:
        data_row = " | ".join(str(row.get(header, '')).ljust(widths[header]) for header in headers)
        print(data_row)

def main():
    """Main function with enhanced analysis for all hunt types."""
    print("=== MISSISSIPPI WMA DRAW HUNT ANALYSIS - ALL HUNT TYPES COMPARISON ===\n")
    
    # Define all hunt files
    hunt_files = {
        'Archery': 'data/deer_archery_hunts_2025_26.csv',
        'Gun': 'data/deer_gun_hunts_2025_26.csv',
        'Primitive Weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
        'Group': 'data/deer_group_hunts_2025_26.csv'
    }
    
    analyzers = {}
    all_hunts = []
    
    # Load all hunt types
    for hunt_type, file_path in hunt_files.items():
        print(f"Loading {hunt_type} hunts...")
        analyzer = EnhancedDrawHuntAnalyzer(file_path)
        if analyzer.hunts:
            analyzers[hunt_type] = analyzer
            # Add hunt type to each hunt record
            for hunt in analyzer.hunts:
                hunt['hunt_method'] = hunt_type
            all_hunts.extend(analyzer.hunts)
        else:
            print(f"⚠️ No {hunt_type} hunts loaded")
    
    if not all_hunts:
        print("Failed to load any hunt data. Please check the file paths.")
        return
    
    print(f"\n📊 TOTAL LOADED: {len(all_hunts)} hunts across {len(analyzers)} hunt types\n")
    print("="*120 + "\n")
    
    # Overall top hunts across all types
    print("🏆 TOP 15 HUNTS - ALL METHODS COMBINED:")
    all_hunts_sorted = sorted(all_hunts, key=lambda x: x['combined_score'], reverse=True)
    
    top_overall = []
    for hunt in all_hunts_sorted[:15]:
        top_overall.append({
            'hunt_name': hunt['hunt_name'][:40] + "..." if len(hunt['hunt_name']) > 40 else hunt['hunt_name'],
            'method': hunt['hunt_method'],
            'location': hunt['wma_location'][:25] + "..." if len(hunt['wma_location']) > 25 else hunt['wma_location'],
            'start_date': hunt['start_date'].strftime('%m/%d'),
            'permits': hunt['permits_available'],
            'score': hunt['combined_score'],
            'rut_period': hunt['rut_score']['description'][:20] + "..." if len(hunt['rut_score']['description']) > 20 else hunt['rut_score']['description']
        })
    
    headers = ['hunt_name', 'method', 'location', 'start_date', 'permits', 'score', 'rut_period']
    print_enhanced_table(top_overall, headers)
    
    print("\n" + "="*120 + "\n")
    
    # Best hunt by each method
    print("🎯 BEST HUNT BY METHOD:")
    method_bests = {}
    for hunt_type, analyzer in analyzers.items():
        if analyzer.hunts:
            best_hunt = max(analyzer.hunts, key=lambda x: x['combined_score'])
            method_bests[hunt_type] = {
                'hunt_name': best_hunt['hunt_name'][:35] + "..." if len(best_hunt['hunt_name']) > 35 else best_hunt['hunt_name'],
                'location': best_hunt['wma_location'][:25] + "..." if len(best_hunt['wma_location']) > 25 else best_hunt['wma_location'],
                'start_date': best_hunt['start_date'].strftime('%m/%d/%Y'),
                'permits': best_hunt['permits_available'],
                'score': best_hunt['combined_score'],
                'rut_period': best_hunt['rut_score']['description'],
                'moon_impact': best_hunt['moon_score']['description']
            }
    
    for method, best in method_bests.items():
        print(f"\n{method.upper()}:")
        print(f"  Hunt: {best['hunt_name']}")
        print(f"  Location: {best['location']}")
        print(f"  Date: {best['start_date']}")
        print(f"  Score: {best['score']} | Permits: {best['permits']}")
        print(f"  Rut: {best['rut_period']}")
        print(f"  Moon: {best['moon_impact']}")
    
    print("\n" + "="*120 + "\n")
    
    # Method comparison statistics
    print("📊 HUNT METHOD COMPARISON:")
    method_stats = []
    for hunt_type, analyzer in analyzers.items():
        if analyzer.hunts:
            scores = [h['combined_score'] for h in analyzer.hunts]
            permits = [h['permits_available'] for h in analyzer.hunts]
            peak_rut_hunts = len([h for h in analyzer.hunts if h['rut_score']['score'] >= 5])
            pre_peak_hunts = len([h for h in analyzer.hunts if h['rut_score']['score'] == 4])
            
            method_stats.append({
                'method': hunt_type,
                'total_hunts': len(analyzer.hunts),
                'avg_score': round(sum(scores) / len(scores), 2),
                'max_score': round(max(scores), 2),
                'total_permits': sum(permits),
                'avg_permits': round(sum(permits) / len(permits), 1),
                'peak_rut_hunts': peak_rut_hunts,
                'pre_peak_hunts': pre_peak_hunts
            })
    
    method_stats.sort(key=lambda x: x['max_score'], reverse=True)
    
    headers = ['method', 'total_hunts', 'avg_score', 'max_score', 'total_permits', 'avg_permits', 'peak_rut_hunts', 'pre_peak_hunts']
    print_enhanced_table(method_stats, headers)
    
    print("\n" + "="*120 + "\n")
    
    # Peak rut opportunities across all methods
    print("🦌 PEAK RUT OPPORTUNITIES (Dec 29 - Jan 4):")
    peak_rut_hunts = [h for h in all_hunts if h['rut_score']['score'] >= 5]
    peak_rut_hunts.sort(key=lambda x: x['combined_score'], reverse=True)
    
    peak_rut_display = []
    for hunt in peak_rut_hunts[:10]:
        peak_rut_display.append({
            'hunt_name': hunt['hunt_name'][:35] + "..." if len(hunt['hunt_name']) > 35 else hunt['hunt_name'],
            'method': hunt['hunt_method'],
            'location': hunt['wma_location'][:20] + "..." if len(hunt['wma_location']) > 20 else hunt['wma_location'],
            'start_date': hunt['start_date'].strftime('%m/%d'),
            'permits': hunt['permits_available'],
            'score': hunt['combined_score']
        })
    
    headers = ['hunt_name', 'method', 'location', 'start_date', 'permits', 'score']
    print_enhanced_table(peak_rut_display, headers)
    
    print("\n" + "="*120 + "\n")
    
    # Key insights
    print("🎯 COMPREHENSIVE INSIGHTS:")
    
    # Overall best
    if all_hunts_sorted:
        best_overall = all_hunts_sorted[0]
        print(f"  🥇 Overall Best: {best_overall['hunt_name']} ({best_overall['hunt_method']})")
        print(f"     Score: {best_overall['combined_score']} | Date: {best_overall['start_date'].strftime('%m/%d/%Y')}")
    
    # Method rankings by max score
    print(f"\n  📈 Method Rankings (by max score):")
    for i, stat in enumerate(method_stats, 1):
        print(f"     {i}. {stat['method']}: {stat['max_score']} max, {stat['avg_score']} avg ({stat['total_hunts']} hunts)")
    
    # Peak rut summary
    peak_count = len(peak_rut_hunts)
    pre_peak_count = len([h for h in all_hunts if h['rut_score']['score'] == 4])
    print(f"\n  🦌 Rut Timing Summary:")
    print(f"     Peak Rut Hunts (Dec 29-Jan 4): {peak_count}")
    print(f"     Pre-Peak Hunts (Dec 16-28): {pre_peak_count}")
    
    # Best locations
    location_scores = defaultdict(list)
    for hunt in all_hunts:
        location_scores[hunt['wma_location']].append(hunt['combined_score'])
    
    best_locations = []
    for location, scores in location_scores.items():
        if len(scores) >= 3:  # Only consider locations with 3+ hunts
            avg_score = sum(scores) / len(scores)
            best_locations.append((location, round(avg_score, 2), len(scores)))
    
    best_locations.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  🏞️ Best Locations (3+ hunts):")
    for location, avg_score, hunt_count in best_locations[:5]:
        print(f"     {location}: {avg_score} avg ({hunt_count} hunts)")
    
    print(f"\n  📊 Total Analysis: {len(all_hunts)} hunts across {len(analyzers)} methods")
    print("     Scoring: 30% Rut Timing, 30% Permits, 20% Moon Phase, 20% Duration")

if __name__ == "__main__":
    main()
