"""
Check which cohorts Juana and alaMar are in
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    find_column_index
)

def check_cohorts():
    """Check cohorts for Juana and alaMar"""
    
    print("=" * 80)
    print("CHECKING COHORTS")
    print("=" * 80)
    print()
    
    # Read raw data (no filtering)
    intern_data = read_sheet_data('Intern Availabilities')
    chef_data = read_sheet_data('Chef Availabilities')
    
    # Find Juana
    print("SEARCHING FOR JUANA TOMAS:")
    headers = intern_data[0]
    first_name_col = find_column_index(headers, 'First Name')
    last_name_col = find_column_index(headers, 'Last Name')
    cohort_col = find_column_index(headers, 'Cohort')
    
    for row in intern_data[1:]:
        if len(row) > max(first_name_col, last_name_col):
            first = row[first_name_col] if first_name_col is not None else ''
            last = row[last_name_col] if last_name_col is not None else ''
            
            if 'Juana' in first or 'Tomas' in last:
                cohort = row[cohort_col] if cohort_col is not None and len(row) > cohort_col else 'N/A'
                print(f"  Found: {first} {last}")
                print(f"  Cohort: {cohort}")
                print()
                break
    
    # Find alaMar
    print("SEARCHING FOR ALAMAR DOMINICAN KITCHEN:")
    headers = chef_data[0]
    restaurant_col = find_column_index(headers, 'Restaurant Name')
    chef_col = find_column_index(headers, "Primary Mentor's Full Name (First and Last)")
    cohort_col = find_column_index(headers, 'Cohort')
    
    for row in chef_data[1:]:
        if len(row) > restaurant_col:
            restaurant = row[restaurant_col] if restaurant_col is not None else ''
            
            if 'alamar' in restaurant.lower() or 'dominican' in restaurant.lower():
                chef_name = row[chef_col] if chef_col is not None and len(row) > chef_col else 'N/A'
                cohort = row[cohort_col] if cohort_col is not None and len(row) > cohort_col else 'N/A'
                print(f"  Found: {restaurant}")
                print(f"  Chef: {chef_name}")
                print(f"  Cohort: {cohort}")
                print()
                break
    
    print("=" * 80)

if __name__ == "__main__":
    check_cohorts()
