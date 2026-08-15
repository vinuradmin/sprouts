#!/usr/bin/env python3
"""
Delta commute analysis: Actual vs Algorithm-suggested commute times
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def delta_commute_analysis():
    """Create delta commute analysis showing actual vs algorithm commutes"""
    print("="*80)
    print("DELTA COMMUTE ANALYSIS")
    print("Actual Commute vs Algorithm-Suggested Commute")
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
        
        # Filter to only assigned interns
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        
        # Create lookups
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        intern_lookup = {intern.user.full_name: intern for intern in interns}
        restaurant_lookup = {restaurant.name: restaurant for restaurant in restaurants}
        
        # Enhanced name mapping
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
        
        print(f"Computing delta commute analysis for {len(assigned_interns)} interns...")
        
        delta_data = []
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find matching intern and algorithm assignment
            intern = None
            algorithm_assignment = None
            
            # Try name mapping
            mapped_name = name_mapping.get(actual_name)
            if mapped_name:
                intern = intern_lookup.get(mapped_name)
                algorithm_assignment = algorithm_lookup.get(mapped_name)
            
            # Compute actual commute
            actual_commute = None
            if intern and actual_restaurant != 'Unassigned':
                # Find actual restaurant
                actual_restaurant_obj = None
                for rest_name, rest_obj in restaurant_lookup.items():
                    if actual_restaurant.lower() in rest_name.lower() or rest_name.lower() in actual_restaurant.lower():
                        actual_restaurant_obj = rest_obj
                        break
                
                if actual_restaurant_obj:
                    actual_commute = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        actual_restaurant_obj.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
            
            # Get algorithm commute
            algorithm_commute = algorithm_assignment['commute_minutes'] if algorithm_assignment else None
            algorithm_restaurant = algorithm_assignment['restaurant_name'] if algorithm_assignment else 'Unassigned'
            
            # Calculate delta
            commute_delta = None
            delta_percentage = None
            
            if actual_commute and algorithm_commute:
                commute_delta = actual_commute - algorithm_commute
                if actual_commute > 0:
                    delta_percentage = (commute_delta / actual_commute) * 100
            
            # Determine status
            if actual_restaurant == algorithm_restaurant:
                status = 'Perfect Match'
            elif commute_delta and commute_delta > 0:
                status = 'Algorithm Better'
            elif commute_delta and commute_delta < 0:
                status = 'Actual Better'
            else:
                status = 'Different Assignment'
            
            delta_data.append({
                'actual_name': actual_name,
                'actual_restaurant': actual_restaurant,
                'algorithm_restaurant': algorithm_restaurant,
                'actual_commute': actual_commute,
                'algorithm_commute': algorithm_commute,
                'commute_delta': commute_delta,
                'delta_percentage': delta_percentage,
                'status': status
            })
            
            print(f"Processed: {actual_name} -> Actual: {actual_commute}min, Algorithm: {algorithm_commute}min, Delta: {commute_delta}min")
        
        # Filter to only interns with both commutes
        complete_data = [d for d in delta_data if d['actual_commute'] and d['algorithm_commute']]
        
        print(f"\nComplete commute data for {len(complete_data)} interns")
        
        # Calculate summary statistics
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
        
        # Create delta analysis report
        report_data = [
            ['Delta Commute Analysis: Actual vs Algorithm-Suggested'],
            [''],
            ['KEY METRICS'],
            ['Interns with Complete Data', len(complete_data)],
            ['Average Actual Commute', f'{avg_actual:.1f} minutes'],
            ['Average Algorithm Commute', f'{avg_algorithm:.1f} minutes'],
            ['Average Delta (Actual - Algorithm)', f'{avg_delta:.1f} minutes'],
            [''],
            ['COMMUTE IMPROVEMENTS'],
            ['Algorithm Better (Saves Time)', len(improvements)],
            ['Actual Better (Current Faster)', len(worsenings)],
            ['Perfect Matches', len(perfect_matches)],
            [''],
            ['DETAILED DELTA ANALYSIS'],
            ['Intern Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Actual Commute', 'Algorithm Commute', 'Delta (min)', 'Delta %', 'Status']
        ]
        
        # Sort by delta (biggest improvements first)
        complete_data.sort(key=lambda x: x['commute_delta'] if x['commute_delta'] else -999, reverse=True)
        
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
        
        # Add summary sections
        report_data.extend([
            [''],
            ['TOP COMMUTE IMPROVEMENTS'],
            ['Intern Name', 'Current Commute', 'Algorithm Commute', 'Time Saved', 'Percentage']
        ])
        
        for data in improvements[:5]:
            report_data.append([
                data['actual_name'],
                f"{data['actual_commute']:.1f} min",
                f"{data['algorithm_commute']:.1f} min",
                f"{data['commute_delta']:.1f} min",
                f"{data['delta_percentage']:.1f}%"
            ])
        
        # Add perfect matches
        report_data.extend([
            [''],
            ['PERFECT MATCHES (No Change Needed)'],
            ['Intern Name', 'Restaurant', 'Commute Time']
        ])
        
        for data in perfect_matches:
            report_data.append([
                data['actual_name'],
                data['actual_restaurant'],
                f"{data['actual_commute']:.1f} min"
            ])
        
        # Save report
        report_df = pd.DataFrame(report_data)
        report_df.to_csv('delta_commute_analysis_report.csv', index=False, header=False)
        
        print(f"Delta commute analysis saved to 'delta_commute_analysis_report.csv'")
        
        # Print summary
        print(f"\nDELTA COMMUTE SUMMARY:")
        print(f"Interns with complete data: {len(complete_data)}")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average algorithm commute: {avg_algorithm:.1f} minutes")
        print(f"Average improvement: {avg_delta:.1f} minutes")
        print(f"Algorithm better: {len(improvements)} interns")
        print(f"Actual better: {len(worsenings)} interns")
        print(f"Perfect matches: {len(perfect_matches)} interns")
        
        return complete_data
        
    except Exception as e:
        print(f"Error in delta analysis: {e}")
        return []

def main():
    """Main function"""
    delta_data = delta_commute_analysis()
    
    print(f"\n" + "="*80)
    print("DELTA COMMUTE ANALYSIS COMPLETE")
    print("="*80)
    print(f"Delta analysis created for {len(delta_data)} interns")

if __name__ == "__main__":
    main()
