#!/usr/bin/env python3
"""
Add missing restaurants from Chef Availabilities to database
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def add_missing_restaurants_to_db():
    """Add missing restaurants from Chef Availabilities to database"""
    print("="*80)
    print("ADDING MISSING RESTAURANTS TO DATABASE")
    print("From Chef Availabilities to fix partial data issue")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Restaurant
        from app import db
        
        app = create_app()
        app.app_context().push()
        
        # Load Chef Availabilities
        chef_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv')
        
        # Get current database restaurants
        db_restaurants = Restaurant.query.all()
        db_restaurant_names = {rest.name for rest in db_restaurants}
        
        print(f"Current database restaurants: {len(db_restaurant_names)}")
        
        # Extract restaurants from Chef Availabilities
        chef_restaurants = {}
        for idx, row in chef_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            restaurant_name = str(row.iloc[3]).strip()  # Column 3 is Restaurant Name
            if restaurant_name and restaurant_name != 'nan':
                # Store details
                chef_restaurants[restaurant_name] = {
                    'mentor_name': str(row.iloc[7]).strip(),  # Primary Mentor's Full Name
                    'mentor_phone': str(row.iloc[8]).strip(),  # Primary Mentor's Cell Phone
                    'mentor_email': str(row.iloc[9]).strip(),  # Primary Mentor's Email
                    'address': str(row.iloc[6]).strip(),  # Restaurant Address
                    'location': str(row.iloc[5]).strip(),  # Restaurant Location
                    'age_requirement': str(row.iloc[4]).strip()  # Over 18 requirement
                }
        
        print(f"Restaurants in Chef Availabilities: {len(chef_restaurants)}")
        
        # Find restaurants to add
        restaurants_to_add = {}
        for name, details in chef_restaurants.items():
            if name not in db_restaurant_names:
                restaurants_to_add[name] = details
        
        print(f"Restaurants to add: {len(restaurants_to_add)}")
        
        if restaurants_to_add:
            print(f"\nAdding missing restaurants:")
            added_count = 0
            
            for restaurant_name, details in restaurants_to_add.items():
                print(f"\nAdding: {restaurant_name}")
                print(f"  Mentor: {details.get('mentor_name', 'N/A')}")
                print(f"  Email: {details.get('mentor_email', 'N/A')}")
                print(f"  Address: {details.get('address', 'N/A')}")
                
                # Create restaurant
                new_restaurant = Restaurant(
                    name=restaurant_name,
                    mentor_name=details.get('mentor_name', f"Chef for {restaurant_name}"),
                    mentor_phone=details.get('mentor_phone', "555-0000"),
                    mentor_email=details.get('mentor_email', f"chef_{restaurant_name.lower().replace(' ', '_')}@example.com"),
                    email=details.get('mentor_email', f"chef_{restaurant_name.lower().replace(' ', '_')}@example.com"),
                    address=details.get('address', f"{restaurant_name} Address, San Francisco, CA"),
                    city=details.get('location', "San Francisco"),
                    state="CA",
                    country="USA",
                    requires_over_18=details.get('age_requirement', 'No') == 'Yes',
                    is_active=True,
                    is_verified=True
                )
                
                db.session.add(new_restaurant)
                added_count += 1
                print(f"  Added successfully")
            
            # Commit changes
            db.session.commit()
            print(f"\nSuccessfully added {added_count} restaurants to database!")
            
            # Verify
            updated_restaurants = Restaurant.query.all()
            print(f"Updated database restaurants: {len(updated_restaurants)}")
            
        else:
            print("No missing restaurants to add")
        
        return len(restaurants_to_add)
        
    except Exception as e:
        print(f"Error adding restaurants: {e}")
        return 0

def rerun_analysis_with_all_restaurants():
    """Rerun analysis with all restaurants now in database"""
    print("="*80)
    print("RERUNNING ANALYSIS WITH ALL RESTAURANTS")
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
        print(f"\nRunning Hungarian algorithm with all restaurants...")
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
        
        # Filter to assigned interns
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        
        print(f"Actual assigned interns: {len(assigned_interns)}")
        
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
        
        # Enhanced delta analysis
        delta_data = []
        matching_stats = {
            'total': len(assigned_interns),
            'intern_matched': 0,
            'actual_restaurant_matched': 0,
            'algorithm_restaurant_matched': 0,
            'both_commutes_computed': 0
        }
        
        print(f"\nComputing enhanced delta analysis...")
        
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
        
        print(f"\nUPDATED MATCHING STATISTICS:")
        print(f"Total interns: {matching_stats['total']}")
        print(f"Interns matched: {matching_stats['intern_matched']}")
        print(f"Actual restaurants matched: {matching_stats['actual_restaurant_matched']}")
        print(f"Algorithm assignments found: {matching_stats['algorithm_restaurant_matched']}")
        print(f"Both commutes computed: {matching_stats['both_commutes_computed']}")
        
        # Filter data
        complete_data = [d for d in delta_data if d['actual_commute'] and d['algorithm_commute']]
        partial_data = [d for d in delta_data if (d['actual_commute'] or d['algorithm_commute']) and not (d['actual_commute'] and d['algorithm_commute'])]
        
        # Calculate metrics
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
        
        print(f"\nIMPROVED RESULTS:")
        print(f"Complete data: {len(complete_data)} interns")
        print(f"Partial data: {len(partial_data)} interns")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average algorithm commute: {avg_algorithm:.1f} minutes")
        print(f"Average improvement: {avg_delta:.1f} minutes")
        
        return complete_data, partial_data
        
    except Exception as e:
        print(f"Error in rerun analysis: {e}")
        return [], []

def main():
    """Main function"""
    # Step 1: Add missing restaurants
    added_count = add_missing_restaurants_to_db()
    print(f"\nAdded {added_count} restaurants to database")
    
    # Step 2: Rerun analysis
    complete, partial = rerun_analysis_with_all_restaurants()
    
    print(f"\n" + "="*80)
    print("COMPLETE ANALYSIS WITH ALL RESTAURANTS - FIXED")
    print("="*80)
    print(f"Results: {len(complete)} complete, {len(partial)} partial data points")

if __name__ == "__main__":
    main()
