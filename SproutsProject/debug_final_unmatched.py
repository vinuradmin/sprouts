#!/usr/bin/env python3
"""
Debug why the final 4 interns are still unmatched
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_final_unmatched():
    """Debug the final 4 unmatched interns"""
    print("="*80)
    print("DEBUGGING FINAL 4 UNMATCHED INTERNS")
    print("="*80)
    
    try:
        # The 4 unmatched interns and their actual assignments
        unmatched_cases = [
            {'actual_name': 'Alex', 'actual_restaurant': 'Stanford'},
            {'actual_name': 'Andrea', 'actual_restaurant': 'Stanford'},
            {'actual_name': 'Shelsea', 'actual_restaurant': 'Burdell'},
            {'actual_name': 'Roni', 'actual_restaurant': 'Teranga'}
        ]
        
        # Load Intern Availabilities
        avail_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv')
        
        # Get algorithm assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        print(f"Algorithm assignments available: {len(algorithm_lookup)}")
        
        for case in unmatched_cases:
            actual_name = case['actual_name']
            actual_restaurant = case['actual_restaurant']
            
            print(f"\n{'='*60}")
            print(f"DEBUGGING: '{actual_name}' -> '{actual_restaurant}'")
            print(f"{'='*60}")
            
            # Step 1: Check Intern Availabilities
            print(f"Step 1: Checking Intern Availabilities...")
            
            avail_matches = []
            for idx, row in avail_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                first_name = str(row.iloc[1]).strip()
                last_name = str(row.iloc[2]).strip()
                full_name = f"{first_name} {last_name}".strip()
                
                if actual_name.lower() == first_name.lower():
                    avail_matches.append({
                        'full_name': full_name,
                        'row': idx,
                        'is_last': idx == len(avail_df) - 1
                    })
            
            if avail_matches:
                last_match = avail_matches[-1]
                avail_full_name = last_match['full_name']
                print(f"  Found in Intern Availabilities: '{avail_full_name}' (row {last_match['row']})")
            else:
                print(f"  NOT found in Intern Availabilities")
                continue
            
            # Step 2: Check if availabilities name matches database
            print(f"Step 2: Checking database matches for '{avail_full_name}'...")
            
            database_names = [intern.user.full_name for intern in interns]
            db_matches = []
            
            for db_name in database_names:
                db_lower = db_name.lower()
                avail_lower = avail_full_name.lower()
                
                if (avail_lower in db_lower or db_lower in avail_lower or
                    avail_lower.replace(' ', '') in db_lower.replace(' ', '') or
                    db_lower.replace(' ', '') in avail_lower.replace(' ', '')):
                    db_matches.append(db_name)
            
            if db_matches:
                print(f"  Database matches: {db_matches}")
                best_match = db_matches[0]
                print(f"  Best database match: '{best_match}'")
            else:
                print(f"  NO database matches found")
                continue
            
            # Step 3: Check if database name has algorithm assignment
            print(f"Step 3: Checking algorithm assignment for '{best_match}'...")
            
            if best_match in algorithm_lookup:
                algo_assignment = algorithm_lookup[best_match]
                print(f"  Algorithm assignment: {algo_assignment['restaurant_name']} ({algo_assignment['commute_minutes']} min)")
                print(f"  SUCCESS: Should be matched!")
            else:
                print(f"  NO algorithm assignment found for '{best_match}'")
                print(f"  Available algorithm names:")
                for i, name in enumerate(algorithm_lookup.keys()):
                    if i < 10:  # Show first 10
                        print(f"    {i+1}. '{name}'")
                    elif i == 10:
                        print(f"    ... and {len(algorithm_lookup)-10} more")
                        break
        
        # Manual check for specific database names
        print(f"\n" + "="*60)
        print("MANUAL CHECK FOR SPECIFIC DATABASE NAMES")
        print("="*60)
        
        target_names = ['Alexander Barrios Castañeda', 'Andrea Caballero ', 'Shelsea Vasquez', 'Roni Velasquez']
        
        for target_name in target_names:
            print(f"\nChecking: '{target_name}'")
            if target_name in algorithm_lookup:
                assignment = algorithm_lookup[target_name]
                print(f"  HAS algorithm assignment: {assignment['restaurant_name']} ({assignment['commute_minutes']} min)")
            else:
                print(f"  NO algorithm assignment")
        
        return True
        
    except Exception as e:
        print(f"Error debugging: {e}")
        return False

def main():
    """Main function"""
    debug_final_unmatched()

if __name__ == "__main__":
    main()
