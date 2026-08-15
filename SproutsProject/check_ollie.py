#!/usr/bin/env python3
"""
Check Ollie O'Malley in original CSV
"""

import csv

def check_ollie():
    """Check Ollie O'Malley in original CSV"""
    print("=== CHECKING OLLIE O'MALLEY IN ORIGINAL CSV ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                if 'Ollie' in intern_name or 'OMalley' in intern_name:
                    print(f"Row {i}: '{intern_name}'")
                    
                    # Check all days for matches
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    has_matches = False
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches[:100]}...")  # First 100 chars
                            has_matches = True
                    
                    if not has_matches:
                        print(f"  No matches found in any day")
                    
                    print()
                    
    except UnicodeDecodeError:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                if 'Ollie' in intern_name or 'OMalley' in intern_name:
                    print(f"Row {i}: '{intern_name}'")
                    
                    # Check all days for matches
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    has_matches = False
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches[:100]}...")  # First 100 chars
                            has_matches = True
                    
                    if not has_matches:
                        print(f"  No matches found in any day")
                    
                    print()
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ollie()
