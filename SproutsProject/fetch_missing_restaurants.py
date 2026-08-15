#!/usr/bin/env python3
"""
Fetch missing restaurants from Chef Availabilities and rerun complete analysis
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fetch_missing_restaurants():
    """Fetch missing restaurants from Chef Availabilities sheet"""
    print("="*80)
    print("FETCHING MISSING RESTAURANTS FROM CHEF AVAILABILITIES")
    print("="*80)
    
    try:
        # Load Chef Availabilities
        chef_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv')
        
        # Load actual assignments from Excel
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Extract actual restaurants
        actual_restaurants = set()
        for idx, row in fall_2025_df.iterrows():
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(restaurant_col):
                restaurant_name = str(restaurant_col).strip()
                if restaurant_name and restaurant_name != 'nan' and restaurant_name != 'Unassigned':
                    actual_restaurants.add(restaurant_name)
        
        print(f"Actual restaurants in Excel: {len(actual_restaurants)}")
        for rest in sorted(actual_restaurants):
            print(f"  - {rest}")
        
        # Extract restaurants from Chef Availabilities
        chef_restaurants = set()
        for idx, row in chef_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            restaurant_col = str(row.iloc[8]).strip()  # restaurantname column
            if restaurant_col and restaurant_col != 'nan':
                chef_restaurants.add(restaurant_col)
        
        print(f"\nRestaurants in Chef Availabilities: {len(chef_restaurants)}")
        for rest in sorted(chef_restaurants):
            print(f"  - {rest}")
        
        # Find missing restaurants
        missing_in_chef = actual_restaurants - chef_restaurants
        missing_in_actual = chef_restaurants - actual_restaurants
        
        print(f"\nMISSING RESTAURANTS:")
        print(f"In Excel but not in Chef Availabilities ({len(missing_in_chef)}):")
        for rest in sorted(missing_in_chef):
            print(f"  - {rest}")
        
        print(f"\nIn Chef Availabilities but not in Excel ({len(missing_in_actual)}):")
        for rest in sorted(missing_in_actual):
            print(f"  - {rest}")
        
        # Check current database restaurants
        from app import create_app
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        db_restaurants = Restaurant.query.all()
        db_restaurant_names = {rest.name for rest in db_restaurants}
        
        print(f"\nCurrent database restaurants: {len(db_restaurant_names)}")
        
        # Find restaurants that need to be added
        restaurants_to_add = actual_restaurants - db_restaurant_names
        restaurants_in_db = actual_restaurants & db_restaurant_names
        
        print(f"\nRESTAURANT STATUS:")
        print(f"Already in database ({len(restaurants_in_db)}):")
        for rest in sorted(restaurants_in_db):
            print(f"  ✓ {rest}")
        
        print(f"\nNeed to add to database ({len(restaurants_to_add)}):")
        for rest in sorted(restaurants_to_add):
            print(f"  + {rest}")
        
        return actual_restaurants, chef_restaurants, restaurants_to_add
        
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return set(), set(), set()

def add_missing_restaurants(restaurants_to_add):
    """Add missing restaurants to database"""
    print("="*80)
    print("ADDING MISSING RESTAURANTS TO DATABASE")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Restaurant, db
        
        app = create_app()
        app.app_context().push()
        
        # Load Chef Availabilities for restaurant details
        chef_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv')
        
        added_count = 0
        
        for restaurant_name in restaurants_to_add:
            print(f"\nProcessing: {restaurant_name}")
            
            # Look for restaurant in Chef Availabilities
            restaurant_details = None
            for idx, row in chef_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                chef_restaurant = str(row.iloc[8]).strip()
                if chef_restaurant == restaurant_name:
                    restaurant_details = row
                    break
            
            if restaurant_details is not None:
                # Extract details
                chef_name = str(restaurant_details.iloc[9]).strip()  # chefname
                chef_email = str(restaurant_details.iloc[11]).strip()  # chef email
                chef_phone = str(restaurant_details.iloc[13]).strip()  # chef phone
                restaurant_address = str(restaurant_details.iloc[20]).strip()  # restaurantaddress
                
                # Create restaurant
                new_restaurant = Restaurant(
                    name=restaurant_name,
                    chef_name=chef_name if chef_name and chef_name != 'nan' else f"Chef for {restaurant_name}",
                    email=chef_email if chef_email and chef_email != 'nan' else f"chef_{restaurant_name.lower().replace(' ', '_')}@example.com",
                    phone=chef_phone if chef_phone and chef_phone != 'nan' else "555-0000",
                    address=restaurant_address if restaurant_address and restaurant_address != 'nan' else f"{restaurant_name} Address, San Francisco, CA",
                    city="San Francisco",
                    state="CA",
                    zip_code="94102",
                    cuisine_type="Various",
                    is_seeking_interns=True
                )
                
                db.session.add(new_restaurant)
                added_count += 1
                print(f"  ✓ Added: {restaurant_name}")
                print(f"    Chef: {chef_name}")
                print(f"    Email: {chef_email}")
                print(f"    Address: {restaurant_address}")
            else:
                print(f"  ✗ Not found in Chef Availabilities: {restaurant_name}")
                # Add with default details
                new_restaurant = Restaurant(
                    name=restaurant_name,
                    chef_name=f"Chef for {restaurant_name}",
                    email=f"chef_{restaurant_name.lower().replace(' ', '_')}@example.com",
                    phone="555-0000",
                    address=f"{restaurant_name} Address, San Francisco, CA",
                    city="San Francisco",
                    state="CA",
                    zip_code="94102",
                    cuisine_type="Various",
                    is_seeking_interns=True
                )
                
                db.session.add(new_restaurant)
                added_count += 1
                print(f"  ✓ Added with defaults: {restaurant_name}")
        
        # Commit changes
        db.session.commit()
        
        print(f"\nSuccessfully added {added_count} restaurants to database!")
        
        return added_count
        
    except Exception as e:
        print(f"Error adding restaurants: {e}")
        return 0

def rerun_complete_analysis():
    """Rerun complete analysis with all restaurants"""
    print("="*80)
    print("RERUNNING COMPLETE ANALYSIS WITH ALL RESTAURANTS")
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
        restaurants = Restaurant.query.filter_by(is_seeking_interns=True).all()
        
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
        
        # Enhanced matching with better restaurant lookup
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
        
        print(f"\nFINAL MATCHING STATISTICS:")
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
        
        # Create final report
        report_data = [
            ['Complete Analysis with All Restaurants'],
            [''],
            ['MATCHING STATISTICS'],
            ['Total Assigned Interns', matching_stats['total']],
            ['Interns Matched to Database', matching_stats['intern_matched']],
            ['Actual Restaurants Matched', matching_stats['actual_restaurant_matched']],
            ['Algorithm Assignments Found', matching_stats['algorithm_restaurant_matched']],
            ['Complete Commute Data', matching_stats['both_commutes_computed']],
            [''],
            ['KEY METRICS'],
            ['Average Actual Commute', f'{avg_actual:.1f} minutes'],
            ['Average Algorithm Commute', f'{avg_algorithm:.1f} minutes'],
            ['Average Delta (Actual - Algorithm)', f'{avg_delta:.1f} minutes'],
            [''],
            ['COMMUTE IMPROVEMENTS'],
            ['Algorithm Better (Saves Time)', len(improvements)],
            ['Actual Better (Current Faster)', len(worsenings)],
            ['Perfect Matches', len(perfect_matches)],
            [''],
            ['COMPLETE DELTA ANALYSIS'],
            ['Intern Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Actual Commute', 'Algorithm Commute', 'Delta (min)', 'Delta %', 'Status']
        ]
        
        # Sort by delta
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
        
        # Save report
        report_df = pd.DataFrame(report_data)
        report_df.to_csv('complete_analysis_all_restaurants.csv', index=False, header=False)
        
        print(f"\nComplete analysis saved to 'complete_analysis_all_restaurants.csv'")
        
        print(f"\nFINAL SUMMARY:")
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
    # Step 1: Fetch missing restaurants
    actual_restaurants, chef_restaurants, restaurants_to_add = fetch_missing_restaurants()
    
    # Step 2: Add missing restaurants
    if restaurants_to_add:
        added_count = add_missing_restaurants(restaurants_to_add)
        print(f"\nAdded {added_count} restaurants to database")
    else:
        print(f"\nNo missing restaurants to add")
    
    # Step 3: Rerun complete analysis
    complete, partial = rerun_complete_analysis()
    
    print(f"\n" + "="*80)
    print("COMPLETE ANALYSIS WITH ALL RESTAURANTS - DONE")
    print("="*80)
    print(f"Final analysis created with {len(complete)} complete and {len(partial)} partial data points")

if __name__ == "__main__":
    main()
