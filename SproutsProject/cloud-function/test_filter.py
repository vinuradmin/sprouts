"""
Test if filter_by_cohort is working correctly for Chef sheet
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    find_column_index
)

def test_filter():
    """Test the filtering"""
    
    print("=" * 80)
    print("TESTING FILTER_BY_COHORT FOR CHEF SHEET")
    print("=" * 80)
    print()
    
    # Read raw data
    chef_data = read_sheet_data('Chef Availabilities')
    print(f"1. Raw data: {len(chef_data)} rows")
    print(f"   First row: {chef_data[0]}")
    print()
    
    # Filter by Summer 2026
    cohort_name = "Summer 2026"
    filtered = filter_by_cohort(chef_data, cohort_name)
    print(f"2. Filtered data for '{cohort_name}': {len(filtered)} rows")
    
    if filtered:
        print(f"   Headers: {filtered[0][:5]}...")
        print()
        
        # Find restaurant name column
        restaurant_col = find_column_index(filtered[0], 'Restaurant Name')
        season_col = find_column_index(filtered[0], 'Season/Year')
        
        print(f"3. Restaurant Name column: {restaurant_col}")
        print(f"   Season/Year column: {season_col}")
        print()
        
        # List first 10 restaurants
        print("4. First 10 restaurants in Summer 2026:")
        for i, row in enumerate(filtered[1:11], 1):
            if len(row) > restaurant_col:
                restaurant = row[restaurant_col] if restaurant_col is not None else 'N/A'
                season = row[season_col] if season_col is not None and len(row) > season_col else 'N/A'
                print(f"   {i}. {restaurant} (Season/Year: {season})")
        print()
        
        # Search for alaMar
        print("5. Searching for alaMar:")
        found = False
        for i, row in enumerate(filtered[1:], 1):
            if restaurant_col is not None and len(row) > restaurant_col:
                restaurant = row[restaurant_col]
                if 'alamar' in restaurant.lower() or 'dominican' in restaurant.lower():
                    print(f"   FOUND at row {i}: {restaurant}")
                    found = True
                    break
        
        if not found:
            print("   NOT FOUND in filtered Summer 2026 data")
            print()
            print("   Checking all cohorts:")
            # Check what cohort alaMar is in
            for row in chef_data:
                if restaurant_col is not None and len(row) > restaurant_col:
                    restaurant = row[restaurant_col]
                    if 'alamar' in restaurant.lower() or 'dominican' in restaurant.lower():
                        season = row[season_col] if season_col is not None and len(row) > season_col else 'N/A'
                        print(f"   Found alaMar in cohort: '{season}'")
                        break
    else:
        print("   ERROR: No filtered data returned!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    test_filter()
