"""
Final comprehensive test of Juana + alaMar matching
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

def final_test():
    """Final comprehensive test"""
    
    print("=" * 80)
    print("FINAL TEST: JUANA TOMAS + ALAMAR DOMINICAN KITCHEN")
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
    
    # Convert to dicts
    intern_dicts = rows_to_dict_list(filtered_interns)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Find and create Juana
    juana = None
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            if 'Juana' in intern.internFullName or 'Tomas' in intern.internFullName:
                juana = intern
                break
        except Exception as e:
            pass
    
    # Find and create alaMar
    alamar = None
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            if 'alamar' in chef.restaurantName.lower():
                alamar = chef
                break
        except Exception as e:
            pass
    
    if not juana:
        print("ERROR: Juana not found or failed to process")
        return
    
    if not alamar:
        print("ERROR: alaMar not found or failed to process")
        return
    
    print("[OK] Both found and processed successfully")
    print()
    
    # Display profiles
    print("=" * 80)
    print("JUANA TOMAS PROFILE")
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
        print(f"  {day}: {slots if slots else 'No availability'}")
    print()
    
    print("=" * 80)
    print("ALAMAR DOMINICAN KITCHEN PROFILE")
    print("=" * 80)
    print(f"Restaurant: {alamar.restaurantName}")
    print(f"Chef: {alamar.chefFullName}")
    print(f"Address: {alamar.getFullAddress()}")
    print(f"Location: {alamar.restaurantLocation}")
    print(f"Requires 18+: {alamar.chefOver18Only}")
    print()
    print("Availability:")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        slots = alamar.availability[day]
        print(f"  {day}: {slots if slots else 'No availability'}")
    print()
    
    # Run filter checks
    print("=" * 80)
    print("FILTER CHECKS")
    print("=" * 80)
    print()
    
    # Check 1: Age
    print("1. AGE REQUIREMENT")
    print(f"   Restaurant requires 18+: {alamar.chefOver18Only}")
    print(f"   Juana is over 18: {juana.internOver18}")
    if alamar.chefOver18Only and not juana.internOver18:
        print("   [BLOCKED] Age requirement not met")
        return
    else:
        print("   [PASS] Age requirement met")
    print()
    
    # Check 2: Commute
    print("2. COMMUTE TIME")
    try:
        commute = Commute.getCommuteTime(juana.internTransportation, juana.getFullAddress(), alamar.getFullAddress())
        print(f"   From: {juana.getFullAddress()}")
        print(f"   To: {alamar.getFullAddress()}")
        print(f"   Commute: {commute.text} ({commute.value} seconds = {commute.value/60:.1f} minutes)")
        print(f"   Threshold: 120 minutes (7200 seconds)")
        if commute.value > 7200:
            print(f"   [BLOCKED] Commute exceeds threshold")
            return
        else:
            print(f"   [PASS] Commute within threshold")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return
    print()
    
    # Check 3: Schedule overlap
    print("3. SCHEDULE OVERLAP (need 4+ hours)")
    has_match = False
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        juana_slots = juana.availability[day]
        alamar_slots = alamar.availability[day]
        
        if not juana_slots or not alamar_slots:
            continue
        
        print(f"   {day}:")
        print(f"     Juana:  {juana_slots}")
        print(f"     alaMar: {alamar_slots}")
        
        for chef_slot in alamar_slots:
            for intern_slot in juana_slots:
                overlap = chef_slot.getOverlap(intern_slot)
                hours = overlap.duration()
                if hours >= 4:
                    has_match = True
                    print(f"     [MATCH] {overlap} ({hours} hours)")
                elif hours > 0:
                    print(f"     [SHORT] {overlap} ({hours} hours - need 4+)")
        print()
    
    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    if has_match:
        print("[SUCCESS] Juana SHOULD match with alaMar Dominican Kitchen!")
        print("If not appearing in results, there's a bug in the matching algorithm.")
    else:
        print("[NO MATCH] No days with 4+ hour overlap")
        print("This is the expected behavior based on their schedules.")
    print("=" * 80)
    
    # Save cache
    save_commute_cache()

if __name__ == "__main__":
    final_test()
