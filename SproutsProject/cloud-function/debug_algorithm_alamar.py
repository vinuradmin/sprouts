"""
Debug why alaMar is being filtered out in the algorithm
"""

import sys
import os
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

def debug_algorithm():
    """Debug the algorithm for Juana + alaMar on Tuesday"""
    
    print("=" * 80)
    print("DEBUGGING ALGORITHM: JUANA + ALAMAR ON TUESDAY")
    print("=" * 80)
    print()
    
    # Load cache
    load_commute_cache()
    
    # Read and filter data
    intern_data = read_sheet_data('Intern Availabilities')
    chef_data = read_sheet_data('Chef Availabilities')
    
    cohort_name = "Summer 2026"
    filtered_interns = filter_by_cohort(intern_data, cohort_name)
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    # Convert to dicts and create objects
    intern_dicts = rows_to_dict_list(filtered_interns)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Find Juana
    juana = None
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            if 'Juana' in intern.internFullName:
                juana = intern
                break
        except:
            pass
    
    # Create all chefs
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.chefFullName] = chef
        except Exception as e:
            pass
    
    if not juana:
        print("ERROR: Juana not found")
        return
    
    print(f"Testing: {juana.internFullName}")
    print(f"Day: Tuesday")
    print(f"Juana's Tuesday availability: {juana.availability['Tuesday']}")
    print()
    
    # Check if alaMar is in chefs dict
    alamar_in_dict = False
    for chef_name in chefs:
        if 'alamar' in chefs[chef_name].restaurantName.lower():
            alamar_in_dict = True
            print(f"alaMar found in chefs dict: {chefs[chef_name].restaurantName} (Chef: {chef_name})")
            print(f"Tuesday availability: {chefs[chef_name].availability['Tuesday']}")
            print()
            break
    
    if not alamar_in_dict:
        print("ERROR: alaMar NOT in chefs dictionary!")
        print(f"Total chefs in dict: {len(chefs)}")
        print("First 10 chefs:")
        for i, chef_name in enumerate(list(chefs.keys())[:10], 1):
            print(f"  {i}. {chefs[chef_name].restaurantName} ({chef_name})")
        return
    
    # Run the matching function for Tuesday
    print("=" * 80)
    print("RUNNING findInternsToRestaurantOverlap FOR TUESDAY")
    print("=" * 80)
    print()
    
    overlaps = findInternsToRestaurantOverlap(chefs, juana, 'Tuesday', juana.availability['Tuesday'])
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total matches found: {len(overlaps)}")
    print()
    
    # Check if alaMar is in results
    alamar_found = False
    for restaurant in overlaps:
        if 'alamar' in restaurant.lower():
            alamar_found = True
            print(f"[SUCCESS] alaMar found in results: {restaurant}")
            print(f"  Commute: {overlaps[restaurant]['commute'].text}")
            print(f"  Overlaps: {overlaps[restaurant]['Tuesday']}")
            break
    
    if not alamar_found:
        print("[BUG] alaMar NOT in results")
        print()
        print("Restaurants that DID match:")
        for restaurant in list(overlaps.keys())[:5]:
            print(f"  - {restaurant} ({overlaps[restaurant]['commute'].text})")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    debug_algorithm()
