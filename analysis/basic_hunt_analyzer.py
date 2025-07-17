"""
Mississippi WMA Draw Hunt Analysis Tool - Basic Version

This script analyzes WMA draw hunt opportunities without requiring additional packages.
"""

import csv
from datetime import datetime
from collections import defaultdict

class BasicDrawHuntAnalyzer:
    def __init__(self, data_file=None):
        """Initialize the analyzer with hunt data."""
        self.data_file = data_file
        self.hunts = []
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        """Load hunt data from CSV file."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Convert dates and numbers
                    row['start_date'] = datetime.strptime(row['start_date'], '%Y-%m-%d')
                    row['end_date'] = datetime.strptime(row['end_date'], '%Y-%m-%d')
                    row['permits_available'] = int(row['permits_available'])
                    row['duration_days'] = int(row['duration_days'])
                    self.hunts.append(row)
            print(f"Loaded {len(self.hunts)} hunt opportunities")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def analyze_by_location(self):
        """Analyze hunts by WMA location."""
        if not self.hunts:
            print("No data loaded")
            return
        
        location_stats = defaultdict(lambda: {'hunt_count': 0, 'total_permits': 0, 'durations': []})
        
        for hunt in self.hunts:
            location = hunt['wma_location']
            location_stats[location]['hunt_count'] += 1
            location_stats[location]['total_permits'] += hunt['permits_available']
            location_stats[location]['durations'].append(hunt['duration_days'])
        
        # Calculate averages and sort by total permits
        results = []
        for location, stats in location_stats.items():
            avg_permits = stats['total_permits'] / stats['hunt_count']
            avg_duration = sum(stats['durations']) / len(stats['durations'])
            permits_per_opportunity = stats['total_permits'] / stats['hunt_count']
            
            results.append({
                'location': location,
                'total_hunts': stats['hunt_count'],
                'total_permits': stats['total_permits'],
                'avg_permits_per_hunt': round(avg_permits, 1),
                'avg_duration': round(avg_duration, 1),
                'permits_per_opportunity': round(permits_per_opportunity, 1)
            })
        
        # Sort by total permits (descending)
        results.sort(key=lambda x: x['total_permits'], reverse=True)
        return results
    
    def analyze_by_month(self):
        """Analyze hunts by month."""
        if not self.hunts:
            print("No data loaded")
            return
        
        month_stats = defaultdict(lambda: {'hunt_count': 0, 'total_permits': 0})
        
        for hunt in self.hunts:
            month_name = hunt['start_date'].strftime('%B %Y')
            month_stats[month_name]['hunt_count'] += 1
            month_stats[month_name]['total_permits'] += hunt['permits_available']
        
        results = []
        for month, stats in month_stats.items():
            results.append({
                'month': month,
                'hunt_count': stats['hunt_count'],
                'total_permits': stats['total_permits']
            })
        
        # Sort by month
        results.sort(key=lambda x: datetime.strptime(x['month'], '%B %Y'))
        return results
    
    def find_best_opportunities(self, criteria='permits_available', top_n=10):
        """Find the best hunt opportunities based on specified criteria."""
        if not self.hunts:
            print("No data loaded")
            return
        
        if criteria == 'permits_available':
            sorted_hunts = sorted(self.hunts, key=lambda x: x['permits_available'], reverse=True)
        elif criteria == 'duration_days':
            sorted_hunts = sorted(self.hunts, key=lambda x: x['duration_days'], reverse=True)
        elif criteria == 'early_season':
            sorted_hunts = sorted(self.hunts, key=lambda x: x['start_date'])
        
        results = []
        for hunt in sorted_hunts[:top_n]:
            results.append({
                'hunt_name': hunt['hunt_name'],
                'location': hunt['wma_location'],
                'start_date': hunt['start_date'].strftime('%Y-%m-%d'),
                'end_date': hunt['end_date'].strftime('%Y-%m-%d'),
                'permits': hunt['permits_available'],
                'duration': hunt['duration_days']
            })
        
        return results
    
    def calculate_competition_estimates(self):
        """Calculate simple competition estimates."""
        if not self.hunts:
            print("No data loaded")
            return
        
        results = []
        for hunt in self.hunts:
            # Simple competition score (lower is better)
            competition_score = (1 / hunt['permits_available']) * 100 + (1 / hunt['duration_days']) * 10
            
            results.append({
                'hunt_name': hunt['hunt_name'],
                'location': hunt['wma_location'],
                'start_date': hunt['start_date'].strftime('%Y-%m-%d'),
                'permits': hunt['permits_available'],
                'duration': hunt['duration_days'],
                'competition_score': round(competition_score, 2)
            })
        
        # Sort by competition score (ascending - lower is better)
        results.sort(key=lambda x: x['competition_score'])
        return results
    
    def get_application_calendar(self):
        """Get important application dates."""
        return {
            'Deer': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Early Teal': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Rabbit': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Dove': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Youth Dove': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Turkey': {'start': '2025-01-01', 'end': '2025-01-31'},
            'Waterfowl': {'start': '2025-10-01', 'end': '2025-10-15'}
        }

def print_table(data, headers):
    """Print data in a table format."""
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
    """Main function to demonstrate the analysis."""
    print("=== MISSISSIPPI WMA DRAW HUNT ANALYSIS ===\n")
    
    # Initialize analyzer
    analyzer = BasicDrawHuntAnalyzer('data/deer_archery_hunts_2025_26.csv')
    
    if not analyzer.hunts:
        print("Failed to load hunt data. Please check the file path.")
        return
    
    # Application calendar
    print("APPLICATION PERIODS:")
    app_calendar = analyzer.get_application_calendar()
    for hunt_type, dates in app_calendar.items():
        print(f"  {hunt_type}: {dates['start']} to {dates['end']}")
    
    print("\n" + "="*80 + "\n")
    
    # Location analysis
    print("ANALYSIS BY WMA LOCATION:")
    location_analysis = analyzer.analyze_by_location()
    headers = ['location', 'total_hunts', 'total_permits', 'avg_permits_per_hunt', 'avg_duration']
    print_table(location_analysis, headers)
    
    print("\n" + "="*80 + "\n")
    
    # Month analysis
    print("ANALYSIS BY TIME PERIOD:")
    month_analysis = analyzer.analyze_by_month()
    headers = ['month', 'hunt_count', 'total_permits']
    print_table(month_analysis, headers)
    
    print("\n" + "="*80 + "\n")
    
    # Best opportunities by permits
    print("TOP 10 HUNTS BY PERMITS AVAILABLE:")
    best_permits = analyzer.find_best_opportunities('permits_available', 10)
    headers = ['hunt_name', 'location', 'start_date', 'permits', 'duration']
    print_table(best_permits, headers)
    
    print("\n" + "="*80 + "\n")
    
    # Lowest competition estimates
    print("LOWEST COMPETITION ESTIMATES (Top 15):")
    competition = analyzer.calculate_competition_estimates()
    headers = ['hunt_name', 'location', 'start_date', 'permits', 'duration', 'competition_score']
    print_table(competition[:15], headers)
    
    print("\n" + "="*80 + "\n")
    
    # Summary insights
    print("KEY INSIGHTS:")
    total_hunts = len(analyzer.hunts)
    total_permits = sum(hunt['permits_available'] for hunt in analyzer.hunts)
    avg_permits = total_permits / total_hunts
    
    print(f"  • Total hunt opportunities: {total_hunts}")
    print(f"  • Total permits available: {total_permits}")
    print(f"  • Average permits per hunt: {avg_permits:.1f}")
    
    # Find best locations
    location_analysis = analyzer.analyze_by_location()
    best_location = location_analysis[0]['location']
    print(f"  • Location with most permits: {best_location}")
    
    # Find early and late season options
    early_hunts = analyzer.find_best_opportunities('early_season', 3)
    print(f"  • Earliest hunt starts: {early_hunts[0]['start_date']}")

if __name__ == "__main__":
    main()
