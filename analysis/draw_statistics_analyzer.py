"""
Draw Hunt Statistics Analyzer
Analyzes MDWFP historical draw hunt success rates and application data
"""

import csv
from collections import defaultdict
import json

class DrawStatisticsAnalyzer:
    def __init__(self):
        """Initialize the draw statistics analyzer."""
        self.historical_data = {}
        self.current_hunts = []
        self.verified_locations = [
            'Mahannah',
            'Phil Bryant (Buck Bayou Unit)',
            'Phil Bryant (Goose Lake Unit)', 
            'Phil Bryant (Ten Point Unit)',
            'Phil Bryant (Backwoods Unit)',
            'Sky Lake',
            'Twin Oaks',
            'Riverfront'
        ]
    
    def load_historical_data(self, data_dict):
        """Load historical draw statistics data."""
        self.historical_data = data_dict
        print(f"Loaded historical data for {len(data_dict)} hunt opportunities")
    
    def load_current_hunts(self, csv_files):
        """Load current 2025-26 hunt opportunities."""
        hunt_types = ['archery', 'gun', 'primitive_weapon', 'group']
        
        for hunt_type, file_path in zip(hunt_types, csv_files):
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        row['hunt_method'] = hunt_type
                        self.current_hunts.append(row)
                print(f"Loaded {hunt_type} hunts from {file_path}")
            except Exception as e:
                print(f"Error loading {hunt_type} hunts: {e}")
    
    def calculate_competition_index(self, wma_location, hunt_method):
        """Calculate competition index based on historical data."""
        if not self.historical_data:
            return 'Unknown'
        
        # This would use actual historical data when available
        key = f"{wma_location}_{hunt_method}"
        if key in self.historical_data:
            apps = self.historical_data[key].get('applications', 0)
            permits = self.historical_data[key].get('permits', 1)
            ratio = apps / permits if permits > 0 else 0
            
            if ratio > 10:
                return 'Very High'
            elif ratio > 5:
                return 'High'
            elif ratio > 3:
                return 'Moderate'
            elif ratio > 1.5:
                return 'Low'
            else:
                return 'Very Low'
        
        return 'Unknown'
    
    def get_strategic_recommendations(self):
        """Generate strategic application recommendations."""
        recommendations = {
            'tier_1_premium': [],
            'tier_2_competitive': [],
            'tier_3_volume': [],
            'analysis_summary': {}
        }
        
        # Group hunts by location and method
        location_groups = defaultdict(lambda: defaultdict(list))
        for hunt in self.current_hunts:
            if hunt['wma_location'] in self.verified_locations:
                location_groups[hunt['wma_location']][hunt['hunt_method']].append(hunt)
        
        # Analyze each location
        for location, methods in location_groups.items():
            for method, hunts in methods.items():
                competition = self.calculate_competition_index(location, method)
                
                # Calculate average permits
                avg_permits = sum(int(h['permits_available']) for h in hunts) / len(hunts)
                
                location_analysis = {
                    'location': location,
                    'hunt_method': method,
                    'hunt_count': len(hunts),
                    'avg_permits': round(avg_permits, 1),
                    'competition_level': competition,
                    'recommendation': self._get_tier_recommendation(location, method, competition, avg_permits)
                }
                
                # Categorize by tier
                if location_analysis['recommendation'] == 'Tier 1':
                    recommendations['tier_1_premium'].append(location_analysis)
                elif location_analysis['recommendation'] == 'Tier 2':
                    recommendations['tier_2_competitive'].append(location_analysis)
                else:
                    recommendations['tier_3_volume'].append(location_analysis)
        
        return recommendations
    
    def _get_tier_recommendation(self, location, method, competition, avg_permits):
        """Determine tier recommendation based on multiple factors."""
        # Phil Bryant units are likely high competition but high quality
        if 'Phil Bryant' in location:
            if method in ['archery', 'gun'] and avg_permits >= 20:
                return 'Tier 1'  # Premium opportunities
            else:
                return 'Tier 2'  # Competitive but worthwhile
        
        # Sky Lake and Twin Oaks may be less competitive
        if location in ['Sky Lake', 'Twin Oaks']:
            if avg_permits >= 15:
                return 'Tier 2'  # Good value
            else:
                return 'Tier 3'  # Volume strategy
        
        # Mahannah - consistent opportunities
        if location == 'Mahannah':
            return 'Tier 2'  # Reliable choice
        
        # Riverfront - limited data but potentially low competition
        if location == 'Riverfront':
            return 'Tier 3'  # Sleeper pick
        
        return 'Tier 3'  # Default
    
    def generate_application_strategy(self):
        """Generate comprehensive application strategy."""
        recs = self.get_strategic_recommendations()
        
        strategy = {
            'primary_targets': [],
            'backup_choices': [],
            'volume_fills': [],
            'strategic_notes': []
        }
        
        # Primary targets (2-3 choices)
        tier_1_sorted = sorted(recs['tier_1_premium'], 
                              key=lambda x: x['avg_permits'], reverse=True)
        strategy['primary_targets'] = tier_1_sorted[:3]
        
        # Backup choices (3-4 choices)
        tier_2_sorted = sorted(recs['tier_2_competitive'], 
                              key=lambda x: x['avg_permits'], reverse=True)
        strategy['backup_choices'] = tier_2_sorted[:4]
        
        # Volume fills (remaining choices)
        strategy['volume_fills'] = recs['tier_3_volume']
        
        # Strategic notes
        strategy['strategic_notes'] = [
            "Focus primary choices on highest-scoring hunts from enhanced analysis",
            "Balance premium opportunities with realistic success probability",
            "Consider multiple hunt methods to increase overall success odds",
            "Apply early in application period for best selection",
            "Review historical trends if available for final optimization"
        ]
        
        return strategy
    
    def print_strategy_report(self):
        """Print formatted application strategy report."""
        strategy = self.generate_application_strategy()
        
        print("=" * 80)
        print("STRATEGIC APPLICATION PLAN - MISSISSIPPI WMA DRAW HUNTS")
        print("=" * 80)
        
        print("\n🎯 PRIMARY TARGETS (Highest Priority)")
        print("-" * 50)
        for i, target in enumerate(strategy['primary_targets'], 1):
            print(f"{i}. {target['location']} - {target['hunt_method'].title()}")
            print(f"   Hunts: {target['hunt_count']} | Avg Permits: {target['avg_permits']}")
            print(f"   Competition: {target['competition_level']}")
        
        print("\n🎯 BACKUP CHOICES (Good Value)")
        print("-" * 50)
        for i, backup in enumerate(strategy['backup_choices'], 1):
            print(f"{i}. {backup['location']} - {backup['hunt_method'].title()}")
            print(f"   Hunts: {backup['hunt_count']} | Avg Permits: {backup['avg_permits']}")
            print(f"   Competition: {backup['competition_level']}")
        
        print("\n🎯 VOLUME STRATEGY (Fill Remaining Choices)")
        print("-" * 50)
        for i, volume in enumerate(strategy['volume_fills'], 1):
            print(f"{i}. {volume['location']} - {volume['hunt_method'].title()}")
            print(f"   Hunts: {volume['hunt_count']} | Avg Permits: {volume['avg_permits']}")
        
        print("\n📋 STRATEGIC NOTES")
        print("-" * 50)
        for note in strategy['strategic_notes']:
            print(f"• {note}")
        
        print("\n" + "=" * 80)

def main():
    """Example usage of the Draw Statistics Analyzer."""
    analyzer = DrawStatisticsAnalyzer()
    
    # Load current hunt data
    csv_files = [
        'data/deer_archery_hunts_2025_26.csv',
        'data/deer_gun_hunts_2025_26.csv', 
        'data/deer_primitive_weapon_hunts_2025_26.csv',
        'data/deer_group_hunts_2025_26.csv'
    ]
    
    analyzer.load_current_hunts(csv_files)
    
    print("DRAW HUNT STRATEGIC ANALYSIS")
    print("Note: Historical competition data would enhance this analysis when available\n")
    
    analyzer.print_strategy_report()
    
    print("\n📊 INTEGRATION WITH ENHANCED HUNT ANALYZER")
    print("-" * 60)
    print("1. Run enhanced_hunt_analyzer.py to get optimal hunt dates/scores")
    print("2. Cross-reference top-scoring hunts with strategic tiers above")
    print("3. Prioritize Tier 1 hunts that also score highly in moon/rut analysis")
    print("4. Use Tier 2/3 hunts as backups for similar date ranges")
    print("5. Apply historical success rate data when PDF data is processed")

if __name__ == "__main__":
    main()
