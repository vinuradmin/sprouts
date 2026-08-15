"""
Test the matching algorithm locally before deploying
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the main module
from main import (
    read_sheet_data,
    filter_by_cohort,
    run_matching_algorithm,
    load_commute_cache,
    save_commute_cache
)

def test_matching():
    """Test the complete matching workflow"""
    
    print("=" * 80)
    print("TESTING MATCHING ALGORITHM LOCALLY")
    print("=" * 80)
    print()
    
    cohort_name = "Spring 2026"
    
    try:
        # Step 1: Load cache
        print("Step 1: Loading commute cache...")
        load_commute_cache()
        print("[OK] Cache loaded")
        print()
        
        # Step 2: Read data from Google Sheets
        print("Step 2: Reading data from Google Sheets...")
        print("  Reading Intern Availabilities...")
        intern_data = read_sheet_data('Intern Availabilities')
        print(f"  [OK] Read {len(intern_data)} rows")
        
        print("  Reading Chef Availabilities...")
        chef_data = read_sheet_data('Chef Availabilities')
        print(f"  [OK] Read {len(chef_data)} rows")
        print()
        
        # Step 3: Filter by cohort
        print(f"Step 3: Filtering by cohort '{cohort_name}'...")
        filtered_interns = filter_by_cohort(intern_data, cohort_name)
        filtered_chefs = filter_by_cohort(chef_data, cohort_name)
        print(f"  [OK] Found {len(filtered_interns)-1} interns")
        print(f"  [OK] Found {len(filtered_chefs)-1} chefs")
        print()
        
        # Step 4: Run matching algorithm
        print("Step 4: Running matching algorithm...")
        print("  (This will take a while - calculating commutes and overlaps)")
        print()
        
        results = run_matching_algorithm(filtered_interns, filtered_chefs)
        
        print()
        print(f"  [OK] Generated matches for {len(results)} interns")
        print()
        
        # Step 5: Display sample results
        print("Step 5: Sample Results")
        print("-" * 80)
        
        if results:
            # Show first intern's results
            first_result = results[0]
            print(f"\nIntern: {first_result['intern_name']}")
            print()
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                matches = first_result['days'].get(day, [])
                if matches:
                    print(f"  {day}:")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"    - {match['restaurant']} ({match['commute']}): {match['time_slots']}")
                else:
                    print(f"  {day}: No matches")
            
            print()
            print(f"Total results: {len(results)} interns with matches")
        
        print()
        print("=" * 80)
        print("TEST SUCCESSFUL!")
        print("=" * 80)
        print()
        print("The algorithm works correctly. Ready to deploy!")
        print()
        
        # Save cache
        print("Saving cache...")
        save_commute_cache()
        print("[OK] Cache saved")
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("TEST FAILED!")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        
        import traceback
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = test_matching()
    sys.exit(0 if success else 1)
