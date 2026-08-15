#!/usr/bin/env python3
"""
Compute actual commute times for current assignments to compare with optimal
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def compute_actual_commutes():
    """Compute actual commute times for current assignments"""
    print("="*80)
    print("COMPUTING ACTUAL COMMUTE TIMES")
    print("For comparison with optimal algorithm assignments")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Get algorithm assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        optimizer = TransportationOptimizer()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        # Create lookup dictionaries
        intern_lookup = {intern.user.full_name: intern for intern in interns}
        restaurant_lookup = {restaurant.name: restaurant for restaurant in restaurants}
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Extract actual assignments and compute commutes
        actual_commute_data = []
        comparison_data = []
        
        print("Computing actual commute times...")
        
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                if actual_restaurant == 'nan' or actual_restaurant == '':
                    actual_restaurant = 'Unassigned'
                
                # Find matching intern and algorithm assignment
                intern = None
                algorithm_assignment = None
                
                # Try exact match first
                if actual_name in intern_lookup:
                    intern = intern_lookup[actual_name]
                    algorithm_assignment = algorithm_lookup.get(actual_name)
                
                # Try partial match if exact fails
                if not intern:
                    for intern_name, intern_obj in intern_lookup.items():
                        algo_lower = intern_name.strip().lower()
                        actual_lower = actual_name.strip().lower()
                        
                        if (actual_lower in algo_lower or algo_lower in actual_lower or
                            actual_lower.replace(' ', '') in algo_lower.replace(' ', '') or
                            algo_lower.replace(' ', '') in actual_lower.replace(' ', '')):
                            intern = intern_obj
                            algorithm_assignment = algorithm_lookup.get(intern_name)
                            break
                
                if intern and actual_restaurant != 'Unassigned':
                    # Find actual restaurant object
                    actual_restaurant_obj = None
                    for rest_name, rest_obj in restaurant_lookup.items():
                        if actual_restaurant.lower() in rest_name.lower() or rest_name.lower() in actual_restaurant.lower():
                            actual_restaurant_obj = rest_obj
                            break
                    
                    if actual_restaurant_obj:
                        # Compute actual commute
                        actual_commute = optimizer.get_optimal_commute(
                            intern.get_full_address(),
                            actual_restaurant_obj.get_full_address(),
                            intern.transportation_method or 'driving'
                        )
                        
                        # Get algorithm assignment data
                        algorithm_restaurant = algorithm_assignment['restaurant_name'] if algorithm_assignment else 'Unassigned'
                        algorithm_commute = algorithm_assignment['commute_minutes'] if algorithm_assignment else None
                        
                        # Calculate improvement
                        commute_improvement = None
                        improvement_percentage = None
                        
                        if actual_commute and algorithm_commute:
                            commute_improvement = actual_commute - algorithm_commute
                            if actual_commute > 0:
                                improvement_percentage = (commute_improvement / actual_commute) * 100
                        
                        # Determine status
                        if actual_restaurant == algorithm_restaurant:
                            status = 'Perfect Match'
                        elif commute_improvement and commute_improvement > 0:
                            status = 'Improvement Opportunity'
                        else:
                            status = 'Different Assignment'
                        
                        actual_commute_data.append({
                            'intern_name': actual_name,
                            'actual_restaurant': actual_restaurant,
                            'algorithm_restaurant': algorithm_restaurant,
                            'actual_commute': actual_commute,
                            'algorithm_commute': algorithm_commute,
                            'commute_improvement': commute_improvement,
                            'improvement_percentage': improvement_percentage,
                            'status': status
                        })
                        
                        comparison_data.append({
                            'Intern Name': actual_name,
                            'Actual Restaurant': actual_restaurant,
                            'Optimal Restaurant': algorithm_restaurant,
                            'Actual Commute (minutes)': actual_commute,
                            'Optimal Commute (minutes)': algorithm_commute,
                            'Commute Improvement': commute_improvement,
                            'Improvement %': improvement_percentage,
                            'Status': status
                        })
        
        print(f"Computed actual commutes for {len(actual_commute_data)} interns")
        
        # Calculate summary statistics
        if actual_commute_data:
            actual_commutes = [d['actual_commute'] for d in actual_commute_data if d['actual_commute']]
            algorithm_commutes = [d['algorithm_commute'] for d in actual_commute_data if d['algorithm_commute']]
            improvements = [d['commute_improvement'] for d in actual_commute_data if d['commute_improvement']]
            
            avg_actual_commute = sum(actual_commutes) / len(actual_commutes) if actual_commutes else 0
            avg_algorithm_commute = sum(algorithm_commutes) / len(algorithm_commutes) if algorithm_commutes else 0
            avg_improvement = sum(improvements) / len(improvements) if improvements else 0
            
            perfect_matches = len([d for d in actual_commute_data if d['status'] == 'Perfect Match'])
            improvement_opportunities = len([d for d in actual_commute_data if d['status'] == 'Improvement Opportunity'])
        else:
            avg_actual_commute = avg_algorithm_commute = avg_improvement = 0
            perfect_matches = improvement_opportunities = 0
        
        # Create comprehensive summary
        summary_data = [
            ['Fall 2025 vs Algorithm Commute Comparison'],
            [''],
            ['KEY METRICS'],
            ['Total Interns Analyzed', len(actual_commute_data)],
            ['Perfect Matches', perfect_matches],
            ['Improvement Opportunities', improvement_opportunities],
            ['Actual Commutes Available', len(actual_commutes)],
            ['Optimal Commutes Available', len(algorithm_commutes)],
            [''],
            ['COMMUTE COMPARISON'],
            ['Average Actual Commute (minutes)', f'{avg_actual_commute:.1f}'],
            ['Average Optimal Commute (minutes)', f'{avg_algorithm_commute:.1f}'],
            ['Average Improvement', f'{avg_improvement:.1f} minutes'],
            [''],
            ['PERFECT MATCHES (Current placements are optimal)'],
            ['Intern Name', 'Restaurant', 'Actual Commute', 'Optimal Commute']
        ]
        
        # Add perfect matches
        for data in actual_commute_data:
            if data['status'] == 'Perfect Match':
                summary_data.append([
                    data['intern_name'],
                    data['actual_restaurant'],
                    f"{data['actual_commute']:.1f}",
                    f"{data['algorithm_commute']:.1f}"
                ])
        
        # Add top improvements
        summary_data.extend([
            [''],
            ['TOP COMMUTE IMPROVEMENTS'],
            ['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Actual', 'Optimal', 'Improvement']
        ])
        
        # Sort by improvement amount
        improvement_data = [d for d in actual_commute_data if d['commute_improvement'] and d['commute_improvement'] > 0]
        improvement_data.sort(key=lambda x: x['commute_improvement'], reverse=True)
        
        for data in improvement_data[:10]:
            summary_data.append([
                data['intern_name'],
                data['actual_restaurant'],
                data['algorithm_restaurant'],
                f"{data['actual_commute']:.1f}",
                f"{data['algorithm_commute']:.1f}",
                f"{data['commute_improvement']:.1f}"
            ])
        
        # Add complete comparison
        summary_data.extend([
            [''],
            ['COMPLETE COMMUTE COMPARISON'],
            ['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Actual Commute', 'Optimal Commute', 'Improvement', 'Status']
        ])
        
        for data in actual_commute_data:
            summary_data.append([
                data['intern_name'],
                data['actual_restaurant'],
                data['algorithm_restaurant'],
                f"{data['actual_commute']:.1f}" if data['actual_commute'] else 'N/A',
                f"{data['algorithm_commute']:.1f}" if data['algorithm_commute'] else 'N/A',
                f"{data['commute_improvement']:.1f}" if data['commute_improvement'] else 'N/A',
                data['status']
            ])
        
        # Save summary
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('fall_2025_commute_comparison_summary.csv', index=False, header=False)
        
        # Save detailed comparison
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv('detailed_commute_comparison.csv', index=False)
        
        print(f"Commute comparison summary saved to 'fall_2025_commute_comparison_summary.csv'")
        print(f"Detailed comparison saved to 'detailed_commute_comparison.csv'")
        
        # Print summary
        print(f"\nFALL 2025 COMMUTE COMPARISON SUMMARY")
        print(f"=" * 60)
        print(f"\nKEY METRICS")
        print(f"Total Interns Analyzed: {len(actual_commute_data)}")
        print(f"Perfect Matches: {perfect_matches}")
        print(f"Improvement Opportunities: {improvement_opportunities}")
        print(f"Average Actual Commute: {avg_actual_commute:.1f} minutes")
        print(f"Average Optimal Commute: {avg_algorithm_commute:.1f} minutes")
        print(f"Average Improvement: {avg_improvement:.1f} minutes")
        
        if improvement_data:
            print(f"\nTOP 5 COMMUTE IMPROVEMENTS")
            for data in improvement_data[:5]:
                print(f"{data['intern_name']}: {data['actual_commute']:.1f} → {data['algorithm_commute']:.1f} min (improvement: {data['commute_improvement']:.1f} min)")
        
        return summary_df, comparison_df, {
            'total_interns': len(actual_commute_data),
            'perfect_matches': perfect_matches,
            'improvement_opportunities': improvement_opportunities,
            'avg_actual_commute': avg_actual_commute,
            'avg_algorithm_commute': avg_algorithm_commute,
            'avg_improvement': avg_improvement
        }
        
    except Exception as e:
        print(f"Error computing actual commutes: {e}")
        return None, None, None

def main():
    """Main function"""
    summary_df, comparison_df, metrics = compute_actual_commutes()
    
    if summary_df is not None:
        print(f"\nFILES CREATED:")
        print(f"1. fall_2025_commute_comparison_summary.csv - Commute comparison summary")
        print(f"2. detailed_commute_comparison.csv - Detailed comparison data")
        
        print(f"\nACTUAL COMMUTE COMPUTATION COMPLETE!")
    else:
        print(f"Error computing actual commutes")

if __name__ == "__main__":
    main()
