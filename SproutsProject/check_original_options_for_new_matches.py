#!/usr/bin/env python3
"""
Check what options the 3 new matches had in original algorithm
"""

import csv
import re

def check_original_options_for_new_matches():
    """Check original options for the 3 new Hungarian matches"""
    print("=== ORIGINAL OPTIONS FOR NEW HUNGARIAN MATCHES ===")
    
    # Load original results
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    except UnicodeDecodeError:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    
    # The 3 new matches
    new_matches = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Abaca "),
        ("Ollie  OMalley", "Snail Bar")
    ]
    
    for intern_name, restaurant_name in new_matches:
        print(f"\n{intern_name} -> {restaurant_name}")
        print("=" * 60)
        
        # Find intern in original results
        found_in_original = False
        for row in original_results:
            original_intern = row.get('Intern Name', '').strip()
            if intern_name in original_intern or original_intern in intern_name:
                found_in_original = True
                print(f"Found in original results as: '{original_intern}'")
                
                # Check all days for any restaurant options
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                has_options = False
                
                for day in days:
                    day_matches = row.get(day, '').strip()
                    if day_matches:
                        lines = day_matches.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                                if match:
                                    original_restaurant = match.group(1).strip()
                                    commute = match.group(2).strip()
                                    start = int(match.group(3))
                                    end = int(match.group(4))
                                    hours = end - start
                                    
                                    has_options = True
                                    # Highlight if this is the target restaurant
                                    if restaurant_name.strip() in original_restaurant:
                                        print(f"  -> {day}: {original_restaurant} ({commute}) [{start}-{end}] ({hours} hrs) TARGET")
                                    else:
                                        print(f"     {day}: {original_restaurant} ({commute}) [{start}-{end}] ({hours} hrs)")
                
                if not has_options:
                    print(f"  No options found in original algorithm")
                break
        
        if not found_in_original:
            print(f"  Intern not found in original results")

if __name__ == "__main__":
    check_original_options_for_new_matches()
