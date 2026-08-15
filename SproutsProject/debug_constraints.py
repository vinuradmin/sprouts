#!/usr/bin/env python3
"""
Debug why long commutes persist despite penalties
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_constraints():
    """Debug constraints and availability issues"""
    print("=== DEBUGGING CONSTRAINTS ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Debugging with {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Test specific cases with long commutes
        service = HungarianMatchingService()
        results = service.find_optimal_assignments(interns, restaurants)
        
        assignments = results.get('assignments', [])
        
        # Find assignments with long commutes
        long_commute_assignments = [a for a in assignments if a['commute_minutes'] >= 45]
        
        print(f"\nFound {len(long_commute_assignments)} assignments with long commutes (45+ min):")
        
        for assignment in long_commute_assignments:
            intern_name = assignment['intern_name']
            restaurant_name = assignment['restaurant_name']
            commute = assignment['commute_minutes']
            hours = assignment['total_overlap_hours']
            
            print(f"\n{intern_name} -> {restaurant_name}:")
            print(f"  Commute: {commute} minutes")
            print(f"  Hours: {hours}")
            
            # Check if this intern has other options
            intern_obj = next((i for i in interns if i.user.full_name == intern_name), None)
            if intern_obj:
                print(f"  Intern age: {intern_obj.age}")
                print(f"  Intern location: {intern_obj.get_full_address()}")
            
            restaurant_obj = next((r for r in restaurants if r.name == restaurant_name), None)
            if restaurant_obj:
                print(f"  Restaurant location: {restaurant_obj.get_full_address()}")
                print(f"  Restaurant capacity: {restaurant_obj.capacity}")
            
            # Check what other options this intern has
            check_alternative_options(intern_obj, restaurant_obj, service, interns, restaurants)
        
        return long_commute_assignments
        
    except Exception as e:
        print(f"Error debugging constraints: {e}")
        return []

def check_alternative_options(intern, current_restaurant, service, interns, restaurants):
    """Check what other options this intern has"""
    try:
        print(f"  Alternative options for {intern.user.full_name}:")
        
        alternative_options = []
        
        for restaurant in restaurants:
            if restaurant.id == current_restaurant.id:
                continue
            
            # Check if this match is valid
            match = service._evaluate_match(intern, restaurant, 60, 12)  # Use higher max commute
            
            if match:
                alternative_options.append({
                    'restaurant': restaurant.name,
                    'commute': match['commute_minutes'],
                    'hours': match['total_overlap_hours']
                })
        
        # Sort by commute time
        alternative_options.sort(key=lambda x: x['commute'])
        
        # Show best 5 alternatives
        for i, option in enumerate(alternative_options[:5]):
            print(f"    {i+1}. {option['restaurant']}: {option['commute']} min, {option['hours']} hrs")
        
        if len(alternative_options) == 0:
            print(f"    No alternative options found")
        elif len(alternative_options) > 5:
            print(f"    ... and {len(alternative_options) - 5} more options")
        
    except Exception as e:
        print(f"    Error checking alternatives: {e}")

def analyze_restaurant_capacity():
    """Analyze restaurant capacity constraints"""
    print(f"\n=== RESTAURANT CAPACITY ANALYSIS ===")
    
    try:
        from app import create_app
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        restaurants = Restaurant.query.all()
        
        print(f"Restaurant capacities:")
        for restaurant in restaurants:
            print(f"  {restaurant.name}: capacity {restaurant.capacity}")
        
        # Check if capacity constraints force long commutes
        total_capacity = sum(r.capacity for r in restaurants)
        print(f"\nTotal capacity: {total_capacity}")
        
        # This might explain why some interns get long commutes
        
    except Exception as e:
        print(f"Error analyzing capacity: {e}")

if __name__ == "__main__":
    long_commutes = debug_constraints()
    analyze_restaurant_capacity()
    
    print(f"\n=== DEBUGGING COMPLETE ===")
    print("This analysis helps understand why long commutes persist despite penalties.")
