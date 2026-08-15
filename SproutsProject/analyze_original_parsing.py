#!/usr/bin/env python3
"""
Analyze how the original algorithm parses and merges time slots
"""

import csv
import re

def analyze_original_parsing():
    """Analyze original algorithm's parsing approach"""
    print("=== ANALYZING ORIGINAL ALGORITHM PARSING ===")
    
    # Get Shelsea's raw CSV data
    print("\n1. SHELSEA'S RAW CSV DATA:")
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Shelsea' in full_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        raw_time = row.get(day, '').strip()
                        print(f"  {day} raw: '{raw_time}'")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Get Abaca's raw CSV data
    print("\n2. ABACA'S RAW CSV DATA:")
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Abaca' in restaurant_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        raw_time = row.get(day, '').strip()
                        print(f"  {day} raw: '{raw_time}'")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Test the original algorithm's slot parsing
    print("\n3. TESTING ORIGINAL ALGORITHM SLOT PARSING:")
    
    # Import the original Slot class
    try:
        import sys
        sys.path.append('..')  # Add parent directory to path
        from Slot import Slot
        
        # Test Shelsea's Saturday availability
        shelsea_saturday = "9AM-9PM"
        print(f"Shelsea Saturday: '{shelsea_saturday}'")
        
        # Parse with original algorithm
        slots = Slot.combine_slots(shelsea_saturday)
        print(f"Parsed slots: {[str(slot) for slot in slots]}")
        
        # Test Abaca's availability
        abaca_wednesday = "10AM-11AM, 11AM-12PM, 12PM-1PM, 2PM-3PM, 3PM-4PM, 4PM-5PM"
        print(f"Abaca Wednesday: '{abaca_wednesday}'")
        
        slots = Slot.combine_slots(abaca_wednesday)
        print(f"Parsed slots: {[str(slot) for slot in slots]}")
        
    except ImportError as e:
        print(f"Could not import original Slot class: {e}")
        print("Let's analyze the parsing pattern manually...")
        
        # Manual analysis of the patterns
        print(f"\nManual analysis:")
        print(f"Shelsea patterns: '9AM-9PM' should become Slot(9, 21)")
        print(f"Abaca patterns: '10AM-11AM, 11AM-12PM, 12PM-1PM, 2PM-3PM, 3PM-4PM, 4PM-5PM'")
        print(f"  Should merge consecutive slots: 10AM-1PM, 2PM-5PM")
        print(f"  Then filter by 4-hour minimum: keep only 2PM-5PM (3 hours) - REJECTED")
        print(f"  Or if merging across gap: 10AM-5PM (7 hours) - ACCEPTED")

def test_time_conversion():
    """Test time conversion logic"""
    print("\n4. TESTING TIME CONVERSION LOGIC:")
    
    test_times = [
        "9AM", "10AM", "11AM", "12AM", "12PM", "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM"
    ]
    
    def to_24_hour(time_str):
        """Convert AM/PM time to 24-hour format"""
        time_str = time_str.strip()
        
        if 'AM' in time_str:
            hour = int(time_str.replace('AM', ''))
            return 12 if hour == 12 else hour
        elif 'PM' in time_str:
            hour = int(time_str.replace('PM', ''))
            return 12 + hour if hour != 12 else 12
        return int(time_str)
    
    for time_str in test_times:
        hour_24 = to_24_hour(time_str)
        print(f"  {time_str} -> {hour_24}")

if __name__ == "__main__":
    analyze_original_parsing()
    test_time_conversion()
