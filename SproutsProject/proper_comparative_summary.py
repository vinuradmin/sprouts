#!/usr/bin/env python3
"""
Create proper comparative summary with name matching
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_proper_comparative_summary():
    """Create proper comparative summary"""
    print("="*60)
    print("CREATING PROPER COMPARATIVE SUMMARY")
    print("="*60)
    
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
        
        # Create name mapping
        print("Creating name mapping...")
        
        # Extract actual assignments with better name matching
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[13]  # Restaurant column
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                # Clean up restaurant names
                if actual_restaurant == 'nan':
                    actual_restaurant = 'Unassigned'
                
                actual_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant
                })
        
        print(f"Actual assignments extracted: {len(actual_assignments)}")
        
        # Show actual names for debugging
        print(f"\nActual names from Excel:")
        for i, actual in enumerate(actual_assignments[:10]):
            print(f"  {i+1}. '{actual['actual_name']}' -> '{actual['actual_restaurant']}'")
        
        # Show algorithm names
        print(f"\nAlgorithm names from database:")
        for i, assign in enumerate(assignments[:10]):
            print(f"  {i+1}. '{assign['intern_name']}' -> '{assign['restaurant_name']}'")
        
        # Create fuzzy matching
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
                    
                    # Check if actual name is contained in algorithm name or vice versa
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
        
        print(f"\nComparative data created: {len(comparative_data)} records")
        
        # Create DataFrame
        df = pd.DataFrame(comparative_data)
        
        # Save to CSV
        df.to_csv('fall_2025_vs_algorithm_proper_comparison.csv', index=False)
        print(f"Proper comparative summary saved to 'fall_2025_vs_algorithm_proper_comparison.csv'")
        
        # Calculate summary
        matched_assignments = df[df['Match Type'] != 'None']
        changed_assignments = df[df['Assignment Changed'] == 'Yes']
        
        summary_stats = {
            'Total Actual Interns': len(df),
            'Matched Interns': len(matched_assignments),
            'Unmatched Interns': len(df) - len(matched_assignments),
            'Changed Assignments': len(changed_assignments),
            'Average Algorithm Commute': matched_assignments['Algorithm Commute (min)'].mean() if not matched_assignments.empty else None,
            'Min Algorithm Commute': matched_assignments['Algorithm Commute (min)'].min() if not matched_assignments.empty else None,
            'Max Algorithm Commute': matched_assignments['Algorithm Commute (min)'].max() if not matched_assignments.empty else None
        }
        
        return df, summary_stats
        
    except Exception as e:
        print(f"Error creating proper summary: {e}")
        return None, None

def print_proper_summary(df, summary_stats):
    """Print proper summary"""
    print("\n" + "="*60)
    print("PROPER COMPARATIVE SUMMARY")
    print("="*60)
    
    if summary_stats:
        print(f"\nSUMMARY STATISTICS:")
        print(f"Total Actual Interns: {summary_stats['Total Actual Interns']}")
        print(f"Matched Interns: {summary_stats['Matched Interns']}")
        print(f"Unmatched Interns: {summary_stats['Unmatched Interns']}")
        print(f"Changed Assignments: {summary_stats['Changed Assignments']}")
        
        if summary_stats['Average Algorithm Commute'] is not None:
            print(f"Average Algorithm Commute: {summary_stats['Average Algorithm Commute']:.1f} minutes")
            print(f"Commute Range: {summary_stats['Min Algorithm Commute']:.0f}-{summary_stats['Max Algorithm Commute']:.0f} minutes")
    
    if df is not None:
        print(f"\nMATCHED ASSIGNMENTS:")
        matched = df[df['Match Type'] != 'None']
        
        print(f"\nExact Matches:")
        exact_matches = matched[matched['Match Type'] == 'Exact']
        for _, row in exact_matches.iterrows():
            change_status = row['Assignment Changed']
            print(f"  {row['Actual Name']} -> {row['Algorithm Restaurant']} ({change_status})")
        
        print(f"\nPartial Matches:")
        partial_matches = matched[matched['Match Type'] == 'Partial']
        for _, row in partial_matches.iterrows():
            print(f"  '{row['Actual Name']}' -> '{row['Algorithm Name']}' -> {row['Algorithm Restaurant']}")
        
        print(f"\nUnmatched Interns:")
        unmatched = df[df['Match Type'] == 'None']
        for _, row in unmatched.iterrows():
            print(f"  {row['Actual Name']} -> {row['Actual Restaurant']} (No algorithm match)")
        
        if not matched.empty:
            print(f"\nTOP COMMUTES:")
            valid_commutes = matched[matched['Algorithm Commute (min)'].notna()]
            if not valid_commutes.empty:
                top_commutes = valid_commutes.nsmallest(5, 'Algorithm Commute (min)')
                for _, row in top_commutes.iterrows():
                    print(f"  {row['Actual Name']} -> {row['Algorithm Restaurant']}: {row['Algorithm Commute (min)']} min")

def main():
    """Main function"""
    print("="*60)
    print("PROPER COMPARATIVE SUMMARY GENERATOR")
    print("With name matching between Excel and database")
    print("="*60)
    
    # Create proper summary
    df, summary_stats = create_proper_comparative_summary()
    
    # Print summary
    print_proper_summary(df, summary_stats)
    
    print(f"\nFILES CREATED:")
    print(f"1. fall_2025_vs_algorithm_proper_comparison.csv - Proper comparison")
    
    print(f"\nPROPER COMPARATIVE SUMMARY COMPLETE!")

if __name__ == "__main__":
    main()
