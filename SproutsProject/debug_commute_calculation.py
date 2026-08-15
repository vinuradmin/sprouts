#!/usr/bin/env python3
"""
Debug commute calculation issues
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_commute_cache():
    """Debug the commute cache"""
    print("=== DEBUGGING COMMUTE CACHE ===")
    
    try:
        from app.services.commute_service import CommuteCache
        
        cache = CommuteCache('cached_commute.json')
        
        print(f"Cache file: cached_commute.json")
        print(f"Cache exists: {os.path.exists('cached_commute.json')}")
        
        # Test cache functionality
        print(f"\nTesting cache with simple addresses...")
        
        # Test with known addresses
        test_cases = [
            ('driving', 'San Francisco, CA', 'Oakland, CA'),
            ('transit', 'San Francisco, CA', 'Oakland, CA'),
            ('rideshare', 'San Francisco, CA', 'Oakland, CA'),
            ('driving', '3016 Brookdale Ave, Oakland, CA', '1 Sansome Street, San Francisco, CA'),
        ]
        
        for transport, origin, destination in test_cases:
            print(f"\nTesting: {transport} from {origin} to {destination}")
            
            try:
                result = cache.get_commute(transport, origin, destination)
                if result:
                    print(f"  Result: {result.value} ms ({result.value // 60000} minutes)")
                    print(f"  Duration: {result.duration}")
                    print(f"  Status: {result.status}")
                else:
                    print(f"  Result: None")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Check cache contents
        print(f"\n=== CACHE CONTENTS ===")
        try:
            import json
            if os.path.exists('cached_commute.json'):
                with open('cached_commute.json', 'r') as f:
                    cache_data = json.load(f)
                
                print(f"Cache entries: {len(cache_data)}")
                
                # Show some sample entries
                for i, (key, value) in enumerate(cache_data.items()):
                    if i < 3:
                        print(f"  {key}: {value}")
                    elif i == 3:
                        print(f"  ... and {len(cache_data) - 3} more entries")
                        break
            else:
                print("Cache file does not exist")
        except Exception as e:
            print(f"Error reading cache: {e}")
        
    except Exception as e:
        print(f"Error debugging commute cache: {e}")

def debug_transportation_optimizer():
    """Debug the transportation optimizer"""
    print("\n=== DEBUGGING TRANSPORTATION OPTIMIZER ===")
    
    try:
        from app.services.transportation_optimizer import TransportationOptimizer
        
        optimizer = TransportationOptimizer()
        
        # Test parsing
        print("Testing transportation parsing...")
        test_strings = [
            "Car (I drive), Public transportation (e.g. bus, BART)",
            "Public transportation (e.g. bus, BART)",
            "Car (My parent drives)",
            "Ridesharing or rental (e.g. Uber, Lyft, Lime)",
            "Skateboard"
        ]
        
        for test_str in test_strings:
            options = optimizer.parse_transportation_options(test_str)
            print(f"Input: {test_str}")
            print(f"Options: {options}")
        
        # Test optimal commute with simple addresses
        print(f"\nTesting optimal commute calculation...")
        
        test_cases = [
            ("Car (I drive), Public transportation (e.g. bus, BART)", 
             "3016 Brookdale Ave, Oakland, CA", "1 Sansome Street, San Francisco, CA"),
            ("Public transportation (e.g. bus, BART)", 
             "3016 Brookdale Ave, Oakland, CA", "1 Sansome Street, San Francisco, CA"),
        ]
        
        for transport_str, origin, destination in test_cases:
            print(f"\nTesting: {transport_str}")
            print(f"From: {origin}")
            print(f"To: {destination}")
            
            comparison = optimizer.get_transportation_comparison(origin, destination, transport_str)
            print(f"Comparison: {comparison}")
            
            optimal = optimizer.get_optimal_commute(origin, destination, transport_str)
            print(f"Optimal: {optimal} minutes")
        
    except Exception as e:
        print(f"Error debugging transportation optimizer: {e}")

def debug_hungarian_integration():
    """Debug Hungarian algorithm integration"""
    print("\n=== DEBUGGING HUNGARIAN INTEGRATION ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        
        # Get a specific intern with multiple options
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        
        # Find Angel Ruiz (has multiple options)
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            print(f"Found intern: {angel_ruiz.user.full_name}")
            print(f"Transportation: {angel_ruiz.transportation_method}")
            print(f"Address: {angel_ruiz.get_full_address()}")
            
            # Get a restaurant
            restaurants = Restaurant.query.all()
            if restaurants:
                restaurant = restaurants[0]
                print(f"Restaurant: {restaurant.name}")
                print(f"Address: {restaurant.get_full_address()}")
                
                # Test the evaluation
                match = service._evaluate_match(angel_ruiz, restaurant, 60, 12)
                if match:
                    print(f"Match found: {match}")
                else:
                    print("No match found")
        
        # Test the full algorithm
        print(f"\nTesting full algorithm...")
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Assignments found: {len(assignments)}")
        
        if assignments:
            commutes = [a['commute_minutes'] for a in assignments]
            avg_commute = sum(commutes) / len(commutes)
            print(f"Average commute: {avg_commute:.1f} minutes")
            
            # Show Angel Ruiz assignment
            for assignment in assignments:
                if 'Angel' in assignment['intern_name']:
                    print(f"Angel Ruiz assignment: {assignment}")
                    break
        
    except Exception as e:
        print(f"Error debugging Hungarian integration: {e}")

def debug_google_maps_api():
    """Debug Google Maps API"""
    print("\n=== DEBUGGING GOOGLE MAPS API ===")
    
    try:
        from app.services.commute_service import CommuteCache
        
        cache = CommuteCache('cached_commute.json')
        
        # Test API directly
        print("Testing Google Maps API...")
        
        # Simple test case
        result = cache.get_commute(
            'driving',
            'San Francisco, CA',
            'Oakland, CA'
        )
        
        if result:
            print(f"API Result: {result.value} ms ({result.value // 60000} minutes)")
            print(f"API Status: {result.status}")
            print(f"API Duration: {result.duration}")
        else:
            print("API returned None")
        
        # Check API key
        print(f"\nChecking API key...")
        print(f"API key configured: {hasattr(cache, 'api_key')}")
        
        if hasattr(cache, 'api_key'):
            print(f"API key length: {len(cache.api_key)}")
            print(f"API key starts with: {cache.api_key[:10]}...")
        
    except Exception as e:
        print(f"Error debugging Google Maps API: {e}")

def run_tests():
    """Run all tests"""
    print("=== RUNNING ALL DEBUG TESTS ===")
    
    debug_commute_cache()
    debug_transportation_optimizer()
    debug_hungarian_integration()
    debug_google_maps_api()
    
    print("\n=== DEBUG TESTS COMPLETE ===")

if __name__ == "__main__":
    run_tests()
