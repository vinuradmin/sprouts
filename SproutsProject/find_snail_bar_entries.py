#!/usr/bin/env python3
"""
Find all entries with Snail Bar to locate Ollie
"""

import csv

def find_snail_bar_entries():
    """Find all entries with Snail Bar"""
    print("=== FINDING ALL SNAIL BAR ENTRIES ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            snail_bar_entries = []
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Check all days for Snail Bar
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                for day in days:
                    day_matches = row.get(day, '').strip()
                    if 'Snail Bar' in day_matches:
                        snail_bar_entries.append((i, intern_name, day, day_matches))
                        break  # Only need to know it has Snail Bar
            
            print(f"Found {len(snail_bar_entries)} entries with Snail Bar:")
            print()
            
            for line_num, intern_name, day, day_matches in snail_bar_entries:
                print(f"Line {line_num}: '{intern_name}' -> {day}")
                print(f"  {day_matches}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_snail_bar_entries()
