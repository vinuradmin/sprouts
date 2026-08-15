#!/usr/bin/env python3
"""
Debug Abaca restaurant availability specifically
"""

import csv
import re

def debug_abaca():
    """Debug Abaca restaurant availability"""
    print("=== DEBUGGING ABACA AVAILABILITY ===")
    
    # Check chef CSV for Abaca
    print("Chef CSV data for Abaca:")
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Abaca' in restaurant_name:
                    print(f"Found: '{restaurant_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        print(f"  {day}: '{time_str}'")
                    break
    except Exception as e:
        print(f"Error: {e}")
    
    # Check intern CSV for Angel Ruiz
    print(f"\nIntern CSV data for Angel Ruiz:")
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Angel Ruiz' in full_name:
                    print(f"Found: '{full_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        print(f"  {day}: '{time_str}'")
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_abaca()
