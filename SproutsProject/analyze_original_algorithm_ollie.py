#!/usr/bin/env python3
"""
Analyze why the original algorithm didn't find Snail Bar as valid for Ollie
"""

import csv
import re

def analyze_original_algorithm_ollie():
    """Analyze why original algorithm rejected Ollie -> Snail Bar"""
    print("=== ANALYZING ORIGINAL ALGORITHM OLLIE -> SNAIL BAR ===")
    
    # Get Ollie's availability from intern CSV
    print("\n1. OLLIE'S AVAILABILITY:")
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Ollie' in full_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        print(f"  {day}: '{time_str}'")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error reading intern CSV: {e}")
    
    # Get Snail Bar's availability from chef CSV
    print("\n2. SNAIL BAR AVAILABILITY:")
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Snail Bar' in restaurant_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        print(f"  {day}: '{time_str}'")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error reading chef CSV: {e}")
    
    # Check original algorithm results for Ollie
    print("\n3. ORIGINAL ALGORITHM RESULTS FOR OLLIE:")
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Find Ollie (line 13 with special character)
                if i == 13 or ('Ollie' in intern_name and intern_name.strip()):
                    print(f"Line {i}: '{intern_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches}")
                            # Parse each restaurant option
                            lines = day_matches.split('\n')
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
                                        
                                        print(f"    -> {restaurant} ({commute}) [{start}-{end}] ({hours} hrs)")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error reading results CSV: {e}")
    
    # Analyze why Snail Bar might have been rejected
    print("\n4. ANALYSIS: WHY SNAIL BAR MIGHT BE REJECTED")
    
    # Check if Snail Bar meets requirements
    print("Checking if Snail Bar meets requirements:")
    
    # Parse availability properly
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
    
    # Check Ollie's Saturday availability
    ollie_saturday = "All Day (9AM-9PM)"
    ollie_slots = parse_time_slots(ollie_saturday)
    print(f"Ollie Saturday: {ollie_slots}")
    
    # Check Snail Bar's Saturday availability  
    snail_saturday = "10AM-11AM, 11AM-12PM, 12PM-1PM, 2PM-3PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    snail_slots = parse_time_slots(snail_saturday)
    print(f"Snail Bar Saturday: {snail_slots}")
    
    # Calculate overlap
    overlap_hours = 0
    for o_start, o_end in ollie_slots:
        for s_start, s_end in snail_slots:
            overlap_start = max(o_start, s_start)
            overlap_end = min(o_end, s_end)
            
            if overlap_end > overlap_start:
                overlap_hours += overlap_end - overlap_start
    
    print(f"\nSaturday overlap: {overlap_hours} hours")
    
    # Check requirements
    print(f"\nREQUIREMENTS CHECK:")
    print(f"  12-hour weekly minimum: {'PASS' if overlap_hours >= 12 else 'FAIL'}")
    print(f"  4-hour daily minimum: {'PASS' if overlap_hours >= 4 else 'FAIL'}")
    print(f"  2-day minimum: {'PASS' if overlap_hours >= 4 else 'FAIL'}")
    
    # Check if this would be considered valid by original algorithm
    print(f"\nORIGINAL ALGORITHM LOGIC:")
    print(f"  - Does this meet the 12-hour weekly requirement? {'YES' if overlap_hours >= 12 else 'NO'}")
    print(f"  - Does this meet the 4-hour daily minimum? {'YES' if overlap_hours >= 4 else 'NO'}")
    print(f"  - Would this be considered a valid match? {'YES' if overlap_hours >= 12 else 'NO'}")

if __name__ == "__main__":
    analyze_original_algorithm_ollie()
