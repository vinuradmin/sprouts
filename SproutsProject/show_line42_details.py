#!/usr/bin/env python3
"""
Show detailed info about line 42
"""

import csv

def show_line42_details():
    """Show detailed info about line 42"""
    print("=== LINE 42 DETAILED ANALYSIS ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                if i == 42:
                    print(f"Line {i}:")
                    print(f"  Intern Name: '{row.get('Intern Name', '')}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        day_matches = row.get(day, '').strip()
                        if day_matches:
                            print(f"  {day}: {day_matches}")
                            # Check for Snail Bar specifically
                            if 'Snail Bar' in day_matches:
                                print(f"    ^^^ SNAIL BAR FOUND! This matches Hungarian algorithm!")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_line42_details()
