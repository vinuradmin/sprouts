#!/usr/bin/env python3
"""
Show detailed availability and options for rejected cases in original algorithm
"""

import csv
import re

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
            end_hour = int(match.group(2)) + 12
            return [(start_hour, end_hour)]
    
    # Parse individual time slots
    slots = []
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
                    start_hour = 0
            else:
                if start_hour != 12:
                    start_hour += 12
            
            if end_period == 'AM':
                if end_hour == 12:
                    end_hour = 0
            else:
                if end_hour != 12:
                    end_hour += 12
            
            slots.append((start_hour, end_hour))
    
    return slots

def get_intern_availability(intern_name):
    """Get intern availability from CSV"""
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if intern_name in full_name or full_name in intern_name:
                    availability = {}
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = parse_time_slots(time_str)
                        if slots:
                            availability[day] = slots
                    
                    return availability
    except Exception as e:
        print(f"Error reading intern CSV: {e}")
        return {}

def get_restaurant_availability(restaurant_name):
    """Get restaurant availability from CSV"""
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                chef_restaurant = row.get('Restaurant Name', '').strip()
                if restaurant_name.strip() in chef_restaurant or chef_restaurant in restaurant_name.strip():
                    availability = {}
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = parse_time_slots(time_str)
                        if slots:
                            availability[day] = slots
                    
                    return availability
    except Exception as e:
        print(f"Error reading chef CSV: {e}")
        return {}

def calculate_total_hours(availability):
    """Calculate total weekly hours from availability"""
    total = 0
    for day, slots in availability.items():
        for start, end in slots:
            total += end - start
    return total

def show_detailed_options():
    """Show detailed availability and options for rejected cases"""
    print("=== DETAILED ORIGINAL ALGORITHM OPTIONS ===")
    
    # Load original results
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    except UnicodeDecodeError:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    
    # Test cases
    test_cases = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga "),
        ("Asslin Espinal", "Ssal")
    ]
    
    for intern_name, restaurant_name in test_cases:
        print(f"\n{'='*80}")
        print(f"INTERN: {intern_name}")
        print(f"{'='*80}")
        
        # Show intern availability
        intern_avail = get_intern_availability(intern_name)
        print(f"\nINTERN AVAILABILITY:")
        if intern_avail:
            total_hours = calculate_total_hours(intern_avail)
            print(f"  Total weekly hours: {total_hours}")
            for day, slots in intern_avail.items():
                if slots:
                    for start, end in slots:
                        print(f"    {day}: {start:02d}:00-{end:02d}:00 ({end-start} hrs)")
        else:
            print("  No availability found")
        
        # Find intern in original results
        intern_row = None
        for row in original_results:
            original_intern = row.get('Intern Name', '').strip()
            if intern_name in original_intern or original_intern in intern_name:
                intern_row = row
                break
        
        if intern_row:
            print(f"\nORIGINAL ALGORITHM OPTIONS:")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                day_matches = intern_row.get(day, '').strip()
                if day_matches:
                    print(f"\n  {day}:")
                    lines = day_matches.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                            if match:
                                restaurant = match.group(1).strip()
                                commute = match.group(2).strip()
                                start = int(match.group(3))
                                end = int(match.group(4))
                                hours = end - start
                                
                                # Highlight the target restaurant
                                if restaurant_name.strip() in restaurant:
                                    print(f"    -> {restaurant} ({commute}) [{start}-{end}] ({hours} hrs) ⭐ TARGET")
                                else:
                                    print(f"       {restaurant} ({commute}) [{start}-{end}] ({hours} hrs)")
                                
                                # Show restaurant availability for comparison
                                rest_avail = get_restaurant_availability(restaurant)
                                if rest_avail and day in rest_avail:
                                    for r_start, r_end in rest_avail[day]:
                                        print(f"         Restaurant available: {r_start:02d}:00-{r_end:02d}:00")
        
        print(f"\nTARGET RESTAURANT: {restaurant_name}")
        restaurant_avail = get_restaurant_availability(restaurant_name)
        if restaurant_avail:
            total_hours = calculate_total_hours(restaurant_avail)
            print(f"  Total weekly hours: {total_hours}")
            for day, slots in restaurant_avail.items():
                if slots:
                    for start, end in slots:
                        print(f"    {day}: {start:02d}:00-{end:02d}:00 ({end-start} hrs)")
        else:
            print("  No availability found")
        
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    show_detailed_options()
