#!/usr/bin/env python3
"""
Debug and fix the name matching logic
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_name_matching():
    """Debug the name matching logic"""
    print("="*80)
    print("DEBUGGING NAME MATCHING LOGIC")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Load Intern Availabilities sheet for cross-reference
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
        
        # Extract actual assignments
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                if actual_restaurant == 'nan' or actual_restaurant == '':
                    actual_restaurant = 'Unassigned'
                
                actual_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'row_number': idx + 338
                })
        
        # Filter to only assigned interns
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        print(f"DEBUG - Algorithm assignments:")
        for i, (name, assign) in enumerate(algorithm_lookup.items()):
            print(f"{i+1:2d}. '{name}' -> {assign['restaurant_name']}")
        
        print(f"\nDEBUG - Actual assigned interns:")
        for i, actual in enumerate(assigned_interns):
            print(f"{i+1:2d}. '{actual['actual_name']}' -> {actual['actual_restaurant']}")
        
        # Test first name matching for specific cases
        print(f"\nDEBUG - Testing first name matching:")
        
        test_cases = ['Gylli', 'Nae', 'maye', 'Shelsea', 'Gio', 'Roni']
        
        for actual_name in test_cases:
            print(f"\nTesting: '{actual_name}'")
            actual_first = actual_name.strip().split()[0].lower()
            print(f"  First name to match: '{actual_first}'")
            
            matches = []
            for algo_name in algorithm_lookup:
                algo_first = algo_name.strip().split()[0].lower()
                if actual_first == algo_first:
                    matches.append(algo_name)
                    print(f"  MATCH: '{algo_name}' -> {algorithm_lookup[algo_name]['restaurant_name']}")
            
            if not matches:
                print(f"  No first name matches found")
        
        # Check Intern Availabilities for specific cases
        print(f"\nDEBUG - Checking Intern Availabilities:")
        
        for actual_name in test_cases:
            print(f"\nChecking '{actual_name}' in Intern Availabilities:")
            
            avail_matches = []
            for idx, row in avail_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                avail_first = str(row.iloc[1]).strip()  # First Name column
                avail_last = str(row.iloc[2]).strip()   # Last Name column
                avail_full = f"{avail_first} {avail_last}".strip()
                
                # Check for matches
                if (actual_name.lower() == avail_first.lower() or 
                    actual_name.lower() == avail_full.lower()):
                    avail_matches.append({
                        'full_name': avail_full,
                        'row': idx,
                        'is_last': idx == len(avail_df) - 1
                    })
                    print(f"  Found: '{avail_full}' at row {idx}")
            
            if not avail_matches:
                print(f"  No matches found in Intern Availabilities")
        
        # Now try improved matching
        print(f"\n" + "="*60)
        print("IMPROVED MATCHING ATTEMPT")
        print("="*60)
        
        matched_assignments = []
        unmatched_assignments = []
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            matched_assignment = None
            match_method = None
            
            # Strategy 1: Exact match
            if actual_name in algorithm_lookup:
                matched_assignment = algorithm_lookup[actual_name]
                match_method = 'Exact match'
            
            # Strategy 2: First name match (improved)
            if not matched_assignment:
                actual_first = actual_name.strip().split()[0].lower()
                
                # Handle special cases
                if actual_name == 'Gylli':
                    # Look for Gyllibhet
                    for algo_name in algorithm_lookup:
                        if 'gyllibhet' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (Gylli -> Gyllibhet)'
                            break
                
                elif actual_name == 'Nae':
                    # Look for Eljanae
                    for algo_name in algorithm_lookup:
                        if 'eljanae' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (Nae -> Eljanae)'
                            break
                
                elif actual_name == 'maye':
                    # Look for Yeimi
                    for algo_name in algorithm_lookup:
                        if 'yeimi' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (maye -> Yeimi)'
                            break
                
                elif actual_name == 'Shelsea':
                    # Look for Shelsea
                    for algo_name in algorithm_lookup:
                        if 'shelsea' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (Shelsea -> Shelsea)'
                            break
                
                elif actual_name == 'Gio':
                    # Look for Giovanni
                    for algo_name in algorithm_lookup:
                        if 'giovanni' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (Gio -> Giovanni)'
                            break
                
                elif actual_name == 'Roni':
                    # Look for Roni
                    for algo_name in algorithm_lookup:
                        if 'roni' in algo_name.lower():
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = 'Special case (Roni -> Roni)'
                            break
                
                else:
                    # General first name match
                    for algo_name in algorithm_lookup:
                        algo_first = algo_name.strip().split()[0].lower()
                        if actual_first == algo_first:
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = f'First name match ({actual_name} -> {algo_name})'
                            break
            
            if matched_assignment:
                matched_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_name': matched_assignment['intern_name'],
                    'algorithm_restaurant': matched_assignment['restaurant_name'],
                    'algorithm_commute': matched_assignment['commute_minutes'],
                    'match_method': match_method
                })
                
                print(f"MATCH: {actual_name} -> {matched_assignment['intern_name']} -> {matched_assignment['restaurant_name']} ({matched_assignment['commute_minutes']} min)")
                print(f"  Method: {match_method}")
            else:
                unmatched_assignments.append(actual)
                print(f"NO MATCH: {actual_name} -> {actual_restaurant}")
        
        print(f"\nIMPROVED RESULTS:")
        print(f"Matched: {len(matched_assignments)}")
        print(f"Unmatched: {len(unmatched_assignments)}")
        print(f"Match Rate: {len(matched_assignments)/len(assigned_interns)*100:.1f}%")
        
        return matched_assignments, unmatched_assignments
        
    except Exception as e:
        print(f"Error in debugging: {e}")
        return [], []

def main():
    """Main function"""
    matched, unmatched = debug_name_matching()

if __name__ == "__main__":
    main()
