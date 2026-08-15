#!/usr/bin/env python3
"""
Check if rejected cases had options in the original algorithm
"""

import csv
import re

def check_original_options():
    """Check original algorithm options for rejected cases"""
    print("=== CHECKING ORIGINAL ALGORITHM OPTIONS ===")
    
    # Load original results
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    except UnicodeDecodeError:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    
    # Test cases that were rejected
    rejected_cases = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga "),
        ("Asslin Espinal", "Ssal")
    ]
    
    for intern_name, restaurant_name in rejected_cases:
        print(f"\n{intern_name} -> {restaurant_name}")
        print("-" * 40)
        
        # Find intern in original results
        found = False
        for row in original_results:
            original_intern = row.get('Intern Name', '').strip()
            if intern_name in original_intern or original_intern in intern_name:
                found = True
                print(f"Found in original results as: '{original_intern}'")
                
                # Check all days for any restaurant options
                has_options = False
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                for day in days:
                    day_matches = row.get(day, '').strip()
                    if day_matches:
                        # Parse restaurant names from this day
                        lines = day_matches.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Extract restaurant name
                                match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                                if match:
                                    original_restaurant = match.group(1).strip()
                                    commute = match.group(2).strip()
                                    
                                    if restaurant_name.strip() in original_restaurant:
                                        has_options = True
                                        print(f"  ✅ Found in original: {day} -> {original_restaurant} ({commute})")
                                    else:
                                        # Show what options they did have
                                        if not has_options:
                                            print(f"  Available options on {day}:")
                                            has_options = True
                                        print(f"    - {original_restaurant} ({commute})")
                
                if not has_options:
                    print(f"  ❌ No options found in original algorithm")
                break
        
        if not found:
            print(f"  ❌ Not found in original results")

if __name__ == "__main__":
    check_original_options()
