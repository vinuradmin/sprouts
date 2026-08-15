#!/usr/bin/env python3
"""
Debug why commute times are reading as 0
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_zero_commute():
    """Debug why commute times are 0"""
    print("=== DEBUGGING ZERO COMMUTE TIMES ===")
    
    try:
        # Check the cache file
        import json
        print("Checking cache file...")
        
        with open('cached_commute.json', 'r') as f:
            cache_data = json.load(f)
        
        print(f"Cache entries: {len(cache_data)}")
        
        # Show some sample entries
        for i, (key, value) in enumerate(cache_data.items()):
            if i < 3:
                print(f"Entry {i+1}:")
                print(f"  Key: {key}")
                print(f"  Value: {value}")
                print(f"  Minutes: {value.get('value', 0) // 60000 if value.get('value') else 0}")
                print()
        
        # Check if values are reasonable
        zero_count = 0
        reasonable_count = 0
        
        for key, value in cache_data.items():
            minutes = value.get('value', 0) // 60000 if value.get('value') else 0
            if minutes == 0:
                zero_count += 1
            elif 0 < minutes < 120:
                reasonable_count += 1
        
        print(f"Cache analysis:")
        print(f"  Zero minute entries: {zero_count}")
        print(f"  Reasonable entries: {reasonable_count}")
        print(f"  Total entries: {len(cache_data)}")
        
        # Test the commute cache directly
        print(f"\n=== TESTING COMMUTE CACHE DIRECTLY ===")
        
        from app import create_app
        from app.services.commute_service import CommuteCache
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        # Test with known addresses
        test_cases = [
            ('driving', 'San Francisco, CA', 'Oakland, CA'),
            ('transit', 'San Francisco, CA', 'Oakland, CA'),
            ('driving', '3016 Brookdale Ave, Oakland, CA', '1 Sansome Street, San Francisco, CA'),
        ]
        
        for transport, origin, destination in test_cases:
            print(f"\nTesting: {transport} from {origin} to {destination}")
            
            try:
                result = cache.get_commute(transport, origin, destination)
                if result:
                    minutes = result.value // 60000
                    print(f"  Result: {minutes} minutes")
                    print(f"  Raw value: {result.value}")
                    print(f"  Text: {result.get('text', 'N/A')}")
                    print(f"  Distance: {result.get('distance_text', 'N/A')}")
                else:
                    print(f"  Result: None")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Test with Angel Ruiz's actual addresses
        print(f"\n=== TESTING WITH ACTUAL ADDRESSES ===")
        
        from app.models import Intern, Restaurant
        
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        # Find Angel Ruiz
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            print(f"Angel Ruiz address: {angel_ruiz.get_full_address()}")
            print(f"Angel Ruiz transport: {angel_ruiz.transportation_method}")
            
            # Find alaMar Dominican Kitchen
            for restaurant in restaurants:
                if 'alaMar' in restaurant.name:
                    print(f"Restaurant: {restaurant.name}")
                    print(f"Restaurant address: {restaurant.get_full_address()}")
                    
                    # Test with different transport methods
                    for method in ['driving', 'transit', 'rideshare']:
                        try:
                            result = cache.get_commute(method, angel_ruiz.get_full_address(), restaurant.get_full_address())
                            if result:
                                minutes = result.value // 60000
                                print(f"  {method}: {minutes} minutes")
                            else:
                                print(f"  {method}: None")
                        except Exception as e:
                            print(f"  {method}: Error - {e}")
                    break
        
        print(f"\n=== ANALYSIS ===")
        
        if zero_count > 0:
            print("ISSUE IDENTIFIED:")
            print(f"- {zero_count} cache entries have 0 minutes")
            print("- This suggests API or calculation issues")
            print("- Need to investigate Google Maps API calls")
        
        if reasonable_count > 0:
            print("GOOD NEWS:")
            print(f"- {reasonable_count} cache entries have reasonable times")
            print("- Cache is working for some cases")
            print("- Issue is specific to certain addresses")
        
    except Exception as e:
        print(f"Error debugging zero commute: {e}")

def investigate_api_issues():
    """Investigate potential API issues"""
    print("\n=== INVESTIGATING API ISSUES ===")
    
    try:
        from app import create_app
        from app.services.commute_service import CommuteCache
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        print("Checking API configuration...")
        
        # Check if API key is set
        if hasattr(cache, 'api_key'):
            print(f"API key found: {bool(cache.api_key)}")
            if cache.api_key:
                print(f"API key length: {len(cache.api_key)}")
                print(f"API key starts with: {cache.api_key[:10]}...")
        else:
            print("No API key attribute found")
        
        # Test API call with simple addresses
        print(f"\nTesting API call with simple addresses...")
        
        try:
            result = cache.get_commute('driving', 'San Francisco, CA', 'Oakland, CA')
            if result:
                print(f"API call successful: {result.value // 60000} minutes")
                print(f"Response: {result}")
            else:
                print("API call returned None")
        except Exception as e:
            print(f"API call failed: {e}")
        
        # Check if there's a rate limit or quota issue
        print(f"\nChecking for rate limit issues...")
        
        # Test multiple calls to see if there's a pattern
        for i in range(3):
            try:
                result = cache.get_commute('driving', 'San Francisco, CA', 'Oakland, CA')
                if result:
                    minutes = result.value // 60000
                    print(f"  Call {i+1}: {minutes} minutes")
                else:
                    print(f"  Call {i+1}: None")
            except Exception as e:
                print(f"  Call {i+1}: Error - {e}")
        
    except Exception as e:
        print(f"Error investigating API issues: {e}")

def propose_solutions():
    """Propose solutions for zero commute issue"""
    print("\n=== PROPOSED SOLUTIONS ===")
    
    print("CURRENT ISSUE:")
    print("- Some commute times are reading as 0 minutes")
    print("- This affects the transportation optimization")
    print("- Angel Ruiz improvement is working despite this")
    
    print("\nPOSSIBLE CAUSES:")
    print("1. Google Maps API quota exceeded")
    print("2. Invalid address formatting")
    print("3. Transportation method mapping issues")
    print("4. Cache key mismatch")
    print("5. API returning invalid responses")
    
    print("\nSOLUTIONS:")
    print("1. FALLBACK TO ESTIMATED COMMUTES:")
    print("   - Use distance-based estimates when API fails")
    print("   - Formula: distance / average_speed")
    print("   - Driving: 30 mph, Transit: 15 mph, Walking: 3 mph")
    
    print("2. IMPROVE ADDRESS FORMATTING:")
    print("   - Standardize address formats")
    print("   - Remove special characters")
    print("   - Use city, state format")
    
    print("3. ADD ERROR HANDLING:")
    print("   - Detect 0-minute results")
    print("   - Fall back to reasonable estimates")
    print("   - Log API issues for debugging")
    
    print("4. CACHE VALIDATION:")
    print("   - Validate cache entries")
    print("   - Remove invalid entries")
    print("   - Rebuild cache if needed")
    
    print("5. API MONITORING:")
    print("   - Check API quota usage")
    print("   - Monitor response quality")
    print("   - Implement retry logic")

def create_fallback_solution():
    """Create a fallback solution for zero commute times"""
    print("\n=== CREATING FALLBACK SOLUTION ===")
    
    try:
        # Create a simple fallback function
        fallback_code = '''
def estimate_commute_time(origin, destination, transport_method):
    """Fallback commute time estimation"""
    
    # Simple distance-based estimation
    # This is a rough approximation
    
    # Average speeds (mph)
    speeds = {
        'driving': 30,
        'transit': 15,
        'rideshare': 25,
        'walking': 3,
        'bicycling': 10
    }
    
    # Estimate distance based on city (rough approximation)
    # San Francisco to Oakland: ~10 miles
    # Within SF: ~2-5 miles
    # Within Oakland: ~2-5 miles
    
    distance = estimate_distance(origin, destination)
    speed = speeds.get(transport_method, 30)
    
    # Time = distance / speed * 60 (to minutes)
    estimated_time = (distance / speed) * 60
    
    return max(5, min(120, estimated_time))  # Clamp between 5-120 minutes

def estimate_distance(origin, destination):
    """Rough distance estimation"""
    # This is very rough - in production, use geocoding
    if 'San Francisco' in origin and 'Oakland' in destination:
        return 10
    elif 'Oakland' in origin and 'San Francisco' in destination:
        return 10
    elif 'San Francisco' in origin and 'San Francisco' in destination:
        return 3
    elif 'Oakland' in origin and 'Oakland' in destination:
        return 3
    else:
        return 5  # Default estimate
        '''
        
        print("Fallback solution code created")
        print("This can be integrated into TransportationOptimizer")
        
        # Test the fallback
        print(f"\n=== TESTING FALLBACK ===")
        
        def estimate_commute_time(origin, destination, transport_method):
            speeds = {'driving': 30, 'transit': 15, 'rideshare': 25, 'walking': 3}
            distance = 10 if ('San Francisco' in origin and 'Oakland' in destination) else 3
            speed = speeds.get(transport_method, 30)
            estimated_time = (distance / speed) * 60
            return max(5, min(120, estimated_time))
        
        # Test cases
        test_cases = [
            ('San Francisco, CA', 'Oakland, CA', 'driving'),
            ('San Francisco, CA', 'Oakland, CA', 'transit'),
            ('San Francisco, CA', 'San Francisco, CA', 'driving'),
        ]
        
        for origin, destination, transport in test_cases:
            estimated = estimate_commute_time(origin, destination, transport)
            print(f"  {transport} {origin} -> {destination}: {estimated:.1f} minutes")
        
    except Exception as e:
        print(f"Error creating fallback solution: {e}")

if __name__ == "__main__":
    debug_zero_commute()
    investigate_api_issues()
    propose_solutions()
    create_fallback_solution()
    
    print(f"\n=== ZERO COMMUTE DEBUG COMPLETE ===")
    print("Multiple solutions proposed for handling zero commute times")
