#!/usr/bin/env python3
"""
Test script to run the original matching algorithm on CSV files
and compare results with the existing intern_to_restaurant.csv
"""

import csv
import json
from collections import defaultdict

# Load the original CSV files
print("Loading CSV files...")

def read_csv_dict(filename):
    """Read CSV file into list of dictionaries"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except UnicodeDecodeError:
        # Try with different encoding
        with open(filename, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

intern_data = read_csv_dict('intern_avail_fall.csv')
chef_data = read_csv_dict('chef_avail_fall.csv')
results_data = read_csv_dict('intern_to_restaurant.csv')

print(f"Interns in CSV: {len(intern_data)}")
print(f"Restaurants in CSV: {len(chef_data)}")
print(f"Results in CSV: {len(results_data)}")

# Display first few results from original matching
print("\n=== ORIGINAL MATCHING RESULTS ===")
for i, row in enumerate(results_data[:10]):
    print(f"Row {i+1}: {row}")

# Parse intern availability
def parse_intern_availability(row):
    """Parse intern availability from CSV row"""
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
    
    return availability

# Parse restaurant availability  
def parse_restaurant_availability(row):
    """Parse restaurant availability from CSV row"""
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
    
    return availability

# Calculate overlap between intern and restaurant availability
def calculate_overlap(intern_avail, restaurant_avail):
    """Calculate total weekly overlap hours"""
    total_hours = 0
    schedule = {}
    
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
                schedule[day] = f"{start}-{end}"
            else:
                schedule[day] = None
        else:
            schedule[day] = None
    
    return total_hours, schedule

# Test parsing on a few examples
print("\n=== TESTING PARSING ===")

# Get first few interns and restaurants
sample_interns = intern_data[:3]
sample_restaurants = chef_data[:3]

for intern_row in sample_interns:
    intern_name = f"{intern_row.get('First Name', '')} {intern_row.get('Last Name', '')}"
    intern_avail = parse_intern_availability(intern_row)
    print(f"\nIntern: {intern_name}")
    print(f"Availability: {intern_avail}")

for restaurant_row in sample_restaurants:
    restaurant_name = restaurant_row.get('Restaurant Name', '')
    restaurant_avail = parse_restaurant_availability(restaurant_row)
    print(f"\nRestaurant: {restaurant_name}")
    print(f"Availability: {restaurant_avail}")

print("\n=== ORIGINAL ALGORITHM TEST COMPLETE ===")
print("CSV files loaded successfully. Parsing functions working.")
print("Ready to implement full matching algorithm comparison.")
