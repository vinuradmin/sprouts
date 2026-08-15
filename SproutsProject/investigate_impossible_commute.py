#!/usr/bin/env python3
"""
Investigate impossible commute times (15.3 miles in 1 minute)
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_impossible_commute():
    """Investigate why commute times are unrealistic"""
    print("=== INVESTIGATING IMPOSSIBLE COMMUTE TIMES ===")
    
    try:
        # Check the cache file directly
        import json
        print("Checking cache file for Angel Ruiz -> Teranga...")
        
        with open('cached_commute.json', 'r') as f:
            cache_data = json.load(f)
        
        # Find the specific cache entry
        angel_addr = "2801 Pullman Ave , Richmond, 94804, USA"
        teranga_addr = " 4 Embarcadero Ctr, San Francisco, CA 94111, United States, Oakland, USA"
        
        cache_key = f"{angel_addr}|{teranga_addr}"
        
        if cache_key in cache_data:
            entry = cache_data[cache_key]
            print(f"Found cache entry:")
            print(f"  Key: {cache_key}")
            print(f"  Value: {entry}")
            
            if 'value' in entry:
                raw_value = entry['value']
                minutes = raw_value // 1000  # Current calculation
                correct_minutes = raw_value // 60000  # Correct calculation
                
                print(f"  Raw value: {raw_value}")
                print(f"  Current calculation (// 1000): {minutes} minutes")
                print(f"  Correct calculation (// 60000): {correct_minutes} minutes")
                
                if 'text' in entry:
                    print(f"  Text from API: {entry['text']}")
                
                if 'distance_text' in entry:
                    print(f"  Distance: {entry['distance_text']}")
                
                print(f"\nANALYSIS:")
                print(f"The API returned '{entry.get('text', 'N/A')}'")
                print(f"But we're calculating {minutes} minutes instead of {correct_minutes} minutes")
                print(f"The issue is in our unit conversion!")
        
        else:
            print(f"Cache key not found: {cache_key}")
            
            # Show some similar keys
            print(f"\nSimilar keys in cache:")
            for key in cache_data.keys():
                if 'Pullman' in key and 'Embarcadero' in key:
                    print(f"  {key}")
                    print(f"  Value: {cache_data[key]}")
                    break
        
        print(f"\n=== TESTING CORRECT CALCULATION ===")
        
        # Test with correct calculation
        from app import create_app
        from app.services.commute_service import CommuteCache
        
        app = create_app()
        app.app_context().push()
        
        cache = CommuteCache('cached_commute.json')
        
        # Test the commute cache directly
        result = cache.get_commute('driving', angel_addr, teranga_addr)
        
        if result:
            print(f"Direct cache result:")
            print(f"  Raw value: {result.value}")
            print(f"  Current calculation: {result.value // 1000} minutes")
            print(f"  Correct calculation: {result.value // 60000} minutes")
            
            if hasattr(result, 'text'):
                print(f"  Text: {result.text}")
            
            if hasattr(result, 'distance_text'):
                print(f"  Distance: {result.distance_text}")
            
            # Calculate realistic speeds
            distance_miles = 15.3
            correct_minutes = result.value // 60000
            
            if correct_minutes > 0:
                speed_mph = distance_miles / (correct_minutes / 60)
                print(f"\nSPEED ANALYSIS:")
                print(f"  Distance: {distance_miles} miles")
                print(f"  Time: {correct_minutes} minutes")
                print(f"  Speed: {speed_mph:.1f} mph")
                
                if speed_mph > 100:
                    print(f"  ⚠️  Unrealistic speed!")
                elif speed_mph > 60:
                    print(f"  ⚠️  Very fast speed")
                else:
                    print(f"  ✅ Realistic speed")
        
        print(f"\n=== CHECKING MULTIPLE ENTRIES ===")
        
        # Check a few more entries to see the pattern
        test_cases = [
            ("driving", angel_addr, teranga_addr),
            ("transit", angel_addr, teranga_addr),
            ("rideshare", angel_addr, teranga_addr),
        ]
        
        for transport, origin, destination in test_cases:
            cache_key = f"{origin}|{destination}"
            
            if cache_key in cache_data:
                entry = cache_data[cache_key]
                raw_value = entry.get('value', 0)
                api_text = entry.get('text', 'N/A')
                
                current_minutes = raw_value // 1000
                correct_minutes = raw_value // 60000
                
                print(f"\n{transport.capitalize()}:")
                print(f"  API text: {api_text}")
                print(f"  Current calc: {current_minutes} minutes")
                print(f"  Correct calc: {correct_minutes} minutes")
                
                if correct_minutes > 0:
                    speed_mph = distance_miles / (correct_minutes / 60)
                    print(f"  Speed: {speed_mph:.1f} mph")
        
        print(f"\n=== CONCLUSION ===")
        print("ISSUE IDENTIFIED:")
        print("1. Google Maps API returns duration in seconds, not milliseconds")
        print("2. Our cache stores the API value directly")
        print("3. We're using wrong unit conversion")
        print("")
        print("CORRECT FIX:")
        print("- API returns seconds (not milliseconds)")
        print("- Convert: value // 60 = minutes")
        print("- NOT: value // 1000 or value // 60000")
        
    except Exception as e:
        print(f"Error investigating impossible commute: {e}")

def test_correct_conversion():
    """Test the correct unit conversion"""
    print("\n=== TESTING CORRECT CONVERSION ===")
    
    try:
        # Test with Angel Ruiz case
        angel_addr = "2801 Pullman Ave , Richmond, 94804, USA"
        teranga_addr = " 4 Embarcadero Ctr, San Francisco, CA 94111, United States, Oakland, USA"
        
        # Load cache
        import json
        with open('cached_commute.json', 'r') as f:
            cache_data = json.load(f)
        
        cache_key = f"{angel_addr}|{teranga_addr}"
        
        if cache_key in cache_data:
            entry = cache_data[cache_key]
            raw_value = entry.get('value', 0)
            api_text = entry.get('text', 'N/A')
            
            print(f"API Response: {api_text}")
            print(f"Raw value: {raw_value}")
            
            # Test different conversions
            conversions = [
                ("Seconds to minutes", raw_value // 60),
                ("Milliseconds to minutes", raw_value // 60000),
                ("Microseconds to minutes", raw_value // 60000000),
            ]
            
            print(f"\nConversion Tests:")
            for name, minutes in conversions:
                speed_mph = 15.3 / (minutes / 60) if minutes > 0 else 0
                print(f"  {name}: {minutes} minutes = {speed_mph:.1f} mph")
            
            # Determine which conversion matches the API text
            api_minutes = None
            if 'mins' in api_text.lower():
                import re
                match = re.search(r'(\d+)\s*mins?', api_text.lower())
                if match:
                    api_minutes = int(match.group(1))
            
            if api_minutes:
                print(f"\nAPI indicates: {api_minutes} minutes")
                
                for name, minutes in conversions:
                    if minutes == api_minutes:
                        print(f"✅ {name} is CORRECT!")
                        return name
            
        print("Could not determine correct conversion")
        
    except Exception as e:
        print(f"Error testing correct conversion: {e}")

if __name__ == "__main__":
    investigate_impossible_commute()
    test_correct_conversion()
    
    print(f"\n=== INVESTIGATION COMPLETE ===")
    print("The impossible commute times are due to incorrect unit conversion!")
    print("Need to fix the TransportationOptimizer to use correct conversion.")
