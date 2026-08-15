#!/usr/bin/env python3
"""
Final comparison report: Actual vs Optimal assignments
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_final_report():
    """Create final comparison report"""
    print("Creating final comparison report...")
    
    try:
        # Load actual data
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_actual = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        # Filter for Fall 2025 interns (rows 338-367)
        fall_2025_df = df_actual.iloc[337:367].copy()
        
        # Extract actual assignments
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            if pd.notna(row.iloc[13]):  # Assignment column
                intern_name = row.iloc[1]
                actual_restaurant = row.iloc[13]
                actual_assignments.append({
                    'intern_name': intern_name,
                    'actual_restaurant': actual_restaurant
                })
        
        # Get optimal assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        optimal_assignments = results.get('assignments', [])
        
        # Create comparison data
        comparison_data = []
        
        # Process actual assignments
        for actual in actual_assignments:
            intern_name = actual['intern_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find corresponding optimal assignment
            optimal_assignment = None
            for opt in optimal_assignments:
                if opt['intern_name'] == intern_name:
                    optimal_assignment = opt
                    break
            
            if optimal_assignment:
                optimal_restaurant = optimal_assignment['restaurant_name']
                optimal_commute = optimal_assignment['commute_minutes']
                optimal_hours = optimal_assignment['total_overlap_hours']
                optimal_days = optimal_assignment['days_matched']
                
                comparison_data.append({
                    'Intern Name': intern_name,
                    'Actual Restaurant': actual_restaurant,
                    'Optimal Restaurant': optimal_restaurant,
                    'Assignment Changed': 'Yes' if actual_restaurant != optimal_restaurant else 'No',
                    'Optimal Commute (min)': optimal_commute,
                    'Optimal Hours': optimal_hours,
                    'Optimal Days': optimal_days
                })
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Save to CSV
        df.to_csv('actual_vs_optimal_final_comparison.csv', index=False)
        
        # Calculate summary
        summary = {
            'Total Interns with Data': len(df),
            'Assignments Changed': df[df['Assignment Changed'] == 'Yes'].shape[0],
            'Assignment Change Rate': df[df['Assignment Changed'] == 'Yes'].shape[0] / len(df) * 100,
            'Average Optimal Commute': df['Optimal Commute (min)'].mean(),
            'Min Optimal Commute': df['Optimal Commute (min)'].min(),
            'Max Optimal Commute': df['Optimal Commute (min)'].max(),
            'Average Optimal Hours': df['Optimal Hours'].mean()
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('final_comparison_summary.csv', index=False)
        
        return df, summary
        
    except Exception as e:
        print(f"Error creating final report: {e}")
        return None, None

def print_final_summary(df, summary):
    """Print final summary"""
    print("\n" + "="*70)
    print("FINAL COMPARISON REPORT: ACTUAL vs OPTIMAL ASSIGNMENTS")
    print("="*70)
    
    if summary:
        print(f"\nSUMMARY METRICS:")
        print(f"Total Interns with Data: {summary['Total Interns with Data']}")
        print(f"Assignments Changed: {summary['Assignments Changed']} ({summary['Assignment Change Rate']:.1f}%)")
        print(f"Average Optimal Commute: {summary['Average Optimal Commute']:.1f} minutes")
        print(f"Commute Range: {summary['Min Optimal Commute']:.0f} - {summary['Max Optimal Commute']:.0f} minutes")
        print(f"Average Optimal Hours: {summary['Average Optimal Hours']:.1f} hours")
    
    if df is not None:
        print(f"\nASSIGNMENT CHANGES:")
        changed = df[df['Assignment Changed'] == 'Yes']
        unchanged = df[df['Assignment Changed'] == 'No']
        
        print(f"Changed Assignments ({len(changed)}):")
        for _, row in changed.iterrows():
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} -> {row['Optimal Restaurant']}")
        
        print(f"\nUnchanged Assignments ({len(unchanged)}):")
        for _, row in unchanged.iterrows():
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} (same)")
        
        print(f"\nOPTIMAL COMMUTE DISTRIBUTION:")
        bins = [0, 15, 25, 35, 50, 100]
        labels = ['<15 min', '15-25 min', '25-35 min', '35-50 min', '>50 min']
        
        df['Commute Category'] = pd.cut(df['Optimal Commute (min)'], bins=bins, labels=labels, right=False)
        commute_dist = df['Commute Category'].value_counts().sort_index()
        
        for category, count in commute_dist.items():
            percentage = count / len(df) * 100
            print(f"  {category}: {count} interns ({percentage:.1f}%)")

def main():
    """Main function"""
    print("="*70)
    print("FINAL COMPARISON REPORT GENERATOR")
    print("Actual Fall 2025 vs Optimal Assignments")
    print("="*70)
    
    # Create final report
    df, summary = create_final_report()
    
    # Print summary
    print_final_summary(df, summary)
    
    print(f"\nFILES CREATED:")
    print(f"1. actual_vs_optimal_final_comparison.csv - Detailed comparison")
    print(f"2. final_comparison_summary.csv - Summary metrics")
    
    print(f"\nFINAL REPORT COMPLETE!")

if __name__ == "__main__":
    main()
