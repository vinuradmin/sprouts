"""
Test the actual run_matching_algorithm function
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    run_matching_algorithm,
    load_commute_cache
)

def test_algorithm():
    """Test the actual algorithm"""
    
    print("=" * 80)
    print("TESTING ACTUAL MATCHING ALGORITHM")
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
    
    print(f"Running algorithm for {cohort_name}")
    print(f"Interns: {len(filtered_interns)-1}")
    print(f"Chefs: {len(filtered_chefs)-1}")
    print()
    
    # Run algorithm
    results = run_matching_algorithm(filtered_interns, filtered_chefs)
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    # Find Juana's results
    for intern_result in results:
        if 'Juana' in intern_result['intern_name'] or 'Tomas' in intern_result['intern_name']:
            print(f"INTERN: {intern_result['intern_name']}")
            print()
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                matches = intern_result['days'].get(day, [])
                if matches:
                    print(f"{day}:")
                    for match in matches:
                        print(f"  - {match['restaurant']} ({match['commute']})")
                        print(f"    Time: {match['time_slots']}")
                    print()
            
            # Check if alaMar is in any day
            has_alamar = False
            for day, matches in intern_result['days'].items():
                for match in matches:
                    if 'alamar' in match['restaurant'].lower():
                        has_alamar = True
                        break
            
            print("=" * 80)
            if has_alamar:
                print("RESULT: alaMar IS in Juana's matches!")
            else:
                print("RESULT: alaMar is NOT in Juana's matches - BUG CONFIRMED")
            print("=" * 80)
            break
    
    print()

if __name__ == "__main__":
    test_algorithm()
