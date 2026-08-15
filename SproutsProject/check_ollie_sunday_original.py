#!/usr/bin/env python3
"""
Check what overlap the original algorithm found for Ollie on Sunday
"""

import csv
import re

def check_ollie_sunday_original():
    """Check what overlap the original algorithm found for Ollie on Sunday"""
    print("=== CHECKING OLLIE SUNDAY IN ORIGINAL ALGORITHM ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Find Ollie (line 13 with special character)
                if i == 13 or ('Ollie' in intern_name and intern_name.strip()):
                    print(f"Line {i}: '{intern_name}'")
                    
                    # Check Sunday specifically
                    sunday_matches = row.get('Sunday', '').strip()
                    print(f"Sunday: '{sunday_matches}'")
                    
                    if sunday_matches:
                        print(f"\nParsing Sunday matches:")
                        lines = sunday_matches.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Parse restaurant option
                                match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                                if match:
                                    restaurant = match.group(1).strip()
                                    commute = match.group(2).strip()
                                    start = int(match.group(3))
                                    end = int(match.group(4))
                                    hours = end - start
                                    
                                    print(f"  -> {restaurant} ({commute}) [{start}-{end}] ({hours} hrs)")
                                    
                                    # Check if this is Snail Bar
                                    if 'Snail Bar' in restaurant:
                                        print(f"    ^^^ SNAIL BAR FOUND!")
                                        print(f"    Hours: {hours}, Time: {start}-{end}")
                    else:
                        print("No Sunday matches found")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error reading results CSV: {e}")
    
    # Also check the raw CSV data to see what's actually there
    print("\n=== RAW SUNDAY DATA ANALYSIS ===")
    
    # Get Ollie's Sunday availability
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Ollie' in full_name:
                    sunday_time = row.get('Sunday', '').strip()
                    print(f"Ollie's Sunday CSV: '{sunday_time}'")
                    break
                    
    except Exception as e:
        print(f"Error reading intern CSV: {e}")
    
    # Get Snail Bar's Sunday availability
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Snail Bar' in restaurant_name:
                    sunday_time = row.get('Sunday', '').strip()
                    print(f"Snail Bar's Sunday CSV: '{sunday_time}'")
                    break
                    
    except Exception as e:
        print(f"Error reading chef CSV: {e}")
    
    # Manual calculation
    print(f"\n=== MANUAL OVERLAP CALCULATION ===")
    
    # Parse both availabilities
    def parse_time_slots(time_str):
        if not time_str or time_str.strip() == '' or time_str.strip() == 'Unavailable':
            return []
        
        time_str = time_str.strip()
        slots = []
        
        # Handle "All Day (9AM-9PM)" format
        if 'All Day' in time_str:
            match = re.search(r'(\d+)AM-(\d+)PM', time_str)
            if match:
                start_hour = int(match.group(1))
                end_hour = int(match.group(2)) + 12
                return [(start_hour, end_hour)]
        
        # Parse individual time slots
        individual_slots = time_str.split(',')
        for slot in individual_slots:
            slot = slot.strip()
            match = re.match(r'(\d+)(AM|PM)-(\d+)(AM|PM)', slot)
            if match:
                start_hour = int(match.group(1))
                start_period = match.group(2)
                end_hour = int(match.group(3))
                end_period = match.group(4)
                
                # Convert to 24-hour format
                if start_period == 'AM':
                    if start_hour == 12:
                        start_24 = 0
                    else:
                        start_24 = start_hour
                else:  # PM
                    if start_hour == 12:
                        start_24 = 12
                    else:
                        start_24 = start_hour + 12
                
                if end_period == 'AM':
                    if end_hour == 12:
                        end_24 = 0
                    else:
                        end_24 = end_hour
                else:  # PM
                    if end_hour == 12:
                        end_24 = 12
                    else:
                        end_24 = end_hour + 12
                
                slots.append((start_24, end_24))
        
        return slots
    
    ollie_sunday = "All Day (9AM-9PM)"
    snail_sunday = "All Day (9AM-9PM)"
    
    ollie_slots = parse_time_slots(ollie_sunday)
    snail_slots = parse_time_slots(snail_sunday)
    
    print(f"Ollie Sunday slots: {ollie_slots}")
    print(f"Snail Bar Sunday slots: {snail_slots}")
    
    # Calculate overlap
    overlap_hours = 0
    for o_start, o_end in ollie_slots:
        for s_start, s_end in snail_slots:
            overlap_start = max(o_start, s_start)
            overlap_end = min(o_end, s_end)
            
            if overlap_end > overlap_start:
                overlap_hours += overlap_end - overlap_start
                print(f"  Overlap: {overlap_start:02d}-{overlap_end:02d} = {overlap_end - overlap_start} hours")
    
    print(f"\nSunday total overlap: {overlap_hours} hours")

if __name__ == "__main__":
    check_ollie_sunday_original()
