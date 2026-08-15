#!/usr/bin/env python3
"""
Check lines around 42 to find Ollie
"""

import csv

def check_lines_around_42():
    """Check lines around 42 to find Ollie"""
    print("=== CHECKING LINES AROUND 42 ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            lines = list(reader)
            
            # Check lines 40-45
            for i in range(39, min(45, len(lines))):
                row = lines[i]
                intern_name = row.get('Intern Name', '').strip()
                line_num = i + 1
                
                print(f"Line {line_num}: '{intern_name}'")
                
                # If this looks like it could be Ollie, show details
                if intern_name and ('ollie' in intern_name.lower() or 'omalley' in intern_name.lower()):
                    print(f"  ^^^ POTENTIAL OLLIE MATCH!")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"    {day}: {day_matches}")
                            if 'Snail Bar' in day_matches:
                                print(f"      ^^^ SNAIL BAR MATCH!")
                
                # If empty name, check for Snail Bar
                if not intern_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if 'Snail Bar' in day_matches:
                            print(f"  ^^^ EMPTY NAME WITH SNAIL BAR - LIKELY OLLIE!")
                            print(f"    {day}: {day_matches}")
                            break
                
                print()
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_lines_around_42()
