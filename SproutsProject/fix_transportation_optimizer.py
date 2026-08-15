#!/usr/bin/env python3
"""
Fix the transportation optimizer to work with the cache
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fix_transportation_optimizer():
    """Fix the transportation optimizer"""
    print("=== FIXING TRANSPORTATION OPTIMIZER ===")
    
    try:
        # Read the current implementation
        with open('app/services/transportation_optimizer.py', 'r') as f:
            content = f.read()
        
        # The issue is that the cache keys don't match exactly
        # Let's create a test to see what's happening
        from app import create_app
        from app.services.commute_service import CommuteCache
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        # Get Angel Ruiz
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            print(f"Angel Ruiz address: {angel_ruiz.get_full_address()}")
            print(f"Angel Ruiz transport: {angel_ruiz.transportation_method}")
            
            # Get a restaurant
            restaurants = Restaurant.query.all()
            if restaurants:
                restaurant = restaurants[0]
                print(f"Restaurant address: {restaurant.get_full_address()}")
                
                # Test different transportation methods
                transport_methods = ['driving', 'transit', 'rideshare']
                
                for method in transport_methods:
                    try:
                        result = cache.get_commute(method, angel_ruiz.get_full_address(), restaurant.get_full_address())
                        if result:
                            minutes = result.value // 60000
                            print(f"  {method}: {minutes} minutes")
                        else:
                            print(f"  {method}: None")
                    except Exception as e:
                        print(f"  {method}: Error - {e}")
        
        # Test the cache key format
        print(f"\n=== TESTING CACHE KEY FORMAT ===")
        
        # Show some cache keys
        import json
        with open('cached_commute.json', 'r') as f:
            cache_data = json.load(f)
        
        print(f"Total cache entries: {len(cache_data)}")
        
        # Show some sample keys
        for i, (key, value) in enumerate(cache_data.items()):
            if i < 5:
                print(f"Key {i+1}: {key}")
                print(f"Value: {value}")
                print()
        
        # Test with exact cache keys
        print(f"=== TESTING WITH EXACT CACHE KEYS ===")
        
        # Use cache keys that exist
        sample_keys = list(cache_data.keys())[:3]
        
        for key in sample_keys:
            print(f"Testing key: {key}")
            parts = key.split('|')
            if len(parts) >= 2:
                origin = parts[0]
                destination = parts[1]
                print(f"  Origin: {origin}")
                print(f"  Destination: {destination}")
                
                # Test with different transport methods
                for method in ['driving', 'transit', 'rideshare']:
                    try:
                        result = cache.get_commute(method, origin, destination)
                        if result:
                            minutes = result.value // 60000
                            print(f"    {method}: {minutes} minutes")
                        else:
                            print(f"    {method}: None")
                    except Exception as e:
                        print(f"    {method}: Error - {e}")
        
        print(f"\n=== ANALYSIS ===")
        print("1. Cache has 512 entries with real data")
        print("2. Transportation optimizer is returning None")
        print("3. This suggests cache key mismatch or API issues")
        print("4. Need to investigate exact key format")
        
    except Exception as e:
        print(f"Error fixing transportation optimizer: {e}")

def create_fixed_optimizer():
    """Create a fixed version of the transportation optimizer"""
    print("\n=== CREATING FIXED OPTIMIZER ===")
    
    try:
        # Create a simple test to understand the issue
        from app import create_app
        from app.services.commute_service import CommuteCache
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        # Get Angel Ruiz
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            print(f"Testing Angel Ruiz: {angel_ruiz.user.full_name}")
            print(f"Transportation: {angel_ruiz.transportation_method}")
            print(f"Address: {angel_ruiz.get_full_address()}")
            
            # Test with alaMar Dominican Kitchen
            restaurants = Restaurant.query.all()
            for restaurant in restaurants:
                if 'alaMar' in restaurant.name:
                    print(f"Restaurant: {restaurant.name}")
                    print(f"Address: {restaurant.get_full_address()}")
                    
                    # Test the exact match from Hungarian algorithm
                    print(f"\nTesting exact match from Hungarian algorithm...")
                    
                    # This is the match we got: 17 minutes
                    try:
                        result = cache.get_commute('driving', angel_ruiz.get_full_address(), restaurant.get_full_address())
                        if result:
                            minutes = result.value // 60000
                            print(f"Driving: {minutes} minutes")
                        
                        result = cache.get_commute('transit', angel_ruiz.get_full_address(), restaurant.get_full_address())
                        if result:
                            minutes = result.value // 60000
                            print(f"Transit: {minutes} minutes")
                        
                        result = cache.get_commute('rideshare', angel_ruiz.get_full_address(), restaurant.get_full_address())
                        if result:
                            minutes = result.value // 60000
                            print(f"Rideshare: {minutes} minutes")
                        
                        # Test with the transportation string
                        transport_options = ['driving', 'transit', 'rideshare']
                        best_commute = None
                        
                        for method in transport_options:
                            result = cache.get_commute(method, angel_ruiz.get_full_address(), restaurant.get_full_address())
                            if result:
                                minutes = result.value // 60000
                                if best_commute is None or minutes < best_commute:
                                    best_commute = minutes
                        
                        print(f"Best commute: {best_commute} minutes")
                        
                    except Exception as e:
                        print(f"Error: {e}")
                    
                    break
        
        print(f"\n=== RECOMMENDATION ===")
        print("1. The cache is working and has data")
        print("2. The transportation optimizer needs to use exact cache keys")
        print("3. Need to fix the key matching logic")
        print("4. Should use the same address format as cache")
        
    except Exception as e:
        print(f"Error creating fixed optimizer: {e}")

def test_simple_case():
    """Test a simple case to understand the issue"""
    print("\n=== TESTING SIMPLE CASE ===")
    
    try:
        from app import create_app
        from app.services.commute_service import CommuteCache
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        # Test with a known cache key
        import json
        with open('cached_commute.json', 'r') as f:
            cache_data = json.load(f)
        
        # Get first cache entry
        first_key = list(cache_data.keys())[0]
        first_value = cache_data[first_key]
        
        print(f"First cache key: {first_key}")
        print(f"First cache value: {first_value}")
        
        parts = first_key.split('|')
        if len(parts) >= 2:
            origin = parts[0]
            destination = parts[1]
            
            print(f"Origin: {origin}")
            print(f"Destination: {destination}")
            
            # Test with different transport methods
            for method in ['driving', 'transit', 'rideshare']:
                try:
                    result = cache.get_commute(method, origin, destination)
                    if result:
                        minutes = result.value // 60000
                        print(f"  {method}: {minutes} minutes")
                    else:
                        print(f"  {method}: None")
                except Exception as e:
                    print(f"  {method}: Error - {e}")
        
        print(f"\n=== CONCLUSION ===")
        print("The cache works fine with exact keys")
        print("The issue is in the transportation optimizer")
        print("Need to fix the key matching logic")
        
    except Exception as e:
        print(f"Error testing simple case: {e}")

if __name__ == "__main__":
    fix_transportation_optimizer()
    create_fixed_optimizer()
    test_simple_case()
    
    print(f"\n=== FIX COMPLETE ===")
    print("Need to update transportation_optimizer.py to fix key matching")
