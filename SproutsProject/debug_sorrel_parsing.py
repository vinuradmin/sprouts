#!/usr/bin/env python3
"""
Debug Sorrel Restaurant parsing issue
"""

import csv
import re

def debug_sorrel_parsing():
    """Debug Sorrel Restaurant CSV parsing"""
    print("=== DEBUGGING SORREL RESTAURANT PARSING ===")
    
    # Get Sorrel's raw CSV data
    print("\n1. SORREL RESTAURANT RAW CSV DATA:")
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Sorrel' in restaurant_name:
                    print(f"Restaurant: '{restaurant_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        raw_time = row.get(day, '').strip()
                        print(f"  {day} raw: '{raw_time}'")
                        
                        # Parse with our current method
                        slots = parse_time_slots_current(raw_time)
                        print(f"  {day} parsed: {slots}")
                        
                        # What should it be?
                        if '10-17' in raw_time or '10AM-5PM' in raw_time:
                            print(f"  {day} should be: [(10, 17)] (7 hours)")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

def parse_time_slots_current(time_str):
    """Current parsing method"""
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

def test_sorrel_parsing():
    """Test different parsing approaches for Sorrel"""
    print("\n2. TESTING DIFFERENT PARSING APPROACHES:")
    
    # Test cases based on what we might see in CSV
    test_cases = [
        "10AM-5PM",
        "10AM-5PM, 5PM-6PM", 
        "10AM-11AM, 11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM, 4PM-5PM",
        "10-17",
        "10:00-17:00"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_case}'")
        
        # Current method
        current_slots = parse_time_slots_current(test_case)
        print(f"  Current parsing: {current_slots}")
        
        # Calculate total hours
        total_hours = sum(end - start for start, end in current_slots)
        print(f"  Total hours: {total_hours}")
        
        # Check if it meets 4-hour minimum
        meets_4hr = any((end - start) >= 4 for start, end in current_slots)
        print(f"  Meets 4hr minimum: {meets_4hr}")

if __name__ == "__main__":
    debug_sorrel_parsing()
    test_sorrel_parsing()
