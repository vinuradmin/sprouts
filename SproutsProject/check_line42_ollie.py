#!/usr/bin/env python3
"""
Check if line 42 empty name is Ollie by looking at restaurant matches
"""

import csv

def check_line42_ollie():
    """Check if line 42 empty name is Ollie"""
    print("=== CHECKING LINE 42 FOR OLLIE ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                if i == 42:
                    intern_name = row.get('Intern Name', '').strip()
                    print(f"Line 42: '{intern_name}' (empty)")
                    
                    # Check all days for matches
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches}")
                            
                            # Check if this contains Snail Bar
                            if 'Snail Bar' in day_matches:
                                print(f"    ^^^ This matches Hungarian algorithm's Snail Bar assignment!")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Also check intern availability CSV to confirm this is Ollie
    print("=== CHECKING INTERN AVAILABILITY CSV FOR OLLIE ===")
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Ollie' in full_name:
                    print(f"Found Ollie in intern CSV: '{full_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        if time_str:
                            print(f"  {day}: {time_str}")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_line42_ollie()
