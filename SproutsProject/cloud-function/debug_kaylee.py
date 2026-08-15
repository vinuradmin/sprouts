"""
Debug Kaylee Calmo Ahilon's matching results
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    rows_to_dict_list,
    Intern,
    Chef,
    Commute,
    load_commute_cache,
    findInternsToRestaurantOverlap
)

def debug_kaylee():
    """Debug Kaylee's matching"""
    
    print("=" * 80)
    print("DEBUGGING KAYLEE CALMO AHILON'S MATCHES")
    print("=" * 80)
    print()
    
    # Load cache
    load_commute_cache()
    
    # Read data
    print("Reading data from Google Sheets...")
    intern_data = read_sheet_data('Intern Availabilities')
    chef_data = read_sheet_data('Chef Availabilities')
    
    # Filter by cohort
    cohort_name = "Summer 2026"
    filtered_interns = filter_by_cohort(intern_data, cohort_name)
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    # Convert to dictionaries
    intern_dicts = rows_to_dict_list(filtered_interns)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Create Intern and Chef objects
    interns = {}
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except Exception as e:
            print(f"Error processing intern: {e}")
    
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.chefFullName] = chef
        except Exception as e:
            print(f"Error processing chef: {e}")
    
    # Find Kaylee
    kaylee = None
    for name, intern in interns.items():
        if 'Kaylee' in name or 'Calmo' in name:
            kaylee = intern
            break
    
    if not kaylee:
        print("ERROR: Could not find Kaylee Calmo Ahilon")
        return
    
    print(f"Found intern: {kaylee.internFullName}")
    print(f"Address: {kaylee.getFullAddress()}")
    print(f"Transportation: {kaylee.internTransportation}")
    print(f"Over 18: {kaylee.internOver18}")
    print()
    
    print("Availability:")
    for day, slots in kaylee.availability.items():
        print(f"  {day}: {slots}")
    print()
    
    # Get Oakland restaurants
    oakland_restaurants = []
    for chef_name, chef in chefs.items():
        if 'Oakland' in chef.restaurantLocation:
            oakland_restaurants.append(chef)
    
    print(f"Found {len(oakland_restaurants)} Oakland restaurants:")
    for chef in oakland_restaurants:
        print(f"  - {chef.restaurantName} ({chef.chefFullName})")
    print()
    
    # Test matching for each day
    print("=" * 80)
    print("DETAILED MATCHING ANALYSIS")
    print("=" * 80)
    print()
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        print(f"\n{day.upper()}")
        print("-" * 80)
        
        kaylee_slots = kaylee.availability[day]
        print(f"Kaylee's availability: {kaylee_slots}")
        
        if not kaylee_slots:
            print("  No availability")
            continue
        
        print()
        
        # Check each Oakland restaurant
        for chef in oakland_restaurants:
            chef_slots = chef.availability[day]
            
            if not chef_slots:
                continue
            
            print(f"\n  {chef.restaurantName}:")
            print(f"    Chef availability: {chef_slots}")
            
            # Check age requirement
            if chef.chefOver18Only and not kaylee.internOver18:
                print(f"    [X] FILTERED: Age requirement (chef requires 18+, Kaylee is {kaylee.internAge})")
                continue
            
            # Check for overlaps
            has_overlap = False
            for chef_slot in chef_slots:
                for intern_slot in kaylee_slots:
                    overlap = chef_slot.getOverlap(intern_slot)
                    if overlap.duration() >= 4:
                        has_overlap = True
                        print(f"    [OK] Overlap found: {overlap} ({overlap.duration()} hours)")
                        
                        # Check commute
                        com_key = kaylee.getFullAddress() + "|" + chef.getFullAddress()
                        try:
                            commute = Commute.getCommuteTime(kaylee.internTransportation, kaylee.getFullAddress(), chef.getFullAddress())
                            print(f"    Commute: {commute.text} ({commute.value} seconds)")
                            
                            if commute.value > 3000:
                                print(f"    [X] FILTERED: Commute too long (>{3000/60:.0f} min)")
                            else:
                                print(f"    [MATCH!]")
                        except Exception as e:
                            print(f"    Error calculating commute: {e}")
            
            if not has_overlap:
                print(f"    [X] No overlap >= 4 hours")
    
    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    debug_kaylee()
