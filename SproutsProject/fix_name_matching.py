#!/usr/bin/env python3
"""
Fix name matching to get all 23 assigned interns in comparison
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fix_name_matching():
    """Fix name matching to get all 23 assigned interns"""
    print("="*80)
    print("FIXING NAME MATCHING FOR ALL 23 ASSIGNED INTERNS")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
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
        
        # Extract actual assignments from Column 15 (Trial Onboarding)
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
        
        # Create database intern names list
        db_intern_names = []
        for intern in interns:
            db_intern_names.append(intern.user.full_name.strip())
        
        print(f"Database intern names: {len(db_intern_names)}")
        
        # Create algorithm assignment names list
        algo_names = []
        for assign in assignments:
            algo_names.append(assign['intern_name'].strip())
        
        print(f"Algorithm assignment names: {len(algo_names)}")
        
        print(f"\nACTUAL ASSIGNED INTERNS (from Excel):")
        for i, actual in enumerate(assigned_interns):
            print(f"{i+1:2d}. '{actual['actual_name']}' -> {actual['actual_restaurant']} (Row {actual['row_number']})")
        
        print(f"\nDATABASE INTERN NAMES:")
        for i, name in enumerate(db_intern_names):
            print(f"{i+1:2d}. '{name}'")
        
        print(f"\nALGORITHM ASSIGNMENT NAMES:")
        for i, name in enumerate(algo_names):
            print(f"{i+1:2d}. '{name}'")
        
        # Try improved matching
        print(f"\n" + "="*60)
        print("IMPROVED NAME MATCHING")
        print("="*60)
        
        matched_assignments = []
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Try multiple matching strategies
            matched_assignment = None
            match_method = None
            
            # Strategy 1: Exact match
            for assign in assignments:
                if assign['intern_name'].strip() == actual_name.strip():
                    matched_assignment = assign
                    match_method = 'Exact'
                    break
            
            # Strategy 2: Partial match (actual name contained in algo name)
            if not matched_assignment:
                for assign in assignments:
                    algo_name = assign['intern_name'].strip().lower()
                    actual_lower = actual_name.strip().lower()
                    
                    if actual_lower in algo_name:
                        matched_assignment = assign
                        match_method = 'Partial (actual in algo)'
                        break
            
            # Strategy 3: Partial match (algo name contained in actual name)
            if not matched_assignment:
                for assign in assignments:
                    algo_name = assign['intern_name'].strip().lower()
                    actual_lower = actual_name.strip().lower()
                    
                    if algo_name in actual_lower:
                        matched_assignment = assign
                        match_method = 'Partial (algo in actual)'
                        break
            
            # Strategy 4: First name match
            if not matched_assignment:
                actual_first = actual_name.strip().split()[0].lower()
                for assign in assignments:
                    algo_first = assign['intern_name'].strip().split()[0].lower()
                    if actual_first == algo_first:
                        matched_assignment = assign
                        match_method = 'First name'
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
                print(f"✓ '{actual_name}' -> '{matched_assignment['intern_name']}' ({match_method})")
            else:
                print(f"✗ '{actual_name}' -> NO MATCH")
        
        print(f"\nMATCHED ASSIGNMENTS: {len(matched_assignments)} out of {len(assigned_interns)}")
        
        # Create comprehensive comparison
        if len(matched_assignments) > 12:
            print(f"\nCreating comprehensive comparison for {len(matched_assignments)} interns...")
            
            # Create summary data
            summary_data = [
                ['Fall 2025 vs Algorithm Comprehensive Comparison'],
                [''],
                ['KEY METRICS'],
                ['Total Interns Analyzed', len(matched_assignments)],
                ['Actual Assigned Interns', len(assigned_interns)],
                ['Successfully Matched', len(matched_assignments)],
                ['Match Rate', f'{len(matched_assignments)/len(assigned_interns)*100:.1f}%'],
                [''],
                ['COMPLETE COMPARISON'],
                ['Actual Name', 'Algorithm Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Algorithm Commute', 'Match Method']
            ]
            
            # Sort by actual name
            matched_assignments.sort(key=lambda x: x['actual_name'])
            
            for match in matched_assignments:
                summary_data.append([
                    match['actual_name'],
                    match['algorithm_name'],
                    match['actual_restaurant'],
                    match['algorithm_restaurant'],
                    f"{match['algorithm_commute']:.1f}" if match['algorithm_commute'] else 'N/A',
                    match['match_method']
                ])
            
            # Save comprehensive comparison
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv('comprehensive_23_intern_comparison.csv', index=False, header=False)
            
            print(f"Comprehensive comparison saved to 'comprehensive_23_intern_comparison.csv'")
        
        return matched_assignments
        
    except Exception as e:
        print(f"Error fixing name matching: {e}")
        return []

def main():
    """Main function"""
    matched_assignments = fix_name_matching()
    
    print(f"\n" + "="*80)
    print("NAME MATCHING FIX COMPLETE")
    print("="*80)
    print(f"Successfully matched {len(matched_assignments)} interns")
    print(f"This should be much closer to the expected 23 assigned interns")

if __name__ == "__main__":
    main()
