#!/usr/bin/env python3
"""
Check specific rows in the CSV file
"""

import csv

def check_csv_rows():
    """Check specific rows for Angel, Shelsea, Asslin"""
    print("=== CHECKING CSV ROWS ===")
    
    with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader, 2):  # Start at row 2 (after header)
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            if 'Angel' in full_name or 'Shelsea' in full_name or 'Asslin' in full_name:
                print(f"\nRow {i}: {full_name}")
                print(f"  Monday: '{row.get('Monday', '')}'")
                print(f"  Tuesday: '{row.get('Tuesday', '')}'")
                print(f"  Wednesday: '{row.get('Wednesday', '')}'")
                print(f"  Thursday: '{row.get('Thursday', '')}'")
                print(f"  Friday: '{row.get('Friday', '')}'")
                print(f"  Saturday: '{row.get('Saturday', '')}'")
                print(f"  Sunday: '{row.get('Sunday', '')}'")

if __name__ == "__main__":
    check_csv_rows()
