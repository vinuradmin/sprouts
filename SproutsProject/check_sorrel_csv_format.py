#!/usr/bin/env python3
"""
Check the exact CSV format for Sorrel Restaurant
"""

import csv

def check_sorrel_csv_format():
    """Check the exact CSV format for Sorrel Restaurant"""
    print("=== SORREL RESTAURANT CSV FORMAT ===")
    
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Sorrel' in restaurant_name:
                    print(f"Restaurant: '{restaurant_name}'")
                    
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        raw_time = row.get(day, '').strip()
                        print(f"  {day}: '{raw_time}'")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sorrel_csv_format()
