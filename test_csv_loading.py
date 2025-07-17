#!/usr/bin/env python3
"""
Simple test to verify what the enhanced analyzer is actually loading
"""

import csv
import os

def test_load(filename):
    print(f"\n=== Testing {filename} ===")
    full_path = f"data/{filename}"
    
    if not os.path.exists(full_path):
        print(f"File does not exist: {full_path}")
        return
    
    try:
        with open(full_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            hunts = list(reader)
            print(f"Number of hunts loaded: {len(hunts)}")
            
            locations = set(row.get('wma_location', '') for row in hunts)
            print(f"Locations found: {sorted(locations)}")
            
            # Check for specific locations
            charles_ray = any('Charles Ray Nix' in row.get('wma_location', '') for row in hunts)
            yockanookany = any('Yockanookany' in row.get('wma_location', '') for row in hunts)
            hell_creek = any('Hell Creek' in row.get('wma_location', '') for row in hunts)
            
            print(f"Contains Charles Ray Nix: {charles_ray}")
            print(f"Contains Yockanookany: {yockanookany}")
            print(f"Contains Hell Creek: {hell_creek}")
            
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Test all CSV files
files = [
    'deer_archery_hunts_2025_26.csv',
    'deer_gun_hunts_2025_26.csv', 
    'deer_primitive_weapon_hunts_2025_26.csv',
    'deer_group_hunts_2025_26.csv'
]

for filename in files:
    test_load(filename)
