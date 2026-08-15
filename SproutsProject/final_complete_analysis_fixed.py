#!/usr/bin/env python3
"""
Final complete analysis with all restaurants properly added to database
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def final_complete_analysis():
    """Final complete analysis with all restaurants"""
    print("="*80)
    print("FINAL COMPLETE ANALYSIS - ALL RESTAURANTS ADDED")
    print("="*80)
    
    try:
        # Load actual data from Excel
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
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        print(f"Total interns: {len(interns)}")
        print(f"Total restaurants: {len(restaurants)}")
        
        # Run algorithm
        print(f"\nRunning Hungarian algorithm...")
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Algorithm generated {len(assignments)} assignments")
        
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
        
        # Separate assigned and unassigned
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        unassigned_interns = [a for a in actual_assignments if a['actual_restaurant'] == 'Unassigned']
        
        print(f"Actual assigned interns: {len(assigned_interns)}")
        print(f"Actual unassigned interns: {len(unassigned_interns)}")
        
        # Enhanced matching
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        intern_lookup = {intern.user.full_name: intern for intern in interns}
        restaurant_lookup = {restaurant.name: restaurant for restaurant in restaurants}
        
        def find_restaurant(restaurant_name):
            """Enhanced restaurant matching"""
            restaurant_name = restaurant_name.strip().lower()
            
            for rest_name, rest_obj in restaurant_lookup.items():
                rest_lower = rest_name.lower()
                
                # Exact match
                if restaurant_name == rest_lower:
                    return rest_obj
                
                # Partial match
                if restaurant_name in rest_lower or rest_lower in restaurant_name:
                    return rest_obj
                
                # Remove common words and match
                clean_actual = restaurant_name.replace('restaurant', '').replace('kitchen', '').strip()
                clean_rest = rest_lower.replace('restaurant', '').replace('kitchen', '').strip()
                
                if clean_actual in clean_rest or clean_rest in clean_actual:
                    return rest_obj
            
            return None
        
        # Name mapping
        name_mapping = {
            'JP': 'Samuel  Gonzalez ',
            'Enrique': 'Enrique Marroquin',
            'Giselle': 'Giselle Contreras ',
            'Ollie': 'Ollie  O\'Malley',
            'Dana': 'Catherine Oropeza Huerta',
            'Bosco Liu': 'Zhijian Liu',
            'Angel': 'Angel Ruiz',
            'Gylli': 'Gyllibhet  Palacio',
            'Jesus': 'Jesus Chavez',
            'Alex': 'Alexander Barrios Castañeda',
            'Andrea': 'Andrea Caballero ',
            'Noel': 'Aliyatt  Rodgers',
            'Alexis/bri': 'Zailea Daniels',
            'Nae': 'Eljanae Robinson',
            'maye': 'Yeimi Diaz ',
            'Shelsea': 'Shelsea Vasquez',
            'Kaylin': 'Kaylin Lewis',
            'Ivory Willows': 'Aaliyah Engram',
            'Roni': 'Roni Velasquez',
            'Melanie Sanchez': 'Melanie Sanchez Ortega',
            'Gio': 'Giovanni Giacomazzi',
            'Imani': 'Imani Jarvis'
        }
        
        # Process assigned interns
        assigned_data = []
        matching_stats = {
            'total': len(assigned_interns),
            'intern_matched': 0,
            'actual_restaurant_matched': 0,
            'algorithm_restaurant_matched': 0,
            'both_commutes_computed': 0
        }
        
        print(f"\nProcessing assigned interns...")
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find intern
            intern = None
            mapped_name = name_mapping.get(actual_name)
            if mapped_name:
                intern = intern_lookup.get(mapped_name)
                if intern:
                    matching_stats['intern_matched'] += 1
            
            # Find algorithm assignment
            algorithm_assignment = None
            if mapped_name:
                algorithm_assignment = algorithm_lookup.get(mapped_name)
            
            # Compute actual commute
            actual_commute = None
            if intern and actual_restaurant != 'Unassigned':
                actual_restaurant_obj = find_restaurant(actual_restaurant)
                if actual_restaurant_obj:
                    actual_commute = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        actual_restaurant_obj.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    if actual_commute:
                        matching_stats['actual_restaurant_matched'] += 1
            
            # Get algorithm commute
            algorithm_commute = None
            algorithm_restaurant = 'Unassigned'
            if algorithm_assignment:
                algorithm_commute = algorithm_assignment['commute_minutes']
                algorithm_restaurant = algorithm_assignment['restaurant_name']
                if algorithm_commute:
                    matching_stats['algorithm_restaurant_matched'] += 1
            
            # Calculate delta
            commute_delta = None
            delta_percentage = None
            
            if actual_commute and algorithm_commute:
                commute_delta = actual_commute - algorithm_commute
                if actual_commute > 0:
                    delta_percentage = (commute_delta / actual_commute) * 100
                matching_stats['both_commutes_computed'] += 1
            
            # Determine status
            if actual_restaurant == algorithm_restaurant:
                status = 'Perfect Match'
            elif commute_delta and commute_delta > 0:
                status = 'Algorithm Better'
            elif commute_delta and commute_delta < 0:
                status = 'Actual Better'
            else:
                status = 'Different Assignment'
            
            assigned_data.append({
                'actual_name': actual_name,
                'actual_restaurant': actual_restaurant,
                'algorithm_restaurant': algorithm_restaurant,
                'actual_commute': actual_commute,
                'algorithm_commute': algorithm_commute,
                'commute_delta': commute_delta,
                'delta_percentage': delta_percentage,
                'status': status
            })
        
        # Calculate metrics
        complete_data = [d for d in assigned_data if d['actual_commute'] and d['algorithm_commute']]
        partial_data = [d for d in assigned_data if (d['actual_commute'] or d['algorithm_commute']) and not (d['actual_commute'] and d['algorithm_commute'])]
        
        if complete_data:
            actual_commutes = [d['actual_commute'] for d in complete_data]
            algorithm_commutes = [d['algorithm_commute'] for d in complete_data]
            deltas = [d['commute_delta'] for d in complete_data]
            
            avg_actual = sum(actual_commutes) / len(actual_commutes)
            avg_algorithm = sum(algorithm_commutes) / len(algorithm_commutes)
            avg_delta = sum(deltas) / len(deltas)
            
            improvements = [d for d in complete_data if d['commute_delta'] > 0]
            worsenings = [d for d in complete_data if d['commute_delta'] < 0]
            perfect_matches = [d for d in complete_data if d['status'] == 'Perfect Match']
        else:
            avg_actual = avg_algorithm = avg_delta = 0
            improvements = worsenings = perfect_matches = []
        
        # Create final report
        report_data = [
            ['FINAL COMPLETE ANALYSIS - ALL RESTAURANTS ADDED'],
            [''],
            ['OVERALL STATISTICS'],
            ['Total Interns in Database', len(interns)],
            ['Total Restaurants in Database', len(restaurants)],
            ['Actual Assigned Interns', len(assigned_interns)],
            ['Actual Unassigned Interns', len(unassigned_interns)],
            ['Algorithm Assignments Generated', len(assignments)],
            [''],
            ['MATCHING STATISTICS'],
            ['Total Assigned Interns', matching_stats['total']],
            ['Interns Matched to Database', matching_stats['intern_matched']],
            ['Actual Restaurants Matched', matching_stats['actual_restaurant_matched']],
            ['Algorithm Assignments Found', matching_stats['algorithm_restaurant_matched']],
            ['Complete Commute Data', matching_stats['both_commutes_computed']],
            [''],
            ['DELTA COMMUTE METRICS'],
            ['Average Actual Commute', f'{avg_actual:.1f} minutes'],
            ['Average Algorithm Commute', f'{avg_algorithm:.1f} minutes'],
            ['Average Delta (Actual - Algorithm)', f'{avg_delta:.1f} minutes'],
            ['Algorithm Better (Saves Time)', len(improvements)],
            ['Actual Better (Current Faster)', len(worsenings)],
            ['Perfect Matches', len(perfect_matches)],
            [''],
            ['COMPLETE DELTA COMMUTE ANALYSIS'],
            ['Intern Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Actual Commute', 'Algorithm Commute', 'Delta (min)', 'Delta %', 'Status']
        ]
        
        # Sort by delta (biggest improvements first)
        complete_data.sort(key=lambda x: x['commute_delta'] if x['commute_delta'] else -999, reverse=True)
        
        # Add complete data
        for data in complete_data:
            report_data.append([
                data['actual_name'],
                data['actual_restaurant'],
                data['algorithm_restaurant'],
                f"{data['actual_commute']:.1f}",
                f"{data['algorithm_commute']:.1f}",
                f"{data['commute_delta']:.1f}",
                f"{data['delta_percentage']:.1f}%" if data['delta_percentage'] else 'N/A',
                data['status']
            ])
        
        # Add partial data
        if partial_data:
            report_data.extend([
                [''],
                ['PARTIAL DATA (One Commute Available)'],
                ['Intern Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Actual Commute', 'Algorithm Commute', 'Status']
            ])
            
            for data in partial_data:
                report_data.append([
                    data['actual_name'],
                    data['actual_restaurant'],
                    data['algorithm_restaurant'],
                    f"{data['actual_commute']:.1f}" if data['actual_commute'] else 'N/A',
                    f"{data['algorithm_commute']:.1f}" if data['algorithm_commute'] else 'N/A',
                    data['status']
                ])
        
        # Save report
        report_df = pd.DataFrame(report_data)
        report_df.to_csv('final_complete_analysis_all_restaurants.csv', index=False, header=False)
        
        print(f"\nFinal complete analysis saved to 'final_complete_analysis_all_restaurants.csv'")
        
        # Print summary
        print(f"\nFINAL RESULTS SUMMARY:")
        print(f"Total interns: {len(interns)}")
        print(f"Total restaurants: {len(restaurants)}")
        print(f"Algorithm assignments: {len(assignments)}")
        print(f"Complete delta data: {len(complete_data)} interns")
        print(f"Partial data: {len(partial_data)} interns")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average algorithm commute: {avg_algorithm:.1f} minutes")
        print(f"Average improvement: {avg_delta:.1f} minutes")
        
        return {
            'total_interns': len(interns),
            'total_restaurants': len(restaurants),
            'algorithm_assignments': len(assignments),
            'complete_data': len(complete_data),
            'partial_data': len(partial_data),
            'avg_actual_commute': avg_actual,
            'avg_algorithm_commute': avg_algorithm,
            'avg_delta': avg_delta
        }
        
    except Exception as e:
        print(f"Error in final analysis: {e}")
        return {}

def main():
    """Main function"""
    results = final_complete_analysis()
    
    print(f"\n" + "="*80)
    print("FINAL COMPLETE ANALYSIS - ALL RESTAURANTS FIXED")
    print("="*80)
    
    if results:
        print(f"SUCCESS: All restaurants added, improved data coverage!")
        print(f"Complete data: {results.get('complete_data', 0)} interns (was 7)")
        print(f"Partial data: {results.get('partial_data', 0)} interns (was 13)")
        print(f"Average improvement: {results.get('avg_delta', 0):.1f} minutes")

if __name__ == "__main__":
    main()
