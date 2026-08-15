#!/usr/bin/env python3
"""
Detailed analysis of the 8 interns with actual assignments but no algorithm assignments
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def detailed_mismatch_analysis():
    """Detailed analysis of each mismatch case"""
    print("="*80)
    print("DETAILED ANALYSIS OF 8 MISMATCH CASES")
    print("Interns with actual assignments but no algorithm assignments")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get data
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        optimizer = TransportationOptimizer()
        
        # The 8 specific cases
        mismatch_cases = [
            {'name': 'Eric  Willis', 'actual': 'alaMar Dominican Kitchen'},
            {'name': "De'Sean Skinner", 'actual': 'Alab SF'},
            {'name': 'Gavin Patane', 'actual': 'Stanford'},
            {'name': 'Giselle Contreras', 'actual': 'Sirene'},
            {'name': 'Andrea Caballero', 'actual': 'Stanford'},
            {'name': 'Jesus Chavez', 'actual': 'Stanford'},
            {'name': 'Shelsea Vasquez', 'actual': 'Burdell'},
            {'name': 'Roni Velasquez', 'actual': 'Teranga'}
        ]
        
        for case in mismatch_cases:
            print(f"\n" + "="*60)
            print(f"CASE: {case['name']}")
            print(f"Actual Assignment: {case['actual']}")
            print("="*60)
            
            # Find intern in database
            intern = None
            for i in interns:
                if case['name'] in i.user.full_name or i.user.full_name in case['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"ERROR: Intern not found in database")
                continue
            
            print(f"OK: Found in database: {intern.user.full_name}")
            print(f"   Email: {intern.user.email}")
            print(f"   Location: {intern.get_full_address()}")
            print(f"   Age: {intern.age}")
            print(f"   Transportation: {intern.transportation_method}")
            
            # Find actual restaurant in database
            actual_restaurant_db = None
            for restaurant in restaurants:
                if case['actual'] in restaurant.name or restaurant.name in case['actual']:
                    actual_restaurant_db = restaurant
                    break
            
            if not actual_restaurant_db:
                print(f"ERROR: Restaurant '{case['actual']}' not found in database")
                continue
            
            print(f"OK: Restaurant found: {actual_restaurant_db.name}")
            
            # Check commute time
            try:
                commute_time = optimizer.get_optimal_commute(
                    intern.get_full_address(),
                    actual_restaurant_db.get_full_address(),
                    intern.transportation_method or 'driving'
                )
                print(f"Commute time: {commute_time} min")
                
                if commute_time is None:
                    print(f"   ERROR: Could not calculate commute")
                elif commute_time > 50:
                    print(f"   ISSUE: Commute exceeds 50 min limit")
                else:
                    print(f"   OK: Commute within limits")
            except Exception as e:
                print(f"   ERROR: {e}")
            
            # Check age requirement
            if actual_restaurant_db.requires_over_18:
                if intern.age and intern.age >= 18:
                    print(f"Age: OK {intern.age} >= 18")
                else:
                    print(f"Age: ISSUE {intern.age} < 18 (restaurant requires 18+)")
            else:
                print(f"Age: OK No restriction")
            
            # Check availability
            if not intern.availability:
                print(f"Availability: ERROR No availability data")
            else:
                print(f"Availability: OK Has availability data")
            
            # Check if they could be assigned to ANY restaurant
            print(f"\nChecking if intern could be assigned to ANY restaurant:")
            possible_assignments = 0
            
            for restaurant in restaurants:
                # Skip if age restriction not met
                if restaurant.requires_over_18 and (not intern.age or intern.age < 18):
                    continue
                
                try:
                    commute = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        restaurant.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    
                    if commute and commute <= 50:
                        possible_assignments += 1
                        if possible_assignments <= 3:  # Show first 3 options
                            print(f"   OK {restaurant.name}: {commute} min")
                except:
                    pass
            
            print(f"   Total possible restaurants within 50 min: {possible_assignments}")
            
            if possible_assignments == 0:
                print(f"   ERROR: NO restaurants within commute limit")
            elif possible_assignments < 5:
                print(f"   WARNING: Limited options ({possible_assignments} restaurants)")
            else:
                print(f"   OK: Good options ({possible_assignments} restaurants)")
        
        # Check Jesus duplication issue
        print(f"\n" + "="*80)
        print("JESUS DUPLICATION INVESTIGATION")
        print("="*80)
        
        # Load Excel data to check for multiple Jesus entries
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        
        jesus_entries = df[df['Name'].str.contains('Jesus', na=False, case=False)]
        
        print(f"Found {len(jesus_entries)} Jesus entries in Excel:")
        for idx, row in jesus_entries.iterrows():
            print(f"\nRow {idx}:")
            print(f"  Name: {row['Name']}")
            print(f"  Restaurant: {row['Restaurant']}")
            print(f"  Location: {row['Location']}")
            print(f"  Age: {row['Age']}")
        
        # Check database for Jesus entries
        jesus_db_interns = [i for i in interns if 'Jesus' in i.user.full_name]
        print(f"\nFound {len(jesus_db_interns)} Jesus entries in database:")
        for intern in jesus_db_interns:
            print(f"\n{intern.user.full_name}:")
            print(f"  Email: {intern.user.email}")
            print(f"  Location: {intern.get_full_address()}")
            print(f"  Age: {intern.age}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    detailed_mismatch_analysis()
    
    print(f"\n" + "="*80)
    print("DETAILED MISMATCH ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
