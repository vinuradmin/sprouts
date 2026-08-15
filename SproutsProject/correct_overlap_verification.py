#!/usr/bin/env python3
"""
Verify overlap with accurate time parsing
"""

import csv
import re
from collections import defaultdict

def parse_time_slots(time_str):
    """Parse time slots like '11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM'"""
    if not time_str or time_str.strip() == '' or time_str.strip() == 'Unavailable':
        return []
    
    time_str = time_str.upper()
    
    # Handle "All Day (9AM-9PM)" format
    if 'ALL DAY' in time_str:
        match = re.search(r'(\d+)AM-(\d+)PM', time_str)
        if match:
            start_hour = int(match.group(1))
            end_hour = int(match.group(2)) + 12  # Convert PM to 24-hour
            return [(start_hour, end_hour)]
    
    # Parse individual time slots - handle AM-PM transitions
    slots = []
    
    # Split by comma and process each slot
    individual_slots = time_str.split(',')
    for slot in individual_slots:
        slot = slot.strip()
        # Match patterns like "11AM-12PM", "12PM-1PM", "5PM-6PM"
        match = re.match(r'(\d+)(AM|PM)-(\d+)(AM|PM)', slot)
        if match:
            start_hour = int(match.group(1))
            start_period = match.group(2)
            end_hour = int(match.group(3))
            end_period = match.group(4)
            
            # Convert to 24-hour format
            if start_period == 'AM':
                if start_hour == 12:  # 12AM = 0
                    start_hour = 0
            else:  # PM
                if start_hour != 12:  # 12PM = 12
                    start_hour += 12
            
            if end_period == 'AM':
                if end_hour == 12:  # 12AM = 0
                    end_hour = 0
            else:  # PM
                if end_hour != 12:  # 12PM = 12
                    end_hour += 12
            
            slots.append((start_hour, end_hour))
    
    return slots

def calculate_overlap(intern_slots, restaurant_slots):
    """Calculate overlap between intern and restaurant time slots"""
    overlap_hours = 0
    overlap_details = []
    
    for intern_start, intern_end in intern_slots:
        for rest_start, rest_end in restaurant_slots:
            # Calculate overlap
            overlap_start = max(intern_start, rest_start)
            overlap_end = min(intern_end, rest_end)
            
            if overlap_end > overlap_start:
                hours = overlap_end - overlap_start
                overlap_hours += hours
                overlap_details.append((overlap_start, overlap_end, hours))
    
    return overlap_hours, overlap_details

def verify_correct_overlaps():
    """Verify overlaps with correct time parsing"""
    print("=== CORRECT OVERLAP VERIFICATION ===")
    
    # Read CSV files
    with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
        intern_reader = csv.DictReader(file)
        intern_data = list(intern_reader)
    
    with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
        chef_reader = csv.DictReader(file)
        chef_data = list(chef_reader)
    
    # Test cases
    test_cases = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga "),
        ("Asslin Espinal", "Ssal")
    ]
    
    for intern_name, restaurant_name in test_cases:
        print(f"\n{intern_name} -> {restaurant_name}")
        print("-" * 40)
        
        # Find intern data
        intern_row = None
        for row in intern_data:
            full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
            if intern_name in full_name:
                intern_row = row
                break
        
        # Find restaurant data
        restaurant_row = None
        for row in chef_data:
            if restaurant_name.strip() in row.get('Restaurant Name', '').strip():
                restaurant_row = row
                break
        
        if not intern_row or not restaurant_row:
            print("  Data not found")
            continue
        
        # Parse availability for each day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        total_weekly_overlap = 0
        
        for day in days:
            intern_slots = parse_time_slots(intern_row.get(day, ''))
            restaurant_slots = parse_time_slots(restaurant_row.get(day, ''))
            
            if intern_slots and restaurant_slots:
                overlap_hours, overlap_details = calculate_overlap(intern_slots, restaurant_slots)
                if overlap_hours > 0:
                    total_weekly_overlap += overlap_hours
                    print(f"  {day}: {overlap_hours} hours", end="")
                    for start, end, hours in overlap_details:
                        print(f" ({start}:00-{end}:00)", end="")
                    print()
        
        print(f"  Total weekly overlap: {total_weekly_overlap} hours")

if __name__ == "__main__":
    verify_correct_overlaps()
