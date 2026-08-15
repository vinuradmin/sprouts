#!/usr/bin/env python3
"""
Get Angel Ruiz's detailed commute information
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def get_angel_ruiz_details():
    """Get Angel Ruiz's detailed commute information"""
    print("=== ANGEL RUIZ DETAILED COMMUTE INFORMATION ===")
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Find Angel Ruiz
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        angel_ruiz = None
        
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if not angel_ruiz:
            print("Angel Ruiz not found")
            return
        
        print(f"INTERN: {angel_ruiz.user.full_name}")
        print(f"Age: {angel_ruiz.age}")
        print(f"Transportation Options: {angel_ruiz.transportation_method}")
        print(f"Address: {angel_ruiz.get_full_address()}")
        print()
        
        # Get all restaurants
        restaurants = Restaurant.query.all()
        
        # Parse Angel's transportation options
        optimizer = TransportationOptimizer()
        transport_options = optimizer.parse_transportation_options(angel_ruiz.transportation_method)
        
        print(f"Parsed Transportation Options: {transport_options}")
        print()
        
        # Check commute to all restaurants
        print("COMMUTE ANALYSIS TO ALL RESTAURANTS:")
        print("=" * 60)
        
        for restaurant in restaurants:
            print(f"\nRESTAURANT: {restaurant.name}")
            print(f"Address: {restaurant.get_full_address()}")
            
            # Get commute comparison for all transportation options
            comparison = optimizer.get_transportation_comparison(
                angel_ruiz.get_full_address(),
                restaurant.get_full_address(),
                angel_ruiz.transportation_method
            )
            
            print(f"Transportation Options:")
            for transport, minutes in comparison.items():
                if minutes is not None:
                    print(f"  {transport.capitalize()}: {minutes} minutes")
                else:
                    print(f"  {transport.capitalize()}: Not available")
            
            # Get optimal commute
            optimal_commute = optimizer.get_optimal_commute(
                angel_ruiz.get_full_address(),
                restaurant.get_full_address(),
                angel_ruiz.transportation_method
            )
            
            if optimal_commute:
                print(f"Optimal Commute: {optimal_commute} minutes")
                
                # Find which option is optimal
                optimal_transport = None
                for transport, minutes in comparison.items():
                    if minutes == optimal_commute:
                        optimal_transport = transport
                        break
                
                if optimal_transport:
                    print(f"Best Option: {optimal_transport.capitalize()}")
            else:
                print("Optimal Commute: Not available")
        
        # Show specific restaurant from Hungarian algorithm
        print(f"\n" + "=" * 60)
        print("HUNGARIAN ALGORITHM ASSIGNMENT:")
        
        from app.services.hungarian_matching import HungarianMatchingService
        
        service = HungarianMatchingService()
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        # Find Angel Ruiz assignment
        angel_assignment = None
        for assignment in assignments:
            if 'Angel' in assignment['intern_name']:
                angel_assignment = assignment
                break
        
        if angel_assignment:
            restaurant_name = angel_assignment['restaurant_name']
            assigned_restaurant = None
            
            for restaurant in restaurants:
                if restaurant.name == restaurant_name:
                    assigned_restaurant = restaurant
                    break
            
            if assigned_restaurant:
                print(f"Assigned Restaurant: {assigned_restaurant.name}")
                print(f"Restaurant Address: {assigned_restaurant.get_full_address()}")
                print(f"Commute Time: {angel_assignment['commute_minutes']} minutes")
                
                # Show detailed comparison for this specific restaurant
                comparison = optimizer.get_transportation_comparison(
                    angel_ruiz.get_full_address(),
                    assigned_restaurant.get_full_address(),
                    angel_ruiz.transportation_method
                )
                
                print(f"All Transportation Options:")
                for transport, minutes in comparison.items():
                    if minutes is not None:
                        print(f"  {transport.capitalize()}: {minutes} minutes")
                    else:
                        print(f"  {transport.capitalize()}: Not available")
                
                # Calculate distance (approximate)
                intern_addr = angel_ruiz.get_full_address()
                rest_addr = assigned_restaurant.get_full_address()
                
                print(f"\nDistance Information:")
                print(f"From: {intern_addr}")
                print(f"To: {rest_addr}")
                
                # Try to get distance from cache
                try:
                    from app.services.commute_service import CommuteCache
                    cache = CommuteCache('cached_commute.json')
                    
                    result = cache.get_commute('driving', intern_addr, rest_addr)
                    if result and hasattr(result, 'distance_text'):
                        print(f"Distance: {result.distance_text}")
                    elif result and hasattr(result, 'distance_value'):
                        distance_km = result.distance_value / 1000  # Convert meters to km
                        print(f"Distance: {distance_km:.1f} km")
                    else:
                        print("Distance: Not available in cache")
                except Exception as e:
                    print(f"Distance: Could not calculate - {e}")
        
        print(f"\n" + "=" * 60)
        print("SUMMARY:")
        print(f"Angel Ruiz has {len(transport_options)} transportation options")
        print(f"System evaluates all options and chooses the minimum commute")
        print(f"This ensures Angel gets the best possible commute time")
        
    except Exception as e:
        print(f"Error getting Angel Ruiz details: {e}")

if __name__ == "__main__":
    get_angel_ruiz_details()
    
    print(f"\n=== ANGEL RUIZ COMMUTE ANALYSIS COMPLETE ===")
