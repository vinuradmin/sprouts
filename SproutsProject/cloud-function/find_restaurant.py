"""
Find alaMar restaurant in the data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    rows_to_dict_list,
    Chef
)

def find_alamar():
    """Find alaMar restaurant"""
    
    # Read data
    chef_data = read_sheet_data('Chef Availabilities')
    cohort_name = "Summer 2026"
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    print("=" * 80)
    print("SEARCHING FOR ALAMAR DOMINICAN KITCHEN")
    print("=" * 80)
    print()
    
    # Create Chef objects and search
    found = []
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            restaurant_name = chef.restaurantName.lower()
            
            # Search for variations
            if 'alamar' in restaurant_name or 'alamar' in restaurant_name or \
               'dominican' in restaurant_name or 'nelson german' in chef.chefFullName.lower():
                found.append(chef)
                print(f"FOUND: {chef.restaurantName}")
                print(f"  Chef: {chef.chefFullName}")
                print(f"  Location: {chef.restaurantLocation}")
                print()
        except Exception as e:
            pass
    
    if not found:
        print("NOT FOUND - Listing all Oakland restaurants:")
        print()
        for row_dict in chef_dicts:
            try:
                chef = Chef(row_dict)
                if 'Oakland' in chef.restaurantLocation:
                    print(f"  - {chef.restaurantName} ({chef.chefFullName})")
            except:
                pass
    
    return found

if __name__ == "__main__":
    find_alamar()
