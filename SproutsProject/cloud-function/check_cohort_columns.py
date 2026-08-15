"""
Check what cohort-related columns exist and their values
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import read_sheet_data

def check_columns():
    """Check cohort columns"""
    
    print("=" * 80)
    print("CHECKING COHORT COLUMNS")
    print("=" * 80)
    print()
    
    # Read intern data
    intern_data = read_sheet_data('Intern Availabilities')
    headers = intern_data[0]
    
    print("INTERN SHEET HEADERS:")
    for i, header in enumerate(headers):
        if 'cohort' in header.lower() or 'season' in header.lower() or 'year' in header.lower():
            print(f"  Column {i}: {header}")
    print()
    
    # Find Juana's row
    print("JUANA'S DATA:")
    for row in intern_data[1:10]:  # Check first 10 rows
        if len(row) > 1:
            name = f"{row[0] if len(row) > 0 else ''} {row[1] if len(row) > 1 else ''}"
            if 'Juana' in name or 'Tomas' in name:
                print(f"  Name: {name}")
                for i, header in enumerate(headers):
                    if 'cohort' in header.lower() or 'season' in header.lower() or 'year' in header.lower():
                        value = row[i] if len(row) > i else 'N/A'
                        print(f"  {header}: {value}")
                print()
                break
    
    # Read chef data
    chef_data = read_sheet_data('Chef Availabilities')
    headers = chef_data[0]
    
    print("CHEF SHEET HEADERS:")
    for i, header in enumerate(headers):
        if 'cohort' in header.lower() or 'season' in header.lower() or 'year' in header.lower():
            print(f"  Column {i}: {header}")
    print()
    
    # Find alaMar's row
    print("ALAMAR'S DATA:")
    for row in chef_data[1:]:
        if len(row) > 2:
            restaurant = row[2] if len(row) > 2 else ''
            if 'alamar' in restaurant.lower() or 'dominican' in restaurant.lower():
                print(f"  Restaurant: {restaurant}")
                for i, header in enumerate(headers):
                    if 'cohort' in header.lower() or 'season' in header.lower() or 'year' in header.lower():
                        value = row[i] if len(row) > i else 'N/A'
                        print(f"  {header}: {value}")
                print()
                break
    
    print("=" * 80)

if __name__ == "__main__":
    check_columns()
