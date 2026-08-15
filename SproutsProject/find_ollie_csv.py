#!/usr/bin/env python3
"""
Find Ollie in the original CSV
"""

import csv

def find_ollie_csv():
    """Find Ollie in the original CSV"""
    print("=== FINDING OLLIE IN ORIGINAL CSV ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                if intern_name:  # Only check non-empty names
                    if 'Ollie' in intern_name.lower() or 'omalley' in intern_name.lower():
                        print(f"Line {i}: '{intern_name}'")
                        
                        # Check all days for matches
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        has_matches = False
                        
                        for day in days:
                            day_matches = row.get(day, '').strip()
                            if day_matches:
                                has_matches = True
                                print(f"  {day}: {day_matches[:100]}...")
                        
                        if not has_matches:
                            print(f"  No matches found")
                        
                        print()
                        break
            else:
                print("Ollie not found with non-empty name")
                
    except Exception as e:
        print(f"Error: {e}")
    
    # Also check for empty names that might be Ollie
    print("\n=== CHECKING FOR EMPTY NAMES ===")
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            empty_count = 0
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                if not intern_name:
                    empty_count += 1
                    if empty_count <= 3:  # Show first 3 empty names
                        print(f"Line {i}: Empty name")
                        # Check if this has Snail Bar matches
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        for day in days:
                            day_matches = row.get(day, '').strip()
                            if 'Snail Bar' in day_matches:
                                print(f"  {day}: {day_matches}")
                                break
                    elif empty_count == 4:
                        print(f"... ({empty_count} total empty names found)")
                        break
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_ollie_csv()
