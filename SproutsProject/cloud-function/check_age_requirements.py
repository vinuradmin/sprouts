"""
Check age requirements for Oakland restaurants
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

def check_age_requirements():
    """Check which Oakland restaurants require 18+"""
    
    print("=" * 80)
    print("OAKLAND RESTAURANTS - AGE REQUIREMENTS")
    print("=" * 80)
    print()
    
    # Read data
    chef_data = read_sheet_data('Chef Availabilities')
    cohort_name = "Summer 2026"
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Create Chef objects
    chefs = []
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs.append(chef)
        except Exception as e:
            pass
    
    # Filter Oakland restaurants
    oakland_restaurants = [c for c in chefs if 'Oakland' in c.restaurantLocation]
    
    print(f"Total Oakland restaurants: {len(oakland_restaurants)}\n")
    
    requires_18 = []
    no_requirement = []
    
    for chef in oakland_restaurants:
        if chef.chefOver18Only:
            requires_18.append(chef)
        else:
            no_requirement.append(chef)
    
    print(f"REQUIRES 18+ ({len(requires_18)}):")
    print("-" * 80)
    for chef in requires_18:
        print(f"  - {chef.restaurantName} ({chef.chefFullName})")
    
    print()
    print(f"\nNO AGE REQUIREMENT ({len(no_requirement)}):")
    print("-" * 80)
    for chef in no_requirement:
        print(f"  - {chef.restaurantName} ({chef.chefFullName})")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {len(requires_18)} require 18+, {len(no_requirement)} have no age requirement")
    print("=" * 80)

if __name__ == "__main__":
    check_age_requirements()
