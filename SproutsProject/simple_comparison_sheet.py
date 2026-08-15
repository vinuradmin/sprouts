#!/usr/bin/env python3
"""
Simple comparison sheet: Actual vs Optimal assignments
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_comparison_sheet():
    """Create comparison sheet"""
    print("Creating comparison sheet...")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get optimal assignments
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        optimizer = TransportationOptimizer()
        
        # Create comparison data
        comparison_data = []
        
        for assignment in assignments:
            intern_name = assignment['intern_name']
            restaurant_name = assignment['restaurant_name']
            optimal_commute = assignment['commute_minutes']
            total_hours = assignment['total_overlap_hours']
            days_matched = assignment['days_matched']
            
            # Find intern details
            intern = None
            for i in interns:
                if i.user.full_name == intern_name:
                    intern = i
                    break
            
            if intern:
                # Get transportation options
                transport_options = optimizer.parse_transportation_options(intern.transportation_method or 'driving')
                
                # Get commute comparison
                comparison = optimizer.get_transportation_comparison(
                    intern.get_full_address(),
                    assignment.get('restaurant_address', ''),
                    intern.transportation_method or 'driving'
                )
                
                # Find best and worst commute options
                if comparison:
                    valid_commutes = [v for v in comparison.values() if v is not None]
                    if valid_commutes:
                        min_commute = min(valid_commutes)
                        max_commute = max(valid_commutes)
                        best_option = None
                        for k, v in comparison.items():
                            if v == min_commute:
                                best_option = k
                                break
                    else:
                        min_commute = None
                        max_commute = None
                        best_option = None
                else:
                    min_commute = None
                    max_commute = None
                    best_option = None
                
                comparison_data.append({
                    'Intern Name': intern_name,
                    'Age': intern.age,
                    'Assigned Restaurant': restaurant_name,
                    'Optimal Commute (min)': optimal_commute,
                    'Total Hours': total_hours,
                    'Days Matched': days_matched,
                    'Transportation Options': intern.transportation_method or 'Unknown',
                    'Parsed Options': ', '.join(transport_options),
                    'Best Transport': best_option,
                    'Min Transport Commute': min_commute,
                    'Max Transport Commute': max_commute,
                    'Transport Range': max_commute - min_commute if (max_commute and min_commute) else None,
                    'Transport Optimization': 'Yes' if (max_commute and min_commute and max_commute > min_commute) else 'No'
                })
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Save to CSV
        df.to_csv('optimal_assignments_comparison.csv', index=False)
        print(f"Comparison sheet saved to 'optimal_assignments_comparison.csv'")
        
        # Calculate summary metrics
        summary = {
            'Total Assignments': len(df),
            'Average Commute': df['Optimal Commute (min)'].mean(),
            'Min Commute': df['Optimal Commute (min)'].min(),
            'Max Commute': df['Optimal Commute (min)'].max(),
            'Average Hours': df['Total Hours'].mean(),
            'Transport Optimization Count': df[df['Transport Optimization'] == 'Yes'].shape[0],
            'Transport Optimization Rate': df[df['Transport Optimization'] == 'Yes'].shape[0] / len(df) * 100
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('optimal_assignments_summary.csv', index=False)
        
        return df, summary
        
    except Exception as e:
        print(f"Error creating comparison sheet: {e}")
        return None, None

def print_summary(df, summary):
    """Print summary"""
    print("\n" + "="*60)
    print("OPTIMAL ASSIGNMENTS COMPARISON SUMMARY")
    print("="*60)
    
    if summary:
        print(f"\nOVERALL METRICS:")
        print(f"Total Assignments: {summary['Total Assignments']}")
        print(f"Average Commute: {summary['Average Commute']:.1f} minutes")
        print(f"Commute Range: {summary['Min Commute']:.0f} - {summary['Max Commute']:.0f} minutes")
        print(f"Average Hours: {summary['Average Hours']:.1f} hours")
        print(f"Transport Optimization: {summary['Transport Optimization Count']} interns ({summary['Transport Optimization Rate']:.1f}%)")
    
    if df is not None:
        print(f"\nTOP ASSIGNMENTS BY COMMUTE TIME:")
        top_commutes = df.nsmallest(5, 'Optimal Commute (min)')
        for _, row in top_commutes.iterrows():
            print(f"  {row['Intern Name']} -> {row['Assigned Restaurant']}: {row['Optimal Commute (min)']} min")
        
        print(f"\nASSIGNMENTS WITH TRANSPORT OPTIMIZATION:")
        transport_opt = df[df['Transport Optimization'] == 'Yes']
        for _, row in transport_opt.iterrows():
            print(f"  {row['Intern Name']}: {row['Min Transport Commute']}-{row['Max Transport Commute']} min")
        
        print(f"\nCOMMUTE DISTRIBUTION:")
        bins = [0, 15, 25, 35, 50, 100]
        labels = ['<15 min', '15-25 min', '25-35 min', '35-50 min', '>50 min']
        
        df['Commute Category'] = pd.cut(df['Optimal Commute (min)'], bins=bins, labels=labels, right=False)
        commute_dist = df['Commute Category'].value_counts().sort_index()
        
        for category, count in commute_dist.items():
            percentage = count / len(df) * 100
            print(f"  {category}: {count} interns ({percentage:.1f}%)")

def main():
    """Main function"""
    print("="*60)
    print("OPTIMAL ASSIGNMENTS COMPARISON SHEET")
    print("="*60)
    
    # Create comparison sheet
    df, summary = create_comparison_sheet()
    
    # Print summary
    print_summary(df, summary)
    
    print(f"\nFILES CREATED:")
    print(f"1. optimal_assignments_comparison.csv - Detailed assignments")
    print(f"2. optimal_assignments_summary.csv - Summary metrics")
    
    print(f"\nCOMPARISON COMPLETE!")

if __name__ == "__main__":
    main()
