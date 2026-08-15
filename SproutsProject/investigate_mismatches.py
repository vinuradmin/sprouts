#!/usr/bin/env python3
"""
Investigate the 8 mismatched cases by showing intern and chef availability details
"""

import csv
import json
import re
from collections import defaultdict
from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def read_csv_dict(filename):
    """Read CSV file into list of dictionaries"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

def parse_intern_availability_from_csv(intern_name):
    """Parse intern availability from intern_avail_fall.csv"""
    intern_data = read_csv_dict('intern_avail_fall.csv')
    
    for row in intern_data:
        full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
        if full_name == intern_name or full_name.replace('  ', ' ').strip() == intern_name.replace('  ', ' ').strip():
            availability = {}
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                time_str = str(row.get(day, '')).strip()
                if time_str and time_str != 'nan':
                    # Parse time ranges like "9-15" or "10-18"
                    try:
                        if '-' in time_str:
                            start, end = time_str.split('-')
                            availability[day] = (int(start), int(end))
                        else:
                            availability[day] = None
                    except:
                        availability[day] = None
                else:
                    availability[day] = None
            
            return availability, row
    
    return {}, None

def parse_chef_availability_from_csv(restaurant_name):
    """Parse chef/restaurant availability from chef_avail_fall.csv"""
    chef_data = read_csv_dict('chef_avail_fall.csv')
    
    for row in chef_data:
        chef_restaurant = row.get('Restaurant Name', '').strip()
        if chef_restaurant == restaurant_name:
            availability = {}
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                time_str = str(row.get(day, '')).strip()
                if time_str and time_str != 'nan':
                    # Parse time ranges
                    try:
                        if '-' in time_str:
                            start, end = time_str.split('-')
                            availability[day] = (int(start), int(end))
                        else:
                            availability[day] = None
                    except:
                        availability[day] = None
                else:
                    availability[day] = None
            
            return availability, row
    
    return {}, None

def calculate_overlap(intern_avail, restaurant_avail):
    """Calculate overlap between intern and restaurant availability"""
    overlaps = {}
    total_hours = 0
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        intern_time = intern_avail.get(day)
        restaurant_time = restaurant_avail.get(day)
        
        if intern_time and restaurant_time:
            # Calculate overlap
            start = max(intern_time[0], restaurant_time[0])
            end = min(intern_time[1], restaurant_time[1])
            
            if end > start:
                overlap_hours = end - start
                total_hours += overlap_hours
                overlaps[day] = (start, end, overlap_hours)
            else:
                overlaps[day] = None
        else:
            overlaps[day] = None
    
    return overlaps, total_hours

def get_flask_mismatches():
    """Get the 8 Flask matches that weren't in original options"""
    # Load verification results
    with open('match_verification.json', 'r') as f:
        verification_results = json.load(f)
    
    return verification_results['not_found']

def investigate_mismatches():
    """Investigate the mismatched cases"""
    print("=== INVESTIGATING MISMATCHED CASES ===\n")
    
    mismatches = get_flask_mismatches()
    
    for i, mismatch in enumerate(mismatches, 1):
        print(f"=== CASE {i}: {mismatch['intern']} -> {mismatch['restaurant']} ===")
        
        # Get intern availability from CSV
        intern_avail, intern_row = parse_intern_availability_from_csv(mismatch['intern'])
        print(f"\nIntern: {mismatch['intern']}")
        print("Availability from CSV:")
        for day, time_range in intern_avail.items():
            if time_range:
                print(f"  {day}: {time_range[0]}-{time_range[1]}")
        
        # Get restaurant availability from CSV
        restaurant_avail, chef_row = parse_chef_availability_from_csv(mismatch['restaurant'])
        print(f"\nRestaurant: {mismatch['restaurant']}")
        print("Availability from CSV:")
        for day, time_range in restaurant_avail.items():
            if time_range:
                print(f"  {day}: {time_range[0]}-{time_range[1]}")
        
        # Calculate overlap
        overlaps, total_hours = calculate_overlap(intern_avail, restaurant_avail)
        print(f"\nOverlap Analysis:")
        print(f"Total weekly overlap: {total_hours} hours")
        
        has_overlap = False
        for day, overlap in overlaps.items():
            if overlap:
                has_overlap = True
                print(f"  {day}: {overlap[0]}-{overlap[1]} ({overlap[2]} hours)")
        
        if not has_overlap:
            print("  No availability overlap found!")
        
        # Show what original algorithm had for this intern
        print(f"\nOriginal algorithm options for {mismatch['intern']}:")
        for option in mismatch['available_options']:
            print(f"  - {option}")
        
        print("\n" + "="*80 + "\n")

def main():
    """Main investigation function"""
    investigate_mismatches()

if __name__ == "__main__":
    main()
