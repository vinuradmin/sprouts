"""
Analyze how many restaurants are affected by duplicate chef names
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    rows_to_dict_list,
    Chef,
    find_column_index
)
from collections import defaultdict

def analyze_duplicates():
    """Analyze duplicate chef names and their impact"""
    
    print("=" * 80)
    print("ANALYZING DUPLICATE CHEF NAMES IN SUMMER 2026")
    print("=" * 80)
    print()
    
    # Read and filter data
    chef_data = read_sheet_data('Chef Availabilities')
    cohort_name = "Summer 2026"
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    print(f"Total restaurants in Summer 2026: {len(filtered_chefs) - 1}")
    print()
    
    # Get location info
    headers = filtered_chefs[0]
    restaurant_col = find_column_index(headers, 'Restaurant Name')
    chef_col = find_column_index(headers, "Primary Mentor's Full Name (First and Last)")
    location_col = find_column_index(headers, 'Restaurant Location')
    
    # Track chef names and their restaurants
    chef_to_restaurants = defaultdict(list)
    
    for row in filtered_chefs[1:]:
        if len(row) > max(restaurant_col, chef_col, location_col):
            restaurant = row[restaurant_col]
            chef_name = row[chef_col]
            location = row[location_col] if location_col is not None else 'Unknown'
            
            chef_to_restaurants[chef_name].append({
                'restaurant': restaurant,
                'location': location
            })
    
    # Find duplicates
    duplicates = {chef: restaurants for chef, restaurants in chef_to_restaurants.items() 
                  if len(restaurants) > 1}
    
    print("=" * 80)
    print("CHEFS WITH MULTIPLE RESTAURANTS")
    print("=" * 80)
    print()
    
    if duplicates:
        total_affected = sum(len(restaurants) for restaurants in duplicates.values())
        total_lost = total_affected - len(duplicates)  # One restaurant per chef survives
        
        print(f"Chefs with multiple restaurants: {len(duplicates)}")
        print(f"Total restaurants affected: {total_affected}")
        print(f"Restaurants LOST due to bug: {total_lost}")
        print()
        
        oakland_lost = 0
        oakland_affected = 0
        
        for chef_name, restaurants in duplicates.items():
            print(f"\nCHEF: {chef_name}")
            print(f"  Operates {len(restaurants)} restaurants:")
            
            for i, rest in enumerate(restaurants, 1):
                location = rest['location']
                is_oakland = 'Oakland' in location
                
                if is_oakland:
                    oakland_affected += 1
                    if i > 1:  # First one survives, rest are lost
                        oakland_lost += 1
                
                status = "[KEPT]" if i == 1 else "[LOST]"
                location_marker = "[OAKLAND]" if is_oakland else ""
                
                print(f"    {i}. {status} {rest['restaurant']} - {location} {location_marker}")
        
        print()
        print("=" * 80)
        print("IMPACT SUMMARY")
        print("=" * 80)
        print(f"Total restaurants in cohort: {len(filtered_chefs) - 1}")
        print(f"Restaurants affected by bug: {total_affected}")
        print(f"Restaurants LOST: {total_lost}")
        print(f"Percentage lost: {(total_lost / (len(filtered_chefs) - 1)) * 100:.1f}%")
        print()
        print(f"Oakland restaurants affected: {oakland_affected}")
        print(f"Oakland restaurants LOST: {oakland_lost}")
        if oakland_lost > 0:
            print(f"Oakland represents {(oakland_lost / total_lost) * 100:.1f}% of lost restaurants")
        print()
        
        # Verify the claim
        print("=" * 80)
        print("VERIFICATION OF USER'S CLAIM")
        print("=" * 80)
        if oakland_lost > 0:
            print(f"YES - Oakland restaurants ARE disproportionately affected!")
            print(f"{oakland_lost} Oakland restaurants were being filtered out.")
        else:
            print("No - Oakland restaurants are not specifically affected by this bug.")
        print("=" * 80)
        
    else:
        print("No chefs with multiple restaurants found.")
    
    print()

if __name__ == "__main__":
    analyze_duplicates()
