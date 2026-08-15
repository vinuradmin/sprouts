#!/usr/bin/env python3
"""
Corrected comparative summary using the right assignment column (Column 15)
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_corrected_comparative_summary():
    """Create corrected comparative summary using Column 15 (Trial Onboarding)"""
    print("="*80)
    print("CORRECTED COMPARATIVE SUMMARY")
    print("Using Column 15 (Trial Onboarding) for actual assignments")
    print("="*80)
    
    try:
        # Load actual data from Excel
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        # Filter for Fall 2025 interns (rows 338-367)
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
        
        # Extract actual assignments from CORRECT column (Column 15, index 14)
        print("Extracting actual assignments from Column 15 (Trial Onboarding)...")
        
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[14]  # CORRECT: Column 15 (index 14)
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                # Clean up restaurant names
                if actual_restaurant == 'nan' or actual_restaurant == '':
                    actual_restaurant = 'Unassigned'
                
                actual_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant
                })
        
        print(f"Actual assignments extracted: {len(actual_assignments)}")
        
        # Show actual assignments
        print(f"\nActual assignments from Column 15:")
        for i, actual in enumerate(actual_assignments):
            if actual['actual_restaurant'] != 'Unassigned':
                print(f"  {i+1}. {actual['actual_name']} -> {actual['actual_restaurant']}")
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Create comparative data with name matching
        comparative_data = []
        
        for actual in actual_assignments:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Try to find matching algorithm assignment
            matching_assignment = None
            
            # First try exact match
            for assign in assignments:
                if assign['intern_name'].strip() == actual_name.strip():
                    matching_assignment = assign
                    break
            
            # If no exact match, try partial match
            if not matching_assignment:
                for assign in assignments:
                    algo_name = assign['intern_name'].strip().lower()
                    actual_lower = actual_name.strip().lower()
                    
                    # Check for partial matches
                    if (actual_lower in algo_name or algo_name in actual_lower or
                        actual_lower.replace(' ', '') in algo_name.replace(' ', '') or
                        algo_name.replace(' ', '') in actual_lower.replace(' ', '')):
                        matching_assignment = assign
                        break
            
            if matching_assignment:
                algorithm_restaurant = matching_assignment['restaurant_name']
                algorithm_commute = matching_assignment['commute_minutes']
                algorithm_hours = matching_assignment['total_overlap_hours']
                algorithm_days = matching_assignment['days_matched']
                
                assignment_changed = actual_restaurant != algorithm_restaurant and actual_restaurant != 'Unassigned'
                
                comparative_data.append({
                    'Actual Name': actual_name,
                    'Algorithm Name': matching_assignment['intern_name'],
                    'Actual Restaurant': actual_restaurant,
                    'Algorithm Restaurant': algorithm_restaurant,
                    'Assignment Changed': 'Yes' if assignment_changed else 'No',
                    'Algorithm Commute (min)': algorithm_commute,
                    'Algorithm Hours': algorithm_hours,
                    'Algorithm Days': algorithm_days,
                    'Match Type': 'Exact' if matching_assignment['intern_name'].strip() == actual_name.strip() else 'Partial'
                })
            else:
                # No matching algorithm assignment
                comparative_data.append({
                    'Actual Name': actual_name,
                    'Algorithm Name': 'No Match',
                    'Actual Restaurant': actual_restaurant,
                    'Algorithm Restaurant': 'Unassigned',
                    'Assignment Changed': 'N/A',
                    'Algorithm Commute (min)': None,
                    'Algorithm Hours': None,
                    'Algorithm Days': None,
                    'Match Type': 'None'
                })
        
        # Create DataFrame
        df_comparison = pd.DataFrame(comparative_data)
        
        # Save to CSV
        df_comparison.to_csv('corrected_fall_2025_vs_algorithm_comparison.csv', index=False)
        print(f"Corrected comparative summary saved to 'corrected_fall_2025_vs_algorithm_comparison.csv'")
        
        # Calculate summary
        matched_assignments = df_comparison[df_comparison['Match Type'] != 'None']
        changed_assignments = df_comparison[df_comparison['Assignment Changed'] == 'Yes']
        actual_assigned = df_comparison[df_comparison['Actual Restaurant'] != 'Unassigned']
        
        summary_stats = {
            'Total Actual Interns': len(df_comparison),
            'Actually Assigned': len(actual_assigned),
            'Matched Interns': len(matched_assignments),
            'Unmatched Interns': len(df_comparison) - len(matched_assignments),
            'Changed Assignments': len(changed_assignments),
            'Average Algorithm Commute': matched_assignments['Algorithm Commute (min)'].mean() if not matched_assignments.empty else None,
            'Min Algorithm Commute': matched_assignments['Algorithm Commute (min)'].min() if not matched_assignments.empty else None,
            'Max Algorithm Commute': matched_assignments['Algorithm Commute (min)'].max() if not matched_assignments.empty else None
        }
        
        return df_comparison, summary_stats
        
    except Exception as e:
        print(f"Error creating corrected summary: {e}")
        return None, None

def print_corrected_summary(df, summary_stats):
    """Print corrected summary"""
    print("\n" + "="*80)
    print("CORRECTED COMPARATIVE SUMMARY")
    print("Using actual assignments from Column 15 (Trial Onboarding)")
    print("="*80)
    
    if summary_stats:
        print(f"\nCORRECTED SUMMARY STATISTICS:")
        print(f"Total Actual Interns: {summary_stats['Total Actual Interns']}")
        print(f"Actually Assigned in Fall 2025: {summary_stats['Actually Assigned']}")
        print(f"Matched Interns: {summary_stats['Matched Interns']}")
        print(f"Unmatched Interns: {summary_stats['Unmatched Interns']}")
        print(f"Changed Assignments: {summary_stats['Changed Assignments']}")
        
        if summary_stats['Average Algorithm Commute'] is not None:
            print(f"Average Algorithm Commute: {summary_stats['Average Algorithm Commute']:.1f} minutes")
            print(f"Commute Range: {summary_stats['Min Algorithm Commute']:.0f}-{summary_stats['Max Algorithm Commute']:.0f} minutes")
    
    if df is not None:
        print(f"\nACTUAL FALL 2025 ASSIGNMENTS (Column 15):")
        actual_assigned = df[df['Actual Restaurant'] != 'Unassigned']
        for _, row in actual_assigned.iterrows():
            print(f"  {row['Actual Name']} -> {row['Actual Restaurant']}")
        
        print(f"\nMATCHED ASSIGNMENTS WITH COMPARISON:")
        matched = df[df['Match Type'] != 'None']
        for _, row in matched.iterrows():
            actual_rest = row['Actual Restaurant']
            algo_rest = row['Algorithm Restaurant']
            change_status = row['Assignment Changed']
            commute = row['Algorithm Commute (min)']
            
            if actual_rest != 'Unassigned':
                print(f"  {row['Actual Name']}: {actual_rest} -> {algo_rest} ({change_status}, {commute} min)")
            else:
                print(f"  {row['Actual Name']}: Unassigned -> {algo_rest} ({commute} min)")
        
        print(f"\nASSIGNMENT CHANGES:")
        changed = df[df['Assignment Changed'] == 'Yes']
        if not changed.empty:
            for _, row in changed.iterrows():
                print(f"  {row['Actual Name']}: {row['Actual Restaurant']} -> {row['Algorithm Restaurant']}")
        else:
            print("  No assignment changes for matched interns")
        
        print(f"\nTOP COMMUTES:")
        valid_commutes = matched[matched['Algorithm Commute (min)'].notna()]
        if not valid_commutes.empty:
            top_commutes = valid_commutes.nsmallest(5, 'Algorithm Commute (min)')
            for _, row in top_commutes.iterrows():
                print(f"  {row['Actual Name']} -> {row['Algorithm Restaurant']}: {row['Algorithm Commute (min)']} min")

def main():
    """Main function"""
    print("="*80)
    print("CORRECTED COMPARATIVE SUMMARY GENERATOR")
    print("Using Column 15 (Trial Onboarding) for actual assignments")
    print("="*80)
    
    # Create corrected summary
    df, summary_stats = create_corrected_comparative_summary()
    
    # Print summary
    print_corrected_summary(df, summary_stats)
    
    print(f"\nFILES CREATED:")
    print(f"1. corrected_fall_2025_vs_algorithm_comparison.csv - Corrected comparison")
    
    print(f"\nCORRECTED COMPARATIVE SUMMARY COMPLETE!")

if __name__ == "__main__":
    main()
