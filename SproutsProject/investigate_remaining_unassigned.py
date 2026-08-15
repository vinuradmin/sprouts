#!/usr/bin/env python3
"""
Investigate why the remaining 3 interns are still unassigned after fixes
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_remaining_unassigned():
    """Investigate why specific interns are still unassigned"""
    print("="*80)
    print("INVESTIGATING REMAINING UNASSIGNED INTERNS")
    print("Why Eric, Gavin, and Andrea are still not assigned")
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
        
        # The 3 remaining cases
        remaining_cases = [
            {'name': 'Eric Willis', 'email': 'Ericg@foreigncinema.com'},
            {'name': 'Gavin Patane', 'email': 'Gavin@sirene-oak.com'},
            {'name': 'Andrea Caballero', 'email': 'andreacaballeropb@gmail.com'}
        ]
        
        for case in remaining_cases:
            print(f"\n" + "="*60)
            print(f"INVESTIGATING: {case['name']}")
            print("="*60)
            
            # Find intern in database
            intern = None
            for i in interns:
                if case['name'] in i.user.full_name or i.user.full_name in case['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"Not found in database")
                continue
            
            print(f"Database intern: {intern.user.full_name}")
            print(f"Email: {intern.user.email}")
            print(f"Address: {intern.get_full_address()}")
            print(f"Age: {intern.age}")
            print(f"Transportation: {intern.transportation_method}")
            print(f"Availability: {'Yes' if intern.availability else 'No'}")
            
            # Check commute times to all restaurants
            print(f"\nCommute analysis (90 minute limit):")
            possible_restaurants = []
            
            for restaurant in restaurants:
                # Check age requirement
                if restaurant.requires_over_18 and (not intern.age or intern.age < 18):
                    continue
                
                try:
                    commute_time = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        restaurant.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    
                    if commute_time and commute_time <= 90:
                        possible_restaurants.append({
                            'name': restaurant.name,
                            'commute': commute_time,
                            'age_req': restaurant.requires_over_18
                        })
                        
                        if len(possible_restaurants) <= 5:  # Show first 5
                            print(f"  OK {restaurant.name}: {commute_time} min")
                except Exception as e:
                    print(f"  ERROR {restaurant.name}: {e}")
            
            print(f"\nTotal possible restaurants: {len(possible_restaurants)}")
            
            if len(possible_restaurants) == 0:
                print("  ISSUE: No restaurants within 90 minute commute")
            elif len(possible_restaurants) < 3:
                print(f"  WARNING: Limited options ({len(possible_restaurants)} restaurants)")
            else:
                print(f"  GOOD: Multiple options ({len(possible_restaurants)} restaurants)")
            
            # Check schedule compatibility for top 3 options
            print(f"\nSchedule compatibility check:")
            for i, rest in enumerate(possible_restaurants[:3]):
                restaurant = next((r for r in restaurants if r.name == rest['name']), None)
                if restaurant:
                    print(f"  {restaurant.name} ({rest['commute']} min):")
                    
                    # Basic schedule check
                    if not intern.availability:
                        print(f"    ERROR: No availability data")
                    else:
                        print(f"    OK: Has availability data")
                    
                    # Age check
                    if restaurant.requires_over_18:
                        if intern.age and intern.age >= 18:
                            print(f"    OK: Age requirement met ({intern.age} >= 18)")
                        else:
                            print(f"    ERROR: Age requirement not met ({intern.age} < 18)")
                    else:
                        print(f"    OK: No age restriction")
        
        # Run a detailed algorithm analysis
        print(f"\n" + "="*60)
        print("DETAILED ALGORITHM ANALYSIS")
        print("="*60)
        
        matching_service = HungarianMatchingService()
        
        # Get algorithm result with detailed info
        result = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            max_commute_minutes=90,
            restaurant_capacity=2
        )
        
        assignments = result.get('assignments', [])
        unmatched = result.get('unmatched_interns', [])
        
        print(f"Algorithm assigned: {len(assignments)} interns")
        print(f"Algorithm unmatched: {len(unmatched)} interns")
        
        # Check if our cases are in unmatched list
        print(f"\nUnmatched interns:")
        for unmatched_intern in unmatched:
            name = unmatched_intern.get('name', '')
            for case in remaining_cases:
                if case['name'] in name or name in case['name']:
                    print(f"  {name}: {unmatched_intern}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    investigate_remaining_unassigned()
    
    print(f"\n" + "="*80)
    print("REMAINING UNASSIGNED INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
