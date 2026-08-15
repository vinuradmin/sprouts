#!/usr/bin/env python3
"""
Comprehensive comparison sheet: Actual vs Optimal assignments with key metrics
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def load_actual_assignments():
    """Load actual Fall 2025 assignments"""
    print("Loading actual Fall 2025 assignments...")
    
    try:
        # Load the Excel file
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        # Filter for Fall 2025 interns (rows 338-367)
        fall_2025_df = df.iloc[337:367].copy()  # 0-indexed, so 337-366
        
        # Extract actual assignments (column 14, 0-indexed = 13)
        actual_assignments = []
        
        for idx, row in fall_2025_df.iterrows():
            if pd.notna(row.iloc[13]):  # Check if assignment exists
                intern_name = row.iloc[1]  # Name column
                actual_restaurant = row.iloc[13]  # Assignment column
                transportation = row.iloc[8] if pd.notna(row.iloc[8]) else 'Unknown'
                address = row.iloc[6] if pd.notna(row.iloc[6]) else 'Unknown'
                
                actual_assignments.append({
                    'intern_name': intern_name,
                    'actual_restaurant': actual_restaurant,
                    'transportation': transportation,
                    'address': address
                })
        
        print(f"Loaded {len(actual_assignments)} actual assignments")
        return actual_assignments
        
    except Exception as e:
        print(f"Error loading actual assignments: {e}")
        return []

def get_optimal_assignments():
    """Get optimal assignments from Hungarian algorithm"""
    print("Getting optimal assignments from Hungarian algorithm...")
    
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
        
        print(f"Generated {len(assignments)} optimal assignments")
        return assignments
        
    except Exception as e:
        print(f"Error getting optimal assignments: {e}")
        return []

def calculate_commute_metrics(actual_assignments, optimal_assignments):
    """Calculate commute metrics for both assignment types"""
    print("Calculating commute metrics...")
    
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
        
        # Calculate actual assignment metrics
        actual_metrics = []
        for assignment in actual_assignments:
            intern_name = assignment['intern_name']
            actual_restaurant = assignment['actual_restaurant']
            
            if intern_name in intern_lookup and actual_restaurant in restaurant_lookup:
                intern = intern_lookup[intern_name]
                restaurant = restaurant_lookup[actual_restaurant]
                
                # Get optimal commute for actual assignment
                optimal_commute = optimizer.get_optimal_commute(
                    intern.get_full_address(),
                    restaurant.get_full_address(),
                    intern.transportation_method or 'driving'
                )
                
                # Get transportation comparison
                comparison = optimizer.get_transportation_comparison(
                    intern.get_full_address(),
                    restaurant.get_full_address(),
                    intern.transportation_method or 'driving'
                )
                
                actual_metrics.append({
                    'intern_name': intern_name,
                    'restaurant': actual_restaurant,
                    'optimal_commute': optimal_commute,
                    'transportation_options': comparison,
                    'transportation_method': intern.transportation_method
                })
        
        # Optimal assignments already have commute metrics
        optimal_metrics = []
        for assignment in optimal_assignments:
            optimal_metrics.append({
                'intern_name': assignment['intern_name'],
                'restaurant': assignment['restaurant_name'],
                'optimal_commute': assignment['commute_minutes'],
                'total_hours': assignment['total_overlap_hours'],
                'days_matched': assignment['days_matched']
            })
        
        return actual_metrics, optimal_metrics
        
    except Exception as e:
        print(f"Error calculating commute metrics: {e}")
        return [], []

def create_comparison_sheet(actual_assignments, optimal_assignments, actual_metrics, optimal_metrics):
    """Create comprehensive comparison sheet"""
    print("Creating comprehensive comparison sheet...")
    
    try:
        # Create comparison data
        comparison_data = []
        
        # Create lookup for optimal assignments
        optimal_lookup = {opt['intern_name']: opt for opt in optimal_metrics}
        
        # Process each actual assignment
        for actual in actual_metrics:
            intern_name = actual['intern_name']
            actual_restaurant = actual['restaurant']
            actual_commute = actual['optimal_commute']
            
            # Find corresponding optimal assignment
            optimal = optimal_lookup.get(intern_name, {})
            optimal_restaurant = optimal.get('restaurant', 'Unassigned')
            optimal_commute = optimal.get('optimal_commute', None)
            optimal_hours = optimal.get('total_hours', None)
            optimal_days = optimal.get('days_matched', None)
            
            # Calculate improvement
            if actual_commute and optimal_commute:
                improvement = actual_commute - optimal_commute
                improvement_pct = (improvement / actual_commute * 100) if actual_commute > 0 else 0
            else:
                improvement = None
                improvement_pct = None
            
            # Determine transportation optimization benefit
            transport_options = actual.get('transportation_options', {})
            if transport_options:
                min_commute = min([v for v in transport_options.values() if v is not None])
                max_commute = max([v for v in transport_options.values() if v is not None])
                transport_range = max_commute - min_commute
            else:
                min_commute = None
                max_commute = None
                transport_range = None
            
            comparison_data.append({
                'Intern Name': intern_name,
                'Actual Restaurant': actual_restaurant,
                'Optimal Restaurant': optimal_restaurant,
                'Actual Commute (min)': actual_commute,
                'Optimal Commute (min)': optimal_commute,
                'Commute Improvement': improvement,
                'Improvement %': improvement_pct,
                'Transportation Options': actual.get('transportation_method', 'Unknown'),
                'Min Transport Commute': min_commute,
                'Max Transport Commute': max_commute,
                'Transport Range': transport_range,
                'Optimal Hours': optimal_hours,
                'Optimal Days': optimal_days,
                'Assignment Changed': 'Yes' if actual_restaurant != optimal_restaurant else 'No'
            })
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Save to CSV
        df.to_csv('actual_vs_optimal_comparison.csv', index=False)
        print(f"Comparison sheet saved to 'actual_vs_optimal_comparison.csv'")
        
        return df
        
    except Exception as e:
        print(f"Error creating comparison sheet: {e}")
        return None

def calculate_summary_metrics(df):
    """Calculate summary metrics"""
    print("Calculating summary metrics...")
    
    if df is None or df.empty:
        return
    
    try:
        # Filter out rows with missing commute data
        valid_commutes = df.dropna(subset=['Actual Commute (min)', 'Optimal Commute (min)'])
        
        # Calculate averages
        avg_actual_commute = valid_commutes['Actual Commute (min)'].mean()
        avg_optimal_commute = valid_commutes['Optimal Commute (min)'].mean()
        avg_improvement = valid_commutes['Commute Improvement'].mean()
        
        # Calculate ranges
        actual_range = valid_commutes['Actual Commute (min)'].max() - valid_commutes['Actual Commute (min)'].min()
        optimal_range = valid_commutes['Optimal Commute (min)'].max() - valid_commutes['Optimal Commute (min)'].min()
        
        # Count assignments changed
        assignments_changed = df[df['Assignment Changed'] == 'Yes'].shape[0]
        total_assignments = df.shape[0]
        
        # Transportation optimization impact
        valid_transport = df.dropna(subset=['Transport Range'])
        avg_transport_range = valid_transport['Transport Range'].mean()
        
        # Create summary
        summary = {
            'Total Interns': total_assignments,
            'Valid Commute Data': len(valid_commutes),
            'Average Actual Commute': avg_actual_commute,
            'Average Optimal Commute': avg_optimal_commute,
            'Average Improvement': avg_improvement,
            'Actual Commute Range': actual_range,
            'Optimal Commute Range': optimal_range,
            'Assignments Changed': assignments_changed,
            'Assignment Change Rate': assignments_changed / total_assignments * 100,
            'Average Transport Range': avg_transport_range,
            'Transport Optimization Impact': 'High' if avg_transport_range > 10 else 'Medium' if avg_transport_range > 5 else 'Low'
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('comparison_summary_metrics.csv', index=False)
        
        return summary
        
    except Exception as e:
        print(f"Error calculating summary metrics: {e}")
        return None

def print_detailed_summary(summary):
    """Print detailed summary"""
    print("\n" + "="*80)
    print("COMPREHENSIVE COMPARISON SUMMARY")
    print("="*80)
    
    if not summary:
        print("No summary data available")
        return
    
    print(f"\n📊 OVERALL METRICS:")
    print(f"Total Interns: {summary['Total Interns']}")
    print(f"Valid Commute Data: {summary['Valid Commute Data']}")
    print(f"Assignments Changed: {summary['Assignments Changed']} ({summary['Assignment Change Rate']:.1f}%)")
    
    print(f"\n🚗 COMMUTE METRICS:")
    print(f"Average Actual Commute: {summary['Average Actual Commute']:.1f} minutes")
    print(f"Average Optimal Commute: {summary['Average Optimal Commute']:.1f} minutes")
    print(f"Average Improvement: {summary['Average Improvement']:.1f} minutes")
    
    if summary['Average Improvement'] > 0:
        improvement_pct = (summary['Average Improvement'] / summary['Average Actual Commute'] * 100)
        print(f"Overall Improvement: {improvement_pct:.1f}%")
    
    print(f"\n📈 RANGE ANALYSIS:")
    print(f"Actual Commute Range: {summary['Actual Commute Range']:.1f} minutes")
    print(f"Optimal Commute Range: {summary['Optimal Commute Range']:.1f} minutes")
    
    print(f"\n🎯 TRANSPORTATION OPTIMIZATION:")
    print(f"Average Transport Range: {summary['Average Transport Range']:.1f} minutes")
    print(f"Transport Optimization Impact: {summary['Transport Optimization Impact']}")
    
    print(f"\n🏆 KEY INSIGHTS:")
    
    if summary['Average Improvement'] > 5:
        print(f"✅ Significant commute improvement achieved")
    elif summary['Average Improvement'] > 0:
        print(f"✅ Moderate commute improvement achieved")
    else:
        print(f"⚠️  No significant commute improvement")
    
    if summary['Assignment Change Rate'] > 50:
        print(f"✅ Major reassignment of interns")
    elif summary['Assignment Change Rate'] > 20:
        print(f"✅ Moderate reassignment of interns")
    else:
        print(f"ℹ️  Minimal reassignment changes")
    
    if summary['Transport Optimization Impact'] == 'High':
        print(f"✅ Transportation optimization provides significant benefits")
    elif summary['Transport Optimization Impact'] == 'Medium':
        print(f"✅ Transportation optimization provides moderate benefits")
    else:
        print(f"ℹ️  Transportation optimization provides limited benefits")

def main():
    """Main function"""
    print("="*80)
    print("COMPREHENSIVE COMPARISON SHEET GENERATOR")
    print("Actual vs Optimal Assignments with Key Metrics")
    print("="*80)
    
    # Load data
    actual_assignments = load_actual_assignments()
    optimal_assignments = get_optimal_assignments()
    
    # Calculate metrics
    actual_metrics, optimal_metrics = calculate_commute_metrics(actual_assignments, optimal_assignments)
    
    # Create comparison sheet
    df = create_comparison_sheet(actual_assignments, optimal_assignments, actual_metrics, optimal_metrics)
    
    # Calculate summary
    summary = calculate_summary_metrics(df)
    
    # Print summary
    print_detailed_summary(summary)
    
    print(f"\n📁 FILES CREATED:")
    print(f"1. actual_vs_optimal_comparison.csv - Detailed comparison")
    print(f"2. comparison_summary_metrics.csv - Summary metrics")
    
    print(f"\n🎯 COMPARISON COMPLETE!")
    print(f"The comprehensive comparison sheet has been generated with key metrics.")

if __name__ == "__main__":
    main()
