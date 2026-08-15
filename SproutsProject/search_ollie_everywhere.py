#!/usr/bin/env python3
"""
Search for Ollie in the entire CSV
"""

import csv

def search_ollie_everywhere():
    """Search for Ollie in the entire CSV"""
    print("=== SEARCHING FOR OLLIE EVERYWHERE ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Check for any variation of Ollie
                if intern_name and ('ollie' in intern_name.lower() or 'omalley' in intern_name.lower()):
                    print(f"Line {i}: '{intern_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches}")
                            if 'Snail Bar' in day_matches:
                                print(f"    ^^^ SNAIL BAR MATCH!")
                    
                    print()
                    
        # Also check if there are any special characters or encoding issues
        print("=== CHECKING FOR ENCODING ISSUES ===")
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '')
                
                # Check for any non-ASCII characters that might be Ollie
                if intern_name and any(ord(char) > 127 for char in intern_name):
                    print(f"Line {i}: '{intern_name}' (contains non-ASCII)")
                    
                    # Check if this could be Ollie
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if 'Snail Bar' in day_matches:
                            print(f"  ^^^ POTENTIAL OLLIE WITH SNAIL BAR!")
                            print(f"  {day}: {day_matches}")
                    print()
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_ollie_everywhere()
