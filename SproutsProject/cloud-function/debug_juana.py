"""
Debug why Juana Tomas isn't matching with alaMar Dominican Kitchen
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

def debug_juana_alamar():
    """Debug Juana's matching with alaMar"""
    
    print("=" * 80)
    print("DEBUGGING: JUANA TOMAS + ALAMAR DOMINICAN KITCHEN")
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
        except Exception as e:
            print(f"Error processing intern: {e}")
    
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.chefFullName] = chef
        except Exception as e:
            print(f"Error processing chef: {e}")
    
    # Find Juana
    juana = None
    for name, intern in interns.items():
        if 'Juana' in name or 'Tomas' in name:
            juana = intern
            print(f"Found intern: {name}")
            break
    
    if not juana:
        print("ERROR: Could not find Juana Tomas")
        return
    
    # Find alaMar
    alamar = None
    for name, chef in chefs.items():
        restaurant_lower = chef.restaurantName.lower()
        if 'alamar' in restaurant_lower or 'dominican' in restaurant_lower:
            alamar = chef
            print(f"Found restaurant: {chef.restaurantName} (Chef: {name})")
            break
    
    if not alamar:
        print("ERROR: Could not find alaMar Dominican Kitchen")
        return
    
    print()
    print("=" * 80)
    print("INTERN DETAILS")
    print("=" * 80)
    print(f"Name: {juana.internFullName}")
    print(f"Age: {juana.internAge}")
    print(f"Over 18: {juana.internOver18}")
    print(f"Address: {juana.getFullAddress()}")
    print(f"Transportation: {juana.internTransportation}")
    print()
    print("Availability:")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        slots = juana.availability[day]
        if slots:
            print(f"  {day}: {slots}")
        else:
            print(f"  {day}: No availability")
    
    print()
    print("=" * 80)
    print("RESTAURANT DETAILS")
    print("=" * 80)
    print(f"Name: {alamar.restaurantName}")
    print(f"Chef: {alamar.chefFullName}")
    print(f"Address: {alamar.getFullAddress()}")
    print(f"Location: {alamar.restaurantLocation}")
    print(f"Requires 18+: {alamar.chefOver18Only}")
    print()
    print("Availability:")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        slots = alamar.availability[day]
        if slots:
            print(f"  {day}: {slots}")
        else:
            print(f"  {day}: No availability")
    
    print()
    print("=" * 80)
    print("FILTER CHECKS")
    print("=" * 80)
    print()
    
    # Check 1: Age requirement
    print("1. AGE REQUIREMENT CHECK")
    print(f"   Restaurant requires 18+: {alamar.chefOver18Only}")
    print(f"   Intern is over 18: {juana.internOver18} (Age: {juana.internAge})")
    if alamar.chefOver18Only and not juana.internOver18:
        print("   [X] FILTERED: Age requirement not met")
        print()
        return
    else:
        print("   [OK] Age requirement passed")
    print()
    
    # Check 2: Commute time
    print("2. COMMUTE TIME CHECK")
    try:
        commute = Commute.getCommuteTime(juana.internTransportation, juana.getFullAddress(), alamar.getFullAddress())
        print(f"   Commute: {commute.text} ({commute.value} seconds = {commute.value/60:.1f} minutes)")
        print(f"   Threshold: 120 minutes (7200 seconds)")
        if commute.value > 7200:
            print(f"   [X] FILTERED: Commute exceeds 120 minute limit")
            print()
            return
        else:
            print(f"   [OK] Commute within limit")
    except Exception as e:
        print(f"   [ERROR] Could not calculate commute: {e}")
        print()
        return
    print()
    
    # Check 3: Schedule overlap
    print("3. SCHEDULE OVERLAP CHECK")
    print("   Checking each day for 4+ hour overlaps...")
    print()
    
    has_any_match = False
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        juana_slots = juana.availability[day]
        alamar_slots = alamar.availability[day]
        
        if not juana_slots or not alamar_slots:
            continue
        
        print(f"   {day}:")
        print(f"     Juana:  {juana_slots}")
        print(f"     alaMar: {alamar_slots}")
        
        # Check overlaps
        found_overlap = False
        max_overlap = 0
        for chef_slot in alamar_slots:
            for intern_slot in juana_slots:
                overlap = chef_slot.getOverlap(intern_slot)
                overlap_hours = overlap.duration()
                if overlap_hours > max_overlap:
                    max_overlap = overlap_hours
                if overlap_hours >= 4:
                    found_overlap = True
                    has_any_match = True
                    print(f"     [MATCH!] Overlap: {overlap} ({overlap_hours} hours)")
        
        if not found_overlap and max_overlap > 0:
            print(f"     [X] Overlap too short: {max_overlap} hours (need 4+)")
        elif not found_overlap:
            print(f"     [X] No time overlap")
        
        print()
    
    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    if has_any_match:
        print("[SUCCESS] Juana SHOULD match with alaMar Dominican Kitchen")
        print("If she's not showing up, there may be an issue with the algorithm logic.")
    else:
        print("[NO MATCH] Juana does NOT match with alaMar Dominican Kitchen")
        print("Reason: No days with 4+ hour overlap")
    print("=" * 80)
    
    # Save cache
    save_commute_cache()

if __name__ == "__main__":
    debug_juana_alamar()
