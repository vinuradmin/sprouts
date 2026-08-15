#!/usr/bin/env python3
"""
Debug Jesus's commute - investigate potential 45 min fallback
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_jesus_commute():
    """Debug Jesus's commute calculation"""
    print("="*80)
    print("DEBUGGING JESUS'S COMMUTE CALCULATION")
    print("Investigating potential 45 min fallback")
    print("="*80)
    
    try:
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
        
        # Find Jesus
        jesus_intern = None
        for intern in interns:
            if 'Jesus' in intern.user.full_name:
                jesus_intern = intern
                break
        
        if not jesus_intern:
            print("Jesus not found in database")
            return
        
        print(f"Found Jesus: {jesus_intern.user.full_name}")
        print(f"Address: {jesus_intern.get_full_address()}")
        print(f"Transportation method: {jesus_intern.transportation_method}")
        
        # Run algorithm to get assignments
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        # Find Jesus's algorithm assignments
        jesus_assignments = [a for a in assignments if 'Jesus' in a['intern_name']]
        
        print(f"\nJesus's algorithm assignments: {len(jesus_assignments)}")
        for assignment in jesus_assignments:
            print(f"  {assignment['intern_name']} -> {assignment['restaurant_name']}: {assignment['commute_minutes']} minutes")
        
        # Test specific commute calculations
        print(f"\n" + "="*60)
        print("TESTING SPECIFIC COMMUTE CALCULATIONS")
        print("="*60)
        
        test_restaurants = ['Tarts de Feybesse', 'Abaca', 'Ofena', 'Stanford', 'UC Berkeley']
        
        for rest_name in test_restaurants:
            restaurant = Restaurant.query.filter_by(name=rest_name).first()
            if restaurant:
                print(f"\nTesting {rest_name}:")
                print(f"  Restaurant address: {restaurant.get_full_address()}")
                
                # Test with different transportation methods
                for transport in ['driving', 'transit', 'walking']:
                    try:
                        commute = optimizer.get_optimal_commute(
                            jesus_intern.get_full_address(),
                            restaurant.get_full_address(),
                            transport
                        )
                        print(f"  {transport}: {commute} minutes")
                    except Exception as e:
                        print(f"  {transport}: ERROR - {e}")
            else:
                print(f"\n{rest_name} not found in database")
        
        # Check for fallback values in the optimizer
        print(f"\n" + "="*60)
        print("CHECKING FOR FALLBACK VALUES")
        print("="*60)
        
        # Look at the transportation optimizer source
        import inspect
        optimizer_source = inspect.getsource(optimizer.get_optimal_commute)
        
        print("Checking get_optimal_commute method for fallback values...")
        
        # Look for hardcoded values
        if '45' in optimizer_source:
            print("Found '45' in optimizer source - potential fallback!")
            lines = optimizer_source.split('\n')
            for i, line in enumerate(lines):
                if '45' in line:
                    print(f"  Line {i+1}: {line.strip()}")
        
        # Test with cache disabled
        print(f"\n" + "="*60)
        print("TESTING WITH CACHE DISABLED")
        print("="*60)
        
        # Clear cache if possible
        if hasattr(optimizer, 'cache'):
            print(f"Cache size before: {len(optimizer.cache) if optimizer.cache else 0}")
            if hasattr(optimizer, 'clear_cache'):
                optimizer.clear_cache()
                print("Cache cleared")
        
        # Test again
        test_restaurant = Restaurant.query.filter_by(name='Tarts de Feybesse').first()
        if test_restaurant:
            commute = optimizer.get_optimal_commute(
                jesus_intern.get_full_address(),
                test_restaurant.get_full_address(),
                'driving'
            )
            print(f"Tarts de Feybesse (after cache clear): {commute} minutes")
        
        # Check actual algorithm internals
        print(f"\n" + "="*60)
        print("CHECKING ALGORITHM INTERNALS")
        print("="*60)
        
        # Look at the Hungarian matching service
        matching_source = inspect.getsource(service.find_optimal_assignments)
        
        if '45' in matching_source:
            print("Found '45' in matching service source!")
            lines = matching_source.split('\n')
            for i, line in enumerate(lines):
                if '45' in line:
                    print(f"  Line {i+1}: {line.strip()}")
        
        return jesus_assignments
        
    except Exception as e:
        print(f"Error debugging Jesus commute: {e}")
        return []

def main():
    """Main function"""
    assignments = debug_jesus_commute()
    
    print(f"\n" + "="*80)
    print("JESUS COMMUTE DEBUG COMPLETE")
    print("="*80)
    print(f"Found {len(assignments)} assignments for Jesus")

if __name__ == "__main__":
    main()
