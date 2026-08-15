#!/usr/bin/env python3
"""
Simple search for Ollie avoiding encoding issues
"""

import csv

def simple_ollie_search():
    """Simple search for Ollie"""
    print("=== SIMPLE OLLIE SEARCH ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            ollie_found = False
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Simple check for Ollie
                if intern_name and ('Ollie' in intern_name):
                    print(f"FOUND OLLIE: Line {i}: '{intern_name}'")
                    ollie_found = True
                    
                    # Check for Snail Bar
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if 'Snail Bar' in day_matches:
                            print(f"  SNAIL BAR: {day} - {day_matches}")
                    
                    print()
                    
            if not ollie_found:
                print("Ollie not found by exact name match")
                
                # Try case insensitive
                file.seek(0)
                reader = csv.DictReader(file)
                
                for i, row in enumerate(reader, 1):
                    intern_name = row.get('Intern Name', '').strip()
                    
                    if intern_name and 'ollie' in intern_name.lower():
                        print(f"FOUND OLLIE (lowercase): Line {i}: '{intern_name}'")
                        
                        # Check for Snail Bar
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        
                        for day in days:
                            day_matches = row.get(day, '').strip()
                            if 'Snail Bar' in day_matches:
                                print(f"  SNAIL BAR: {day} - {day_matches}")
                        
                        print()
                        break
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_ollie_search()
