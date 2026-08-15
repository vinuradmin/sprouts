"""
Oakland-specific analysis:
1. How many of the 7 threshold gains (120->180min) are Oakland restaurants
2. How many age-filtered matches involve Oakland restaurants
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
    load_commute_cache
)

def oakland_analysis():
    """Analyze Oakland-specific impacts"""
    
    print("=" * 80)
    print("OAKLAND-SPECIFIC ANALYSIS")
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
    
    # Create interns and chefs
    interns = {}
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except:
            pass
    
    chefs = {}
    oakland_chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.restaurantName] = chef
            if 'Oakland' in chef.restaurantLocation:
                oakland_chefs[chef.restaurantName] = chef
        except:
            pass
    
    print(f"Total restaurants: {len(chefs)}")
    print(f"Oakland restaurants: {len(oakland_chefs)}")
    print()
    print("Oakland restaurants:")
    for name in oakland_chefs.keys():
        print(f"  - {name}")
    print()
    
    # Question 1: How many of the 7 threshold gains are Oakland restaurants?
    print("=" * 80)
    print("QUESTION 1: THRESHOLD GAINS (120min -> 180min)")
    print("=" * 80)
    print()
    
    matches_120_all = []
    matches_180_all = []
    matches_120_oakland = []
    matches_180_oakland = []
    
    for intern_name, intern in interns.items():
        for rest_name, chef in chefs.items():
            is_oakland = rest_name in oakland_chefs
            
            # Check age
            if chef.chefOver18Only and not intern.internOver18:
                continue
            
            # Check schedule overlap
            has_overlap = False
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern.availability[day]
                chef_slots = chef.availability[day]
                
                if not intern_slots or not chef_slots:
                    continue
                
                for chef_slot in chef_slots:
                    for intern_slot in intern_slots:
                        overlap = chef_slot.getOverlap(intern_slot)
                        if overlap.duration() >= 4:
                            has_overlap = True
                            break
                    if has_overlap:
                        break
                if has_overlap:
                    break
            
            if not has_overlap:
                continue
            
            # Check commute at 120 minutes
            try:
                commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                
                if commute.value <= 7200:  # 120 minutes
                    matches_120_all.append((intern_name, rest_name, commute.value))
                    if is_oakland:
                        matches_120_oakland.append((intern_name, rest_name, commute.value))
                
                if commute.value <= 10800:  # 180 minutes
                    matches_180_all.append((intern_name, rest_name, commute.value))
                    if is_oakland:
                        matches_180_oakland.append((intern_name, rest_name, commute.value))
            except:
                continue
    
    # Calculate gains
    gain_all = len(matches_180_all) - len(matches_120_all)
    gain_oakland = len(matches_180_oakland) - len(matches_120_oakland)
    
    print(f"Matches at 120min threshold: {len(matches_120_all)}")
    print(f"  Oakland: {len(matches_120_oakland)}")
    print()
    print(f"Matches at 180min threshold: {len(matches_180_all)}")
    print(f"  Oakland: {len(matches_180_oakland)}")
    print()
    print(f"GAIN from 120->180min: +{gain_all} total matches")
    print(f"  Oakland gain: +{gain_oakland} matches")
    print(f"  Non-Oakland gain: +{gain_all - gain_oakland} matches")
    print()
    
    if gain_oakland > 0:
        print(f"Oakland represents {(gain_oakland/gain_all*100):.1f}% of the threshold gains")
        print()
        print("New Oakland matches from threshold increase:")
        
        # Find which matches are new
        matches_120_set = set((i, r) for i, r, c in matches_120_all)
        for intern_name, rest_name, commute_val in matches_180_all:
            if (intern_name, rest_name) not in matches_120_set and rest_name in oakland_chefs:
                print(f"  - {intern_name} -> {rest_name} ({commute_val/60:.0f} min)")
    
    print()
    
    # Question 2: Age restriction filtering for Oakland
    print("=" * 80)
    print("QUESTION 2: AGE RESTRICTION FILTERING (OAKLAND)")
    print("=" * 80)
    print()
    
    age_filtered_all = 0
    age_filtered_oakland = 0
    age_filtered_details = []
    
    for intern_name, intern in interns.items():
        for rest_name, chef in chefs.items():
            is_oakland = rest_name in oakland_chefs
            
            # Check if filtered by age
            if chef.chefOver18Only and not intern.internOver18:
                age_filtered_all += 1
                if is_oakland:
                    age_filtered_oakland += 1
                    age_filtered_details.append((intern_name, rest_name))
    
    print(f"Total combinations filtered by age: {age_filtered_all}")
    print(f"  Oakland combinations filtered: {age_filtered_oakland}")
    print(f"  Non-Oakland combinations filtered: {age_filtered_all - age_filtered_oakland}")
    print()
    
    if age_filtered_oakland > 0:
        print(f"Oakland represents {(age_filtered_oakland/age_filtered_all*100):.1f}% of age-filtered combinations")
        print()
        
        # Show which Oakland restaurants require 18+
        oakland_18plus = [name for name, chef in oakland_chefs.items() if chef.chefOver18Only]
        print(f"Oakland restaurants requiring 18+: {len(oakland_18plus)}/{len(oakland_chefs)}")
        for rest_name in oakland_18plus:
            print(f"  - {rest_name}")
        print()
        
        # Show under-18 interns
        under_18_interns = [name for name, intern in interns.items() if not intern.internOver18]
        print(f"Interns under 18: {len(under_18_interns)}/{len(interns)}")
        print()
        
        print(f"Potential Oakland matches lost to age restrictions: {age_filtered_oakland}")
        print(f"  ({len(oakland_18plus)} Oakland restaurants × {len(under_18_interns)} under-18 interns)")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"1. Threshold increase (120->180min):")
    print(f"   - Total gain: +{gain_all} matches")
    print(f"   - Oakland gain: +{gain_oakland} matches ({(gain_oakland/gain_all*100) if gain_all > 0 else 0:.1f}%)")
    print()
    print(f"2. Age restriction filtering:")
    print(f"   - Total filtered: {age_filtered_all} combinations")
    print(f"   - Oakland filtered: {age_filtered_oakland} combinations ({(age_filtered_oakland/age_filtered_all*100):.1f}%)")
    print()
    print("=" * 80)

if __name__ == "__main__":
    oakland_analysis()
