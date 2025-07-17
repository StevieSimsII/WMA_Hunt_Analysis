"""
Mississippi WMA Draw Hunt Analysis Tool

This script analyzes WMA draw hunt opportunities to help make informed decisions
about which hunts to apply for based on various criteria.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

class DrawHuntAnalyzer:
    def __init__(self, data_file=None):
        """Initialize the analyzer with hunt data."""
        self.data_file = data_file
        self.hunts_df = None
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        """Load hunt data from CSV file."""
        try:
            self.hunts_df = pd.read_csv(file_path)
            self.hunts_df['start_date'] = pd.to_datetime(self.hunts_df['start_date'])
            self.hunts_df['end_date'] = pd.to_datetime(self.hunts_df['end_date'])
            print(f"Loaded {len(self.hunts_df)} hunt opportunities")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def analyze_by_location(self):
        """Analyze hunts by WMA location."""
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        location_stats = self.hunts_df.groupby('wma_location').agg({
            'hunt_name': 'count',
            'permits_available': ['sum', 'mean'],
            'duration_days': 'mean'
        }).round(2)
        
        location_stats.columns = ['Total_Hunts', 'Total_Permits', 'Avg_Permits_Per_Hunt', 'Avg_Duration']
        
        # Calculate competition ratio (lower is better)
        location_stats['Permits_Per_Hunt_Opportunity'] = (
            location_stats['Total_Permits'] / location_stats['Total_Hunts']
        )
        
        return location_stats.sort_values('Permits_Per_Hunt_Opportunity', ascending=False)
    
    def analyze_by_time_period(self):
        """Analyze hunts by time period (month)."""
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        self.hunts_df['month'] = self.hunts_df['start_date'].dt.month
        self.hunts_df['month_name'] = self.hunts_df['start_date'].dt.strftime('%B')
        
        time_stats = self.hunts_df.groupby(['month', 'month_name']).agg({
            'hunt_name': 'count',
            'permits_available': 'sum'
        })
        
        time_stats.columns = ['Hunt_Count', 'Total_Permits']
        return time_stats.reset_index().sort_values('month')
    
    def find_best_opportunities(self, criteria='permits_available', top_n=10):
        """Find the best hunt opportunities based on specified criteria."""
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        if criteria == 'permits_available':
            best_hunts = self.hunts_df.nlargest(top_n, 'permits_available')
        elif criteria == 'duration_days':
            best_hunts = self.hunts_df.nlargest(top_n, 'duration_days')
        elif criteria == 'early_season':
            best_hunts = self.hunts_df.nsmallest(top_n, 'start_date')
        
        return best_hunts[['hunt_name', 'wma_location', 'start_date', 'end_date', 
                          'permits_available', 'duration_days']]
    
    def calculate_competition_estimate(self, historical_data=None):
        """
        Estimate competition level based on permits available.
        This is a simple model - actual competition depends on many factors.
        """
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        # Simple competition scoring (lower score = less competition)
        # Based on permits available and hunt duration
        self.hunts_df['competition_score'] = (
            (1 / self.hunts_df['permits_available']) * 100 +
            (1 / self.hunts_df['duration_days']) * 10
        )
        
        return self.hunts_df.sort_values('competition_score')[
            ['hunt_name', 'wma_location', 'start_date', 'permits_available', 
             'duration_days', 'competition_score']
        ]
    
    def get_application_calendar(self):
        """Get important application dates."""
        application_periods = {
            'Deer': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Early Teal': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Rabbit': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Dove': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Youth Dove': {'start': '2025-07-15', 'end': '2025-08-15'},
            'Turkey': {'start': '2025-01-01', 'end': '2025-01-31'},
            'Waterfowl': {'start': '2025-10-01', 'end': '2025-10-15'}
        }
        
        return application_periods
    
    def plot_permits_by_location(self):
        """Create visualization of permits available by location."""
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        location_permits = self.hunts_df.groupby('wma_location')['permits_available'].sum().sort_values(ascending=True)
        
        plt.figure(figsize=(12, 8))
        location_permits.plot(kind='barh')
        plt.title('Total Permits Available by WMA Location')
        plt.xlabel('Total Permits Available')
        plt.tight_layout()
        plt.show()
    
    def plot_hunts_timeline(self):
        """Create timeline visualization of hunts."""
        if self.hunts_df is None:
            print("No data loaded")
            return
        
        plt.figure(figsize=(15, 8))
        
        # Create timeline plot
        for i, hunt in self.hunts_df.iterrows():
            plt.barh(i, (hunt['end_date'] - hunt['start_date']).days, 
                    left=hunt['start_date'], height=0.8, 
                    alpha=0.7, label=hunt['wma_location'])
        
        plt.xlabel('Date')
        plt.ylabel('Hunt Index')
        plt.title('Hunt Timeline - All Deer Archery Hunts 2025-26')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def main():
    """Main function to demonstrate the analysis."""
    # Initialize analyzer
    analyzer = DrawHuntAnalyzer('data/deer_archery_hunts_2025_26.csv')
    
    print("=== MISSISSIPPI WMA DRAW HUNT ANALYSIS ===\n")
    
    # Application calendar
    print("APPLICATION PERIODS:")
    app_calendar = analyzer.get_application_calendar()
    for hunt_type, dates in app_calendar.items():
        print(f"{hunt_type}: {dates['start']} to {dates['end']}")
    
    print("\n" + "="*50 + "\n")
    
    # Location analysis
    print("ANALYSIS BY WMA LOCATION:")
    location_analysis = analyzer.analyze_by_location()
    print(location_analysis)
    
    print("\n" + "="*50 + "\n")
    
    # Time period analysis
    print("ANALYSIS BY TIME PERIOD:")
    time_analysis = analyzer.analyze_by_time_period()
    print(time_analysis)
    
    print("\n" + "="*50 + "\n")
    
    # Best opportunities
    print("TOP 10 HUNTS BY PERMITS AVAILABLE:")
    best_permits = analyzer.find_best_opportunities('permits_available', 10)
    print(best_permits.to_string(index=False))
    
    print("\n" + "="*50 + "\n")
    
    # Competition estimates
    print("LOWEST COMPETITION ESTIMATES (Top 15):")
    competition = analyzer.calculate_competition_estimate()
    print(competition.head(15).to_string(index=False))

if __name__ == "__main__":
    main()
