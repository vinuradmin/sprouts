#!/usr/bin/env python3
"""
Debug and create working comparative summary
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_data_loading():
    """Debug data loading issues"""
    print("DEBUGGING DATA LOADING...")
    
    try:
        # Load actual data
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        print(f"Excel sheet shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Filter for Fall 2025 interns
        fall_2025_df = df.iloc[337:367].copy()
        print(f"Fall 2025 interns shape: {fall_2025_df.shape}")
        
        # Show sample data
        print(f"\nSample Fall 2025 data:")
        for idx, row in fall_2025_df.head(3).iterrows():
            print(f"Row {idx}: Name={row.iloc[1]}, Restaurant={row.iloc[13]}")
        
        # Get algorithm data
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"\nDatabase interns: {len(interns)}")
        print(f"Database restaurants: {len(restaurants)}")
        
        # Show sample intern names
        print(f"\nSample intern names:")
        for i, intern in enumerate(interns[:5]):
            print(f"  {i+1}. {intern.user.full_name}")
        
        # Get algorithm assignments
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"\nAlgorithm assignments: {len(assignments)}")
        print(f"Sample assignments:")
        for i, assign in enumerate(assignments[:3]):
            print(f"  {i+1}. {assign['intern_name']} -> {assign['restaurant_name']}")
        
        return fall_2025_df, assignments, interns
        
    except Exception as e:
        print(f"Error in debug: {e}")
        return None, None, None

def create_working_comparative_summary():
    """Create working comparative summary"""
    print("\n" + "="*60)
    print("CREATING WORKING COMPARATIVE SUMMARY")
    print("="*60)
    
    try:
        # Debug data loading
        fall_2025_df, assignments, interns = debug_data_loading()
        
        if fall_2025_df is None or assignments is None:
            print("Could not load data properly")
            return
        
        # Create intern name mapping
        intern_names = [intern.user.full_name for intern in interns]
        print(f"\nIntern names from database: {len(intern_names)}")
        print(f"Sample: {intern_names[:5]}")
        
        # Extract actual assignments
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            intern_name = str(row.iloc[1]).strip()
            actual_restaurant = str(row.iloc[13]).strip() if pd.notna(row.iloc[13]) else 'Unassigned'
            
            if intern_name and intern_name != 'nan':
                actual_assignments.append({
                    'intern_name': intern_name,
                    'actual_restaurant': actual_restaurant
                })
        
        print(f"\nActual assignments extracted: {len(actual_assignments)}")
        print(f"Sample actual assignments:")
        for i, actual in enumerate(actual_assignments[:5]):
            print(f"  {i+1}. {actual['intern_name']} -> {actual['actual_restaurant']}")
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        print(f"\nAlgorithm lookup created: {len(algorithm_lookup)} entries")
        
        # Create comparative data
        comparative_data = []
        
        for actual in actual_assignments:
            intern_name = actual['intern_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find matching algorithm assignment
            algorithm_assignment = algorithm_lookup.get(intern_name)
            
            if algorithm_assignment:
                algorithm_restaurant = algorithm_assignment['restaurant_name']
                algorithm_commute = algorithm_assignment['commute_minutes']
                algorithm_hours = algorithm_assignment['total_overlap_hours']
                algorithm_days = algorithm_assignment['days_matched']
                
                assignment_changed = actual_restaurant != algorithm_restaurant
                
                comparative_data.append({
                    'Intern Name': intern_name,
                    'Actual Restaurant': actual_restaurant,
                    'Algorithm Restaurant': algorithm_restaurant,
                    'Assignment Changed': 'Yes' if assignment_changed else 'No',
                    'Algorithm Commute (min)': algorithm_commute,
                    'Algorithm Hours': algorithm_hours,
                    'Algorithm Days': algorithm_days
                })
            else:
                # No algorithm assignment found
                comparative_data.append({
                    'Intern Name': intern_name,
                    'Actual Restaurant': actual_restaurant,
                    'Algorithm Restaurant': 'Unassigned',
                    'Assignment Changed': 'Yes',
                    'Algorithm Commute (min)': None,
                    'Algorithm Hours': None,
                    'Algorithm Days': None
                })
        
        print(f"\nComparative data created: {len(comparative_data)} records")
        
        # Create DataFrame
        df = pd.DataFrame(comparative_data)
        
        # Save to CSV
        df.to_csv('fall_2025_vs_algorithm_comparison.csv', index=False)
        print(f"Comparative summary saved to 'fall_2025_vs_algorithm_comparison.csv'")
        
        # Calculate summary
        summary_stats = {
            'Total Interns': len(df),
            'Assignments Changed': df[df['Assignment Changed'] == 'Yes'].shape[0],
            'Unchanged Assignments': df[df['Assignment Changed'] == 'No'].shape[0],
            'Average Algorithm Commute': df['Algorithm Commute (min)'].mean(),
            'Min Algorithm Commute': df['Algorithm Commute (min)'].min(),
            'Max Algorithm Commute': df['Algorithm Commute (min)'].max(),
            'Average Algorithm Hours': df['Algorithm Hours'].mean()
        }
        
        return df, summary_stats
        
    except Exception as e:
        print(f"Error creating working summary: {e}")
        return None, None

def print_working_summary(df, summary_stats):
    """Print working summary"""
    print("\n" + "="*60)
    print("WORKING COMPARATIVE SUMMARY")
    print("="*60)
    
    if summary_stats:
        print(f"\nSUMMARY STATISTICS:")
        print(f"Total Interns: {summary_stats['Total Interns']}")
        print(f"Assignments Changed: {summary_stats['Assignments Changed']}")
        print(f"Unchanged Assignments: {summary_stats['Unchanged Assignments']}")
        print(f"Average Algorithm Commute: {summary_stats['Average Algorithm Commute']:.1f} minutes")
        print(f"Commute Range: {summary_stats['Min Algorithm Commute']:.0f}-{summary_stats['Max Algorithm Commute']:.0f} minutes")
        print(f"Average Algorithm Hours: {summary_stats['Average Algorithm Hours']:.1f}")
    
    if df is not None:
        print(f"\nASSIGNMENT CHANGES:")
        changed = df[df['Assignment Changed'] == 'Yes']
        unchanged = df[df['Assignment Changed'] == 'No']
        
        print(f"\nChanged Assignments ({len(changed)}):")
        for _, row in changed.iterrows():
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} -> {row['Algorithm Restaurant']}")
        
        print(f"\nUnchanged Assignments ({len(unchanged)}):")
        for _, row in unchanged.iterrows():
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} (same)")
        
        print(f"\nTOP COMMUTES:")
        valid_commutes = df[df['Algorithm Commute (min)'].notna()]
        if not valid_commutes.empty:
            top_commutes = valid_commutes.nsmallest(5, 'Algorithm Commute (min)')
            for _, row in top_commutes.iterrows():
                print(f"  {row['Intern Name']} -> {row['Algorithm Restaurant']}: {row['Algorithm Commute (min)']} min")

def main():
    """Main function"""
    print("="*60)
    print("DEBUG AND CREATE WORKING COMPARATIVE SUMMARY")
    print("="*60)
    
    # Create working summary
    df, summary_stats = create_working_comparative_summary()
    
    # Print summary
    print_working_summary(df, summary_stats)
    
    print(f"\nFILES CREATED:")
    print(f"1. fall_2025_vs_algorithm_comparison.csv - Working comparison")
    
    print(f"\nWORKING COMPARATIVE SUMMARY COMPLETE!")

if __name__ == "__main__":
    main()
