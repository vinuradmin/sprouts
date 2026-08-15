#!/usr/bin/env python3
"""
Debug why we still have partial data after adding all restaurants
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_partial_data():
    """Debug remaining partial data issues"""
    print("="*80)
    print("DEBUGGING REMAINING PARTIAL DATA")
    print("Why 8 interns still have partial data after adding all restaurants?")
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
        
        # Filter to assigned interns
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        
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
        
        print(f"DEBUGGING PARTIAL DATA ISSUES:")
        print(f"Total assigned interns: {len(assigned_interns)}")
        
        partial_data_cases = []
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find intern
            intern = None
            mapped_name = name_mapping.get(actual_name)
            if mapped_name:
                intern = intern_lookup.get(mapped_name)
            
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
            
            # Get algorithm commute
            algorithm_commute = None
            algorithm_restaurant = 'Unassigned'
            if algorithm_assignment:
                algorithm_commute = algorithm_assignment['commute_minutes']
                algorithm_restaurant = algorithm_assignment['restaurant_name']
            
            # Check if this is partial data
            has_actual = actual_commute is not None
            has_algorithm = algorithm_commute is not None
            is_partial = (has_actual != has_algorithm) and (has_actual or has_algorithm)
            
            if is_partial:
                partial_data_cases.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_restaurant': algorithm_restaurant,
                    'intern_found': intern is not None,
                    'mapped_name': mapped_name,
                    'actual_restaurant_obj': find_restaurant(actual_restaurant) is not None,
                    'actual_commute': actual_commute,
                    'algorithm_commute': algorithm_commute,
                    'algorithm_assignment_found': algorithm_assignment is not None,
                    'has_actual': has_actual,
                    'has_algorithm': has_algorithm,
                    'issue_type': 'Missing actual commute' if has_algorithm and not has_actual else 'Missing algorithm commute'
                })
        
        print(f"\nFound {len(partial_data_cases)} partial data cases:")
        
        for i, case in enumerate(partial_data_cases, 1):
            print(f"\n{i}. {case['actual_name']}")
            print(f"   Actual Restaurant: {case['actual_restaurant']}")
            print(f"   Algorithm Restaurant: {case['algorithm_restaurant']}")
            print(f"   Issue Type: {case['issue_type']}")
            print(f"   Intern Found: {case['intern_found']}")
            print(f"   Mapped Name: {case['mapped_name']}")
            print(f"   Actual Restaurant Object Found: {case['actual_restaurant_obj']}")
            print(f"   Algorithm Assignment Found: {case['algorithm_assignment_found']}")
            print(f"   Actual Commute: {case['actual_commute']}")
            print(f"   Algorithm Commute: {case['algorithm_commute']}")
            
            # Debug specific issues
            if case['issue_type'] == 'Missing actual commute':
                print(f"   DEBUG - Why missing actual commute:")
                if not case['intern_found']:
                    print(f"     - Intern not found in database")
                elif not case['actual_restaurant_obj']:
                    print(f"     - Actual restaurant not found in database")
                    print(f"     - Available restaurants: {list(restaurant_lookup.keys())}")
                else:
                    print(f"     - Commute calculation failed (API issue?)")
            
            elif case['issue_type'] == 'Missing algorithm commute':
                print(f"   DEBUG - Why missing algorithm commute:")
                if not case['algorithm_assignment_found']:
                    print(f"     - No algorithm assignment found")
                    print(f"     - Available algorithm assignments: {list(algorithm_lookup.keys())}")
                else:
                    print(f"     - Algorithm assignment has no commute data")
        
        # Special focus on problematic restaurants
        print(f"\n" + "="*60)
        print("PROBLEMATIC RESTAURANTS ANALYSIS")
        print("="*60)
        
        problematic_restaurants = set()
        for case in partial_data_cases:
            if case['issue_type'] == 'Missing actual commute':
                problematic_restaurants.add(case['actual_restaurant'])
        
        if problematic_restaurants:
            print(f"Restaurants causing missing actual commutes:")
            for rest in sorted(problematic_restaurants):
                print(f"  - {rest}")
                
                # Check if restaurant exists in database
                rest_obj = find_restaurant(rest)
                if rest_obj:
                    print(f"    Found in database: {rest_obj.name}")
                    print(f"    Address: {rest_obj.address}")
                else:
                    print(f"    NOT FOUND in database")
        
        return partial_data_cases
        
    except Exception as e:
        print(f"Error debugging partial data: {e}")
        return []

def main():
    """Main function"""
    partial_cases = debug_partial_data()
    
    print(f"\n" + "="*80)
    print("PARTIAL DATA DEBUG COMPLETE")
    print("="*80)
    print(f"Found {len(partial_cases)} partial data cases")

if __name__ == "__main__":
    main()
