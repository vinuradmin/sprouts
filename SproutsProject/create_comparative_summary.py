#!/usr/bin/env python3
"""
Create comparative summary like fall_2025_final_summary.csv format
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def load_actual_fall_2025_data():
    """Load actual Fall 2025 data from Excel"""
    print("Loading actual Fall 2025 data...")
    
    try:
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        # Filter for Fall 2025 interns (rows 338-367)
        fall_2025_df = df.iloc[337:367].copy()
        
        # Extract relevant columns
        actual_data = []
        for idx, row in fall_2025_df.iterrows():
            intern_name = row.iloc[1]  # Name
            age = row.iloc[2]  # Age
            transportation = row.iloc[8] if pd.notna(row.iloc[8]) else 'Unknown'
            address = row.iloc[6] if pd.notna(row.iloc[6]) else 'Unknown'
            actual_restaurant = row.iloc[13] if pd.notna(row.iloc[13]) else 'Unassigned'
            
            actual_data.append({
                'intern_name': intern_name,
                'age': age,
                'transportation': transportation,
                'address': address,
                'actual_restaurant': actual_restaurant
            })
        
        print(f"Loaded {len(actual_data)} actual Fall 2025 assignments")
        return actual_data
        
    except Exception as e:
        print(f"Error loading actual data: {e}")
        return []

def get_algorithm_assignments():
    """Get assignments from our algorithm"""
    print("Getting algorithm assignments...")
    
    try:
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
        
        print(f"Generated {len(assignments)} algorithm assignments")
        return assignments
        
    except Exception as e:
        print(f"Error getting algorithm assignments: {e}")
        return []

def calculate_commute_times(actual_data, algorithm_assignments):
    """Calculate commute times for both actual and algorithm assignments"""
    print("Calculating commute times...")
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        # Create lookup dictionaries
        intern_lookup = {intern.user.full_name: intern for intern in interns}
        restaurant_lookup = {restaurant.name: restaurant for restaurant in restaurants}
        algorithm_lookup = {assign['intern_name']: assign for assign in algorithm_assignments}
        
        comparative_data = []
        
        for actual in actual_data:
            intern_name = actual['intern_name']
            
            if intern_name not in intern_lookup:
                continue
                
            intern = intern_lookup[intern_name]
            actual_restaurant = actual['actual_restaurant']
            
            # Get algorithm assignment
            algorithm_assignment = algorithm_lookup.get(intern_name, {})
            algorithm_restaurant = algorithm_assignment.get('restaurant_name', 'Unassigned')
            algorithm_commute = algorithm_assignment.get('commute_minutes', None)
            
            # Calculate actual commute
            actual_commute = None
            if actual_restaurant in restaurant_lookup:
                actual_restaurant_obj = restaurant_lookup[actual_restaurant]
                actual_commute = optimizer.get_optimal_commute(
                    intern.get_full_address(),
                    actual_restaurant_obj.get_full_address(),
                    intern.transportation_method or 'driving'
                )
            
            # Determine if assignment changed
            assignment_changed = actual_restaurant != algorithm_restaurant
            
            # Calculate improvement
            commute_improvement = None
            if actual_commute and algorithm_commute:
                commute_improvement = actual_commute - algorithm_commute
            
            # Get transportation options
            transport_options = optimizer.parse_transportation_options(intern.transportation_method or 'driving')
            
            comparative_data.append({
                'Intern Name': intern_name,
                'Age': actual['age'],
                'Transportation Options': actual['transportation'],
                'Actual Restaurant': actual_restaurant,
                'Algorithm Restaurant': algorithm_restaurant,
                'Assignment Changed': 'Yes' if assignment_changed else 'No',
                'Actual Commute (min)': actual_commute,
                'Algorithm Commute (min)': algorithm_commute,
                'Commute Improvement': commute_improvement,
                'Parsed Transport Options': ', '.join(transport_options),
                'Algorithm Hours': algorithm_assignment.get('total_overlap_hours', None),
                'Algorithm Days': algorithm_assignment.get('days_matched', None)
            })
        
        print(f"Processed {len(comparative_data)} comparative records")
        return comparative_data
        
    except Exception as e:
        print(f"Error calculating commute times: {e}")
        return []

def create_comparative_summary(comparative_data):
    """Create comparative summary in CSV format"""
    print("Creating comparative summary...")
    
    try:
        # Create DataFrame
        df = pd.DataFrame(comparative_data)
        
        # Sort by intern name
        df = df.sort_values('Intern Name')
        
        # Save to CSV
        df.to_csv('fall_2025_vs_algorithm_comparative_summary.csv', index=False)
        print(f"Comparative summary saved to 'fall_2025_vs_algorithm_comparative_summary.csv'")
        
        # Calculate summary statistics
        summary_stats = {
            'Total Interns': len(df),
            'Valid Actual Commutes': df['Actual Commute (min)'].notna().sum(),
            'Valid Algorithm Commutes': df['Algorithm Commute (min)'].notna().sum(),
            'Assignments Changed': df[df['Assignment Changed'] == 'Yes'].shape[0],
            'Average Actual Commute': df['Actual Commute (min)'].mean(),
            'Average Algorithm Commute': df['Algorithm Commute (min)'].mean(),
            'Average Commute Improvement': df['Commute Improvement'].mean(),
            'Max Commute Improvement': df['Commute Improvement'].max(),
            'Min Commute Improvement': df['Commute Improvement'].min()
        }
        
        return df, summary_stats
        
    except Exception as e:
        print(f"Error creating comparative summary: {e}")
        return None, None

def print_comparative_analysis(df, summary_stats):
    """Print comparative analysis"""
    print("\n" + "="*80)
    print("FALL 2025 vs ALGORITHM COMPARATIVE ANALYSIS")
    print("="*80)
    
    if summary_stats:
        print(f"\nSUMMARY STATISTICS:")
        print(f"Total Interns: {summary_stats['Total Interns']}")
        print(f"Valid Actual Commutes: {summary_stats['Valid Actual Commutes']}")
        print(f"Valid Algorithm Commutes: {summary_stats['Valid Algorithm Commutes']}")
        print(f"Assignments Changed: {summary_stats['Assignments Changed']}")
        print(f"Average Actual Commute: {summary_stats['Average Actual Commute']:.1f} minutes")
        print(f"Average Algorithm Commute: {summary_stats['Average Algorithm Commute']:.1f} minutes")
        print(f"Average Commute Improvement: {summary_stats['Average Commute Improvement']:.1f} minutes")
        print(f"Max Commute Improvement: {summary_stats['Max Commute Improvement']:.1f} minutes")
        print(f"Min Commute Improvement: {summary_stats['Min Commute Improvement']:.1f} minutes")
    
    if df is not None:
        print(f"\nASSIGNMENT CHANGES:")
        changed = df[df['Assignment Changed'] == 'Yes']
        unchanged = df[df['Assignment Changed'] == 'No']
        
        print(f"\nChanged Assignments ({len(changed)}):")
        for _, row in changed.iterrows():
            actual_commute = row['Actual Commute (min)']
            algo_commute = row['Algorithm Commute (min)']
            improvement = row['Commute Improvement']
            
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} -> {row['Algorithm Restaurant']}")
            print(f"    Commute: {actual_commute} -> {algo_commute} min (Improvement: {improvement:+.1f} min)")
        
        print(f"\nUnchanged Assignments ({len(unchanged)}):")
        for _, row in unchanged.iterrows():
            print(f"  {row['Intern Name']}: {row['Actual Restaurant']} (same)")
        
        print(f"\nTOP COMMUTE IMPROVEMENTS:")
        valid_improvements = df[df['Commute Improvement'].notna()]
        if not valid_improvements.empty:
            top_improvements = valid_improvements.nlargest(5, 'Commute Improvement')
            for _, row in top_improvements.iterrows():
                print(f"  {row['Intern Name']}: {row['Commute Improvement']:+.1f} min improvement")
        
        print(f"\nCOMMUTE DISTRIBUTION COMPARISON:")
        if summary_stats['Valid Actual Commutes'] > 0 and summary_stats['Valid Algorithm Commutes'] > 0:
            print(f"Actual Commute Distribution:")
            actual_commutes = df['Actual Commute (min)'].dropna()
            print(f"  Mean: {actual_commutes.mean():.1f} min")
            print(f"  Range: {actual_commutes.min():.0f}-{actual_commutes.max():.0f} min")
            
            print(f"Algorithm Commute Distribution:")
            algo_commutes = df['Algorithm Commute (min)'].dropna()
            print(f"  Mean: {algo_commutes.mean():.1f} min")
            print(f"  Range: {algo_commutes.min():.0f}-{algo_commutes.max():.0f} min")

def main():
    """Main function"""
    print("="*80)
    print("FALL 2025 vs ALGORITHM COMPARATIVE SUMMARY GENERATOR")
    print("Similar format to fall_2025_final_summary.csv")
    print("="*80)
    
    # Load data
    actual_data = load_actual_fall_2025_data()
    algorithm_assignments = get_algorithm_assignments()
    
    # Calculate commute times
    comparative_data = calculate_commute_times(actual_data, algorithm_assignments)
    
    # Create comparative summary
    df, summary_stats = create_comparative_summary(comparative_data)
    
    # Print analysis
    print_comparative_analysis(df, summary_stats)
    
    print(f"\nFILES CREATED:")
    print(f"1. fall_2025_vs_algorithm_comparative_summary.csv - Main comparison")
    
    print(f"\nCOMPARATIVE SUMMARY COMPLETE!")

if __name__ == "__main__":
    main()
