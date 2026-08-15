"""
Complete analysis of Juana and alaMar matching issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    find_column_index
)

def analyze_complete():
    """Complete analysis"""
    
    print("=" * 80)
    print("COMPLETE ANALYSIS: JUANA + ALAMAR")
    print("=" * 80)
    print()
    
    # Read intern data
    intern_data = read_sheet_data('Intern Availabilities')
    headers = intern_data[0]
    
    first_name_col = find_column_index(headers, 'First Name')
    last_name_col = find_column_index(headers, 'Last Name')
    season_year_col = find_column_index(headers, 'Season/Year')
    
    print("1. SEARCHING FOR JUANA TOMAS:")
    juana_row = None
    for row in intern_data[1:]:
        if len(row) > max(first_name_col, last_name_col):
            first = row[first_name_col] if first_name_col is not None else ''
            last = row[last_name_col] if last_name_col is not None else ''
            
            if 'Juana' in first or 'Tomas' in last:
                juana_row = row
                season_year = row[season_year_col] if season_year_col is not None and len(row) > season_year_col else 'N/A'
                print(f"   Found: {first} {last}")
                print(f"   Season/Year: '{season_year}'")
                print()
                break
    
    if not juana_row:
        print("   ERROR: Juana not found!")
        return
    
    # Read chef data
    chef_data = read_sheet_data('Chef Availabilities')
    headers = chef_data[0]
    
    print("2. CHECKING CHEF SHEET STRUCTURE:")
    print(f"   Total columns: {len(headers)}")
    print(f"   First 10 headers: {headers[:10]}")
    print()
    
    # Look for cohort-related columns
    cohort_cols = []
    for i, header in enumerate(headers):
        if 'cohort' in header.lower() or 'season' in header.lower() or 'year' in header.lower():
            cohort_cols.append((i, header))
    
    if cohort_cols:
        print(f"   Found {len(cohort_cols)} cohort-related columns:")
        for i, header in cohort_cols:
            print(f"     Column {i}: {header}")
    else:
        print("   No cohort-related columns found")
    print()
    
    # Find alaMar
    restaurant_col = find_column_index(headers, 'Restaurant Name')
    chef_col = find_column_index(headers, "Primary Mentor's Full Name (First and Last)")
    
    print("3. SEARCHING FOR ALAMAR DOMINICAN KITCHEN:")
    alamar_row = None
    for row in chef_data[1:]:
        if restaurant_col is not None and len(row) > restaurant_col:
            restaurant = row[restaurant_col]
            
            if 'alamar' in restaurant.lower() or 'dominican' in restaurant.lower():
                alamar_row = row
                chef_name = row[chef_col] if chef_col is not None and len(row) > chef_col else 'N/A'
                print(f"   Found: {restaurant}")
                print(f"   Chef: {chef_name}")
                
                # Print all cohort-related values
                if cohort_cols:
                    for i, header in cohort_cols:
                        value = row[i] if len(row) > i else 'N/A'
                        print(f"   {header}: '{value}'")
                print()
                break
    
    if not alamar_row:
        print("   ERROR: alaMar not found!")
        print()
        print("   Listing all Oakland restaurants:")
        location_col = find_column_index(headers, 'Restaurant Location')
        for row in chef_data[1:]:
            if location_col is not None and len(row) > location_col:
                location = row[location_col]
                if 'Oakland' in location:
                    restaurant = row[restaurant_col] if restaurant_col is not None and len(row) > restaurant_col else 'N/A'
                    print(f"     - {restaurant}")
        return
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("Both Juana and alaMar found in the sheets.")
    print("Next step: Check if they're in the same cohort and why matching fails.")
    print()

if __name__ == "__main__":
    analyze_complete()
