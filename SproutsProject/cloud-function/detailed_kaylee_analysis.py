"""
Detailed analysis of Kaylee's matches with Oakland restaurants
Shows exact overlap times and commute calculations
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
    save_commute_cache
)

def analyze_kaylee_oakland():
    """Detailed analysis of Kaylee's Oakland restaurant matches"""
    
    print("=" * 80)
    print("DETAILED ANALYSIS: KAYLEE + OAKLAND RESTAURANTS")
    print("=" * 80)
    print()
    
    # Load cache
    load_commute_cache()
    
    # Read data
    intern_data = read_sheet_data('Intern Availabilities')
    chef_data = read_sheet_data('Chef Availabilities')
    
    # Filter by cohort
    cohort_name = "Summer 2026"
    filtered_interns = filter_by_cohort(intern_data, cohort_name)
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    # Convert to dictionaries
    intern_dicts = rows_to_dict_list(filtered_interns)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Create objects
    interns = {}
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except:
            pass
    
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.chefFullName] = chef
        except:
            pass
    
    # Find Kaylee
    kaylee = None
    for name, intern in interns.items():
        if 'Kaylee' in name or 'Calmo' in name:
            kaylee = intern
            break
    
    if not kaylee:
        print("ERROR: Could not find Kaylee")
        return
    
    print(f"INTERN: {kaylee.internFullName}")
    print(f"Address: {kaylee.getFullAddress()}")
    print(f"Transportation: {kaylee.internTransportation}")
    print(f"Over 18: {kaylee.internOver18}")
    print()
    
    print("AVAILABILITY:")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        slots = kaylee.availability[day]
        if slots:
            print(f"  {day}: {slots}")
        else:
            print(f"  {day}: No availability")
    print()
    
    # Get Oakland restaurants (no age requirement)
    oakland_restaurants = []
    for chef_name, chef in chefs.items():
        if 'Oakland' in chef.restaurantLocation and not chef.chefOver18Only:
            oakland_restaurants.append(chef)
    
    print("=" * 80)
    print(f"OAKLAND RESTAURANTS (NO AGE REQUIREMENT): {len(oakland_restaurants)}")
    print("=" * 80)
    print()
    
    total_matches = 0
    
    for chef in oakland_restaurants:
        print("-" * 80)
        print(f"RESTAURANT: {chef.restaurantName}")
        print(f"Chef: {chef.chefFullName}")
        print(f"Address: {chef.getFullAddress()}")
        print()
        
        # Calculate commute once
        try:
            commute = Commute.getCommuteTime(kaylee.internTransportation, kaylee.getFullAddress(), chef.getFullAddress())
            print(f"COMMUTE: {commute.text} ({commute.value} seconds = {commute.value/60:.1f} minutes)")
            
            if commute.value > 3000:
                print(f"[X] FILTERED: Commute exceeds 50 minute limit")
                print()
                continue
            else:
                print(f"[OK] Commute within limit")
        except Exception as e:
            print(f"ERROR calculating commute: {e}")
            print()
            continue
        
        print()
        print("SCHEDULE ANALYSIS:")
        
        restaurant_has_matches = False
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            kaylee_slots = kaylee.availability[day]
            chef_slots = chef.availability[day]
            
            if not kaylee_slots or not chef_slots:
                continue
            
            print(f"\n  {day}:")
            print(f"    Kaylee:     {kaylee_slots}")
            print(f"    Restaurant: {chef_slots}")
            
            # Check overlaps
            found_overlap = False
            for chef_slot in chef_slots:
                for intern_slot in kaylee_slots:
                    overlap = chef_slot.getOverlap(intern_slot)
                    if overlap.duration() >= 4:
                        found_overlap = True
                        restaurant_has_matches = True
                        total_matches += 1
                        print(f"    [MATCH!] Overlap: {overlap} ({overlap.duration()} hours)")
            
            if not found_overlap and kaylee_slots and chef_slots:
                # Calculate actual overlap even if < 4 hours
                max_overlap = 0
                for chef_slot in chef_slots:
                    for intern_slot in kaylee_slots:
                        overlap = chef_slot.getOverlap(intern_slot)
                        if overlap.duration() > max_overlap:
                            max_overlap = overlap.duration()
                
                if max_overlap > 0:
                    print(f"    [X] Overlap too short: {max_overlap} hours (need 4+)")
                else:
                    print(f"    [X] No time overlap")
        
        if restaurant_has_matches:
            print(f"\n  [RESULT] This restaurant SHOULD appear in Kaylee's matches")
        else:
            print(f"\n  [RESULT] No valid matches (need 4+ hour overlap)")
        
        print()
    
    print("=" * 80)
    print(f"SUMMARY: Found {total_matches} valid day matches across Oakland restaurants")
    print("=" * 80)
    
    # Save cache
    save_commute_cache()

if __name__ == "__main__":
    analyze_kaylee_oakland()
