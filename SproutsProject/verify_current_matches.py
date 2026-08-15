#!/usr/bin/env python3
"""
Verify if all current Hungarian algorithm matches were in original algorithm options
"""

import csv
import re

def verify_current_matches():
    """Verify if current matches were in original algorithm"""
    print("=== VERIFYING CURRENT MATCHES IN ORIGINAL ALGORITHM ===")
    
    # Load original results
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    except UnicodeDecodeError:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    
    # Current Hungarian algorithm matches
    current_matches = [
        ("Zhijian Liu", "Millennium Restaurant"),
        ("Aliyatt  Rodgers", "Millennium Restaurant"),
        ("Samuel  Gonzalez ", "Tarts de Feybesse"),
        ("Enrique Marroquin", "Tarts de Feybesse"),
        ("Ollie  OMalley", "Snail Bar"),
        ("Jayden Piansay", "Snail Bar"),
        ("Gyllibhet  Palacio", "Burdell"),
        ("Eljanae Robinson", "Burdell"),
        ("Asslin Espinal", "Arquet"),
        ("Giovanni Giacomazzi", "Arquet")
    ]
    
    verified_count = 0
    not_found_count = 0
    
    for intern_name, restaurant_name in current_matches:
        print(f"\n{intern_name} -> {restaurant_name}")
        print("-" * 50)
        
        # Find intern in original results
        found_in_original = False
        for row in original_results:
            original_intern = row.get('Intern Name', '').strip()
            if intern_name in original_intern or original_intern in intern_name:
                found_in_original = True
                print(f"Found in original results as: '{original_intern}'")
                
                # Check all days for this restaurant
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                restaurant_found = False
                
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
                                    
                                    if restaurant_name.strip() in original_restaurant:
                                        restaurant_found = True
                                        print(f"  Found in original: {day} -> {original_restaurant} ({commute}) [{start}-{end}] ({hours} hrs)")
                
                if restaurant_found:
                    verified_count += 1
                    print(f"  STATUS: VERIFIED in original algorithm")
                else:
                    not_found_count += 1
                    print(f"  STATUS: NOT FOUND in original algorithm options")
                break
        
        if not found_in_original:
            not_found_count += 1
            print(f"  STATUS: INTERN NOT FOUND in original results")
    
    print(f"\n" + "="*60)
    print(f"VERIFICATION SUMMARY:")
    print(f"Total current matches: {len(current_matches)}")
    print(f"Verified in original: {verified_count}")
    print(f"Not found in original: {not_found_count}")
    print(f"Verification rate: {verified_count/len(current_matches)*100:.1f}%")
    
    if not_found_count > 0:
        print(f"\n{not_found_count} matches were NOT in original algorithm options")
        print("This suggests the Hungarian algorithm found better matches!")
    else:
        print(f"\nAll current matches were available in original algorithm")

if __name__ == "__main__":
    verify_current_matches()
