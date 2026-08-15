#!/usr/bin/env python3
"""
Parse actual time ranges from CSV data accurately
"""

import re
from datetime import datetime

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

def test_parsing():
    """Test the parsing with actual CSV data"""
    print("=== ACCURATE TIME PARSING TEST ===")
    
    test_cases = [
        "11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM",
        "12PM-1PM", 
        "All Day (9AM-9PM)",
        "5PM-6PM, 6PM-7PM, 7PM-8PM, 8PM-9PM",
        "9AM-10AM, 10AM-11AM, 11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        slots = parse_time_slots(test_case)
        print(f"\nTest {i}: '{test_case}'")
        print(f"  Parsed slots: {slots}")
        
        if slots:
            total_hours = sum(end - start for start, end in slots)
            print(f"  Total hours: {total_hours}")
            
            # Show time range
            min_start = min(start for start, end in slots)
            max_end = max(end for start, end in slots)
            print(f"  Overall range: {min_start}:00-{max_end}:00")

if __name__ == "__main__":
    test_parsing()
