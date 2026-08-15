#!/usr/bin/env python3
"""
Verify that each of the 8 Flask matches have overlap in the original CSV files
"""

import csv
import re
from collections import defaultdict

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

def parse_csv_availability(row, days, prefix=""):
    """Parse availability from CSV row"""
    availability = {}
    
    for day in days:
        # Try different column names
        for col_name in [day, f"{day}{prefix}"]:
            time_str = str(row.get(col_name, '')).strip()
            if time_str and time_str != 'nan' and time_str != 'Unavailable':
                # Parse AM/PM patterns like "11AM-12PM, 12PM-1PM"
                time_str_upper = time_str.upper()
                
                has_am = False
                has_pm = False
                
                # Check for AM availability
                am_patterns = ['9AM', '10AM', '11AM', '12PM', 'ALL DAY']
                for pattern in am_patterns:
                    if pattern in time_str_upper:
                        has_am = True
                        break
                
                # Check for PM availability
                pm_patterns = ['1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', 'ALL DAY']
                for pattern in pm_patterns:
                    if pattern in time_str_upper:
                        has_pm = True
                        break
                
                if has_am or has_pm:
                    # Convert to time ranges for overlap calculation
                    if has_am and has_pm:
                        availability[day] = (9, 21)  # Full day
                    elif has_am:
                        availability[day] = (9, 13)  # AM only
                    elif has_pm:
                        availability[day] = (13, 21)  # PM only
                    break
        else:
            availability[day] = None
    
    return availability

def find_intern_in_csv(intern_name):
    """Find intern in intern_avail_fall.csv"""
    intern_data = read_csv_dict('intern_avail_fall.csv')
    
    for row in intern_data:
        full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
        # Try different name matching approaches
        if (full_name == intern_name or 
            full_name.replace('  ', ' ').strip() == intern_name.replace('  ', ' ').strip() or
            intern_name.strip() in full_name or
            full_name.strip() in intern_name):
            return row
    
    return None

def find_restaurant_in_csv(restaurant_name):
    """Find restaurant in chef_avail_fall.csv"""
    chef_data = read_csv_dict('chef_avail_fall.csv')
    
    for row in chef_data:
        chef_restaurant = row.get('Restaurant Name', '').strip()
        if (chef_restaurant == restaurant_name or 
            chef_restaurant.replace('  ', ' ').strip() == restaurant_name.replace('  ', ' ').strip() or
            restaurant_name.strip() in chef_restaurant or
            chef_restaurant.strip() in restaurant_name):
            return row
    
    return None

def calculate_csv_overlap(intern_avail, restaurant_avail):
    """Calculate overlap between CSV availabilities"""
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

def verify_8_matches():
    """Verify the 8 Flask matches in original CSV files"""
    print("=== VERIFYING 8 FLASK MATCHES IN ORIGINAL CSV FILES ===\n")
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # The 8 mismatches
    matches = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga "),
        ("Asslin Espinal", "Ssal"),
        ("Giovanni Giacomazzi", "Ssal"), 
        ("Eljanae Robinson", "Teranga "),
        ("Andrea Caballero ", "Tarts de Feybesse"),
        ("Cristina Cubias ", "alaMar Dominican Kitchen"),
        ("Maryam Washington", "alaMar Dominican Kitchen")
    ]
    
    for i, (intern_name, restaurant_name) in enumerate(matches, 1):
        print(f"{i}. {intern_name} -> {restaurant_name}")
        print("-" * 50)
        
        # Find in CSV files
        intern_row = find_intern_in_csv(intern_name)
        restaurant_row = find_restaurant_in_csv(restaurant_name)
        
        if not intern_row:
            print(f"  Intern NOT found in intern_avail_fall.csv")
            print()
            continue
        
        if not restaurant_row:
            print(f"  Restaurant NOT found in chef_avail_fall.csv")
            print()
            continue
        
        print(f"  Found in CSV files")
        
        # Parse availability from CSV
        intern_avail = parse_csv_availability(intern_row, days)
        restaurant_avail = parse_csv_availability(restaurant_row, days)
        
        # Show intern availability
        print(f"  Intern availability from CSV:")
        for day, time_range in intern_avail.items():
            if time_range:
                print(f"    {day}: {time_range[0]}-{time_range[1]}")
        
        # Show restaurant availability
        print(f"  Restaurant availability from CSV:")
        for day, time_range in restaurant_avail.items():
            if time_range:
                print(f"    {day}: {time_range[0]}-{time_range[1]}")
        
        # Calculate overlap
        overlaps, total_hours = calculate_csv_overlap(intern_avail, restaurant_avail)
        
        print(f"  CSV Overlap Analysis:")
        print(f"    Total weekly overlap: {total_hours} hours")
        
        has_overlap = False
        for day, overlap in overlaps.items():
            if overlap:
                has_overlap = True
                print(f"    {day}: {overlap[0]}-{overlap[1]} ({overlap[2]} hours)")
        
        if not has_overlap:
            print("    NO availability overlap found in CSV!")
        else:
            print("    Availability overlap confirmed in CSV!")
        
        print()

if __name__ == "__main__":
    verify_8_matches()
