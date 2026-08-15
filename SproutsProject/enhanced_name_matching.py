#!/usr/bin/env python3
"""
Enhanced name matching with last name assumptions and Intern Availabilities cross-reference
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def enhanced_name_matching():
    """Enhanced name matching with better logic"""
    print("="*80)
    print("ENHANCED NAME MATCHING")
    print("With last name assumptions and Intern Availabilities cross-reference")
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
        print(f"Actual assigned interns: {len(assigned_interns)}")
        
        # Create database intern lookup
        database_interns = {}
        for intern in interns:
            database_interns[intern.user.full_name] = intern
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Enhanced matching process
        matched_assignments = []
        unmatched_assignments = []
        
        print(f"\nEnhanced matching process:")
        print("-" * 60)
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            matched_assignment = None
            match_method = None
            
            # Strategy 1: Exact match
            if actual_name in algorithm_lookup:
                matched_assignment = algorithm_lookup[actual_name]
                match_method = 'Exact match'
            
            # Strategy 2: First name match (assume last name matches)
            if not matched_assignment:
                actual_first = actual_name.strip().split()[0].lower()
                for algo_name in algorithm_lookup:
                    algo_first = algo_name.strip().split()[0].lower()
                    if actual_first == algo_first:
                        matched_assignment = algorithm_lookup[algo_name]
                        match_method = f'First name match ({actual_name} -> {algo_name})'
                        break
            
            # Strategy 3: Check Intern Availabilities sheet for completely different names
            if not matched_assignment:
                # Look for the actual name in Intern Availabilities
                avail_matches = []
                for idx, row in avail_df.iterrows():
                    if idx == 0:  # Skip header
                        continue
                    
                    avail_first = str(row.iloc[1]).strip()  # First Name column
                    avail_last = str(row.iloc[2]).strip()   # Last Name column
                    avail_full = f"{avail_first} {avail_last}".strip()
                    
                    # Check if actual name matches first name or full name in availabilities
                    if (actual_name.lower() == avail_first.lower() or 
                        actual_name.lower() == avail_full.lower()):
                        avail_matches.append({
                            'full_name': avail_full,
                            'row': idx,
                            'is_last': idx == len(avail_df) - 1  # Check if last occurrence
                        })
                
                # If found in availabilities, try to match with database
                if avail_matches:
                    # Pick the last occurrence as requested
                    last_match = avail_matches[-1]
                    avail_full_name = last_match['full_name']
                    
                    # Try to match this full name with database
                    for algo_name in algorithm_lookup:
                        algo_lower = algo_name.lower()
                        avail_lower = avail_full_name.lower()
                        
                        # Check for partial matches
                        if (avail_lower in algo_lower or algo_lower in avail_lower or
                            avail_lower.replace(' ', '') in algo_lower.replace(' ', '') or
                            algo_lower.replace(' ', '') in avail_lower.replace(' ', '')):
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = f'Availabilities cross-ref ({actual_name} -> {avail_full_name} -> {algo_name})'
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
        
        print(f"\nRESULTS:")
        print(f"Matched: {len(matched_assignments)}")
        print(f"Unmatched: {len(unmatched_assignments)}")
        print(f"Match Rate: {len(matched_assignments)/len(assigned_interns)*100:.1f}%")
        
        # Create comprehensive comparison
        comparison_data = [
            ['Enhanced Fall 2025 vs Algorithm Comparison'],
            [''],
            ['KEY METRICS'],
            ['Total Assigned Interns', len(assigned_interns)],
            ['Successfully Matched', len(matched_assignments)],
            ['Unmatched', len(unmatched_assignments)],
            ['Match Rate', f'{len(matched_assignments)/len(assigned_interns)*100:.1f}%'],
            [''],
            ['MATCHED INTERNS COMPARISON'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)', 'Status', 'Match Method']
        ]
        
        # Add matched interns
        perfect_matches = 0
        different_matches = 0
        
        for match in matched_assignments:
            if match['actual_restaurant'] == match['algorithm_restaurant']:
                status = 'Perfect Match'
                perfect_matches += 1
            else:
                status = 'Different Assignment'
                different_matches += 1
            
            comparison_data.append([
                match['actual_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                f"{match['algorithm_commute']:.1f}",
                status,
                match['match_method']
            ])
        
        # Add unmatched interns
        comparison_data.extend([
            [''],
            ['UNMATCHED INTERNS'],
            ['Actual Name', 'Actual Restaurant', 'Status']
        ])
        
        for unmatched in unmatched_assignments:
            comparison_data.append([
                unmatched['actual_name'],
                unmatched['actual_restaurant'],
                'No algorithm match'
            ])
        
        # Save comparison
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv('enhanced_23_interns_comparison.csv', index=False, header=False)
        
        print(f"\nEnhanced comparison saved to 'enhanced_23_interns_comparison.csv'")
        
        # Print summary
        print(f"\nENHANCED SUMMARY:")
        print(f"Perfect Matches: {perfect_matches}")
        print(f"Different Assignments: {different_matches}")
        
        if matched_assignments:
            avg_commute = sum(m['algorithm_commute'] for m in matched_assignments if m['algorithm_commute']) / len([m for m in matched_assignments if m['algorithm_commute']])
            print(f"Average Algorithm Commute: {avg_commute:.1f} minutes")
        
        return matched_assignments, unmatched_assignments
        
    except Exception as e:
        print(f"Error in enhanced name matching: {e}")
        return [], []

def main():
    """Main function"""
    matched, unmatched = enhanced_name_matching()
    
    print(f"\n" + "="*80)
    print("ENHANCED NAME MATCHING COMPLETE")
    print("="*80)
    print(f"Enhanced matching for {len(matched) + len(unmatched)} assigned interns")

if __name__ == "__main__":
    main()
