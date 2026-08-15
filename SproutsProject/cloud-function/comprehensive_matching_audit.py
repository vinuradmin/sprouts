"""
Comprehensive audit of matching algorithm to find other potential bugs
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
from collections import defaultdict

def audit_matching():
    """Comprehensive audit of matching logic"""
    
    print("=" * 80)
    print("COMPREHENSIVE MATCHING AUDIT - SUMMER 2026")
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
    
    # Create interns
    interns = {}
    intern_errors = []
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except Exception as e:
            intern_errors.append(str(e))
    
    # Create chefs (using RESTAURANT NAME as key - the fix)
    chefs = {}
    chef_errors = []
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.restaurantName] = chef
        except Exception as e:
            chef_errors.append(str(e))
    
    print(f"Loaded {len(interns)} interns ({len(intern_errors)} errors)")
    print(f"Loaded {len(chefs)} restaurants ({len(chef_errors)} errors)")
    print()
    
    # Get Oakland restaurants
    oakland_restaurants = [name for name, chef in chefs.items() if 'Oakland' in chef.restaurantLocation]
    print(f"Oakland restaurants: {len(oakland_restaurants)}")
    for rest in oakland_restaurants:
        print(f"  - {rest}")
    print()
    
    # Sample 5 diverse interns for testing
    sample_interns = []
    for i, (name, intern) in enumerate(interns.items()):
        if i >= 5:
            break
        sample_interns.append((name, intern))
    
    print("=" * 80)
    print("TESTING SAMPLE INTERNS")
    print("=" * 80)
    print()
    
    issues_found = []
    
    for intern_name, intern in sample_interns:
        print(f"\nINTERN: {intern_name}")
        print(f"  Age: {intern.internAge}, Over 18: {intern.internOver18}")
        print(f"  Location: {intern.internCity}, {intern.internZip}")
        print(f"  Transportation: {intern.internTransportation}")
        
        # Count potential matches
        total_restaurants = len(chefs)
        age_filtered = 0
        commute_filtered = 0
        schedule_filtered = 0
        valid_matches = 0
        
        for rest_name, chef in chefs.items():
            # Check age
            if chef.chefOver18Only and not intern.internOver18:
                age_filtered += 1
                continue
            
            # Check schedule overlap (any day with 4+ hours)
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
                schedule_filtered += 1
                continue
            
            # Check commute (only if we have overlap)
            try:
                commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                if commute.value > 7200:  # 120 minutes
                    commute_filtered += 1
                    continue
            except Exception as e:
                commute_filtered += 1
                continue
            
            valid_matches += 1
        
        print(f"\n  FILTER BREAKDOWN:")
        print(f"    Total restaurants: {total_restaurants}")
        print(f"    Filtered by age: {age_filtered}")
        print(f"    Filtered by schedule: {schedule_filtered}")
        print(f"    Filtered by commute: {commute_filtered}")
        print(f"    VALID MATCHES: {valid_matches}")
        
        match_percentage = (valid_matches / total_restaurants) * 100
        print(f"    Match rate: {match_percentage:.1f}%")
        
        # Flag potential issues
        if valid_matches == 0:
            issues_found.append(f"{intern_name}: NO MATCHES (potential issue)")
        elif match_percentage < 10:
            issues_found.append(f"{intern_name}: Very low match rate ({match_percentage:.1f}%)")
        
        # Check Oakland specifically
        oakland_matches = 0
        oakland_age_filtered = 0
        oakland_commute_filtered = 0
        oakland_schedule_filtered = 0
        
        for rest_name in oakland_restaurants:
            chef = chefs[rest_name]
            
            # Age check
            if chef.chefOver18Only and not intern.internOver18:
                oakland_age_filtered += 1
                continue
            
            # Schedule check
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
                oakland_schedule_filtered += 1
                continue
            
            # Commute check
            try:
                commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                if commute.value > 7200:
                    oakland_commute_filtered += 1
                    continue
            except:
                oakland_commute_filtered += 1
                continue
            
            oakland_matches += 1
        
        print(f"\n  OAKLAND RESTAURANTS:")
        print(f"    Total Oakland restaurants: {len(oakland_restaurants)}")
        print(f"    Filtered by age: {oakland_age_filtered}")
        print(f"    Filtered by schedule: {oakland_schedule_filtered}")
        print(f"    Filtered by commute: {oakland_commute_filtered}")
        print(f"    Oakland matches: {oakland_matches}")
        
        if oakland_matches == 0 and len(oakland_restaurants) > 0:
            issues_found.append(f"{intern_name}: NO Oakland matches despite {len(oakland_restaurants)} Oakland restaurants")
    
    print()
    print("=" * 80)
    print("SUMMARY OF ISSUES FOUND")
    print("=" * 80)
    if issues_found:
        for issue in issues_found:
            print(f"  - {issue}")
    else:
        print("  No major issues detected in sample testing")
    
    print()
    print("=" * 80)
    print("POTENTIAL BUG ANALYSIS")
    print("=" * 80)
    print()
    
    # Check for other systematic issues
    print("1. CHECKING FOR DUPLICATE RESTAURANT NAMES:")
    restaurant_names = list(chefs.keys())
    if len(restaurant_names) != len(set(restaurant_names)):
        print("   [WARNING] Duplicate restaurant names found!")
        name_counts = defaultdict(int)
        for name in restaurant_names:
            name_counts[name] += 1
        for name, count in name_counts.items():
            if count > 1:
                print(f"     - '{name}' appears {count} times")
    else:
        print("   [OK] No duplicate restaurant names")
    print()
    
    print("2. CHECKING AGE REQUIREMENT DISTRIBUTION:")
    age_required = sum(1 for chef in chefs.values() if chef.chefOver18Only)
    print(f"   Restaurants requiring 18+: {age_required}/{len(chefs)} ({(age_required/len(chefs)*100):.1f}%)")
    
    under_18_interns = sum(1 for intern in interns.values() if not intern.internOver18)
    print(f"   Interns under 18: {under_18_interns}/{len(interns)} ({(under_18_interns/len(interns)*100):.1f}%)")
    
    if age_required > len(chefs) * 0.5 and under_18_interns > 0:
        print("   [WARNING] Many restaurants require 18+, which may limit matches for younger interns")
    else:
        print("   [OK] Age requirements seem reasonable")
    print()
    
    print("3. CHECKING SCHEDULE AVAILABILITY:")
    no_availability = sum(1 for chef in chefs.values() 
                         if all(len(chef.availability[day]) == 0 for day in chef.availability))
    if no_availability > 0:
        print(f"   [WARNING] {no_availability} restaurants have NO availability on any day")
    else:
        print("   [OK] All restaurants have some availability")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    audit_matching()
