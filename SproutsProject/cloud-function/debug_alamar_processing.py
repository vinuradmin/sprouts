"""
Debug why alaMar fails to process into a Chef object
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    rows_to_dict_list,
    find_column_index,
    Chef
)

def debug_alamar_processing():
    """Debug alaMar processing"""
    
    print("=" * 80)
    print("DEBUGGING ALAMAR PROCESSING")
    print("=" * 80)
    print()
    
    # Read and filter data
    chef_data = read_sheet_data('Chef Availabilities')
    cohort_name = "Summer 2026"
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    print(f"Filtered chefs: {len(filtered_chefs)} rows (including header)")
    print()
    
    # Find alaMar row
    headers = filtered_chefs[0]
    restaurant_col = find_column_index(headers, 'Restaurant Name')
    
    alamar_row = None
    alamar_index = None
    for i, row in enumerate(filtered_chefs[1:], 1):
        if len(row) > restaurant_col:
            restaurant = row[restaurant_col]
            if 'alamar' in restaurant.lower():
                alamar_row = row
                alamar_index = i
                print(f"Found alaMar at index {i}: {restaurant}")
                break
    
    if not alamar_row:
        print("ERROR: alaMar not found in filtered data")
        return
    
    print()
    print("alaMar Row Data:")
    print(f"  Total columns: {len(alamar_row)}")
    for i, (header, value) in enumerate(zip(headers, alamar_row)):
        if value:  # Only print non-empty values
            print(f"  [{i}] {header}: '{value}'")
    print()
    
    # Convert to dict
    print("Converting to dictionary...")
    chef_dicts = rows_to_dict_list(filtered_chefs)
    alamar_dict = chef_dicts[alamar_index - 1]  # -1 because chef_dicts doesn't include header
    
    print("alaMar Dictionary:")
    for key, value in alamar_dict.items():
        if value:
            print(f"  {key}: '{value}'")
    print()
    
    # Try to create Chef object
    print("Attempting to create Chef object...")
    try:
        chef = Chef(alamar_dict)
        print("SUCCESS! Chef object created:")
        print(f"  Restaurant: {chef.restaurantName}")
        print(f"  Chef: {chef.chefFullName}")
        print(f"  Location: {chef.restaurantLocation}")
        print(f"  Over 18 Only: {chef.chefOver18Only}")
        print(f"  Availability: {chef.availability}")
    except Exception as e:
        print(f"ERROR creating Chef object: {e}")
        print()
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    debug_alamar_processing()
