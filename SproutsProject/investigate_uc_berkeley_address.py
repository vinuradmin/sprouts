#!/usr/bin/env python3
"""
Investigate UC Berkeley address - why 118 minutes?
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_uc_berkeley_address():
    """Investigate UC Berkeley address issue"""
    print("="*80)
    print("INVESTIGATING UC BERKELEY ADDRESS")
    print("Why 118 minutes from San Jose?")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Get UC Berkeley restaurant
        uc_berkeley_restaurant = Restaurant.query.filter_by(name='UC Berkeley').first()
        
        print(f"UC Berkeley restaurant found: {uc_berkeley_restaurant is not None}")
        if uc_berkeley_restaurant:
            print(f"Name: {uc_berkeley_restaurant.name}")
            print(f"Address: {uc_berkeley_restaurant.address}")
            print(f"Full address: {uc_berkeley_restaurant.get_full_address()}")
            print(f"City: {uc_berkeley_restaurant.city}")
            print(f"State: {uc_berkeley_restaurant.state}")
        
        # Test with different Berkeley addresses
        test_addresses = [
            "UC Berkeley Campus, Berkeley, CA",
            "Berkeley, CA",
            "University of California, Berkeley, CA",
            "Telegraph Ave, Berkeley, CA",
            "Downtown Berkeley, Berkeley, CA"
        ]
        
        print(f"\n" + "="*60)
        print("TESTING DIFFERENT BERKELEY ADDRESSES")
        print("="*60)
        
        jesus_address = "4271 N First St, San Jose, 95134, USA"
        
        for test_addr in test_addresses:
            try:
                commute = optimizer.get_optimal_commute(
                    jesus_address,
                    test_addr,
                    'driving'
                )
                print(f"Jesus -> {test_addr}: {commute} minutes")
            except Exception as e:
                print(f"Jesus -> {test_addr}: ERROR - {e}")
        
        # Check what's in the cache for UC Berkeley
        print(f"\n" + "="*60)
        print("CHECKING CACHE FOR UC BERKELEY")
        print("="*60)
        
        try:
            import json
            with open('cached_commute.json', 'r') as f:
                cache = json.load(f)
            
            # Find all cache entries with Berkeley
            berkeley_keys = [k for k in cache.keys() if 'Berkeley' in k]
            print(f"Found {len(berkeley_keys)} Berkeley cache entries:")
            
            for key in berkeley_keys[:5]:  # Show first 5
                data = cache[key]
                seconds = data['value']
                minutes = round(seconds / 60)
                print(f"  {key}")
                print(f"    {data['text']} ({seconds} seconds = {minutes} minutes)")
        
        except Exception as e:
            print(f"Error checking cache: {e}")
        
        # Test the actual Google Maps API call
        print(f"\n" + "="*60)
        print("TESTING FRESH GOOGLE MAPS API CALL")
        print("="*60)
        
        try:
            from app.services.commute_service import CommuteService
            
            service = CommuteService()
            
            # Test with current UC Berkeley address
            if uc_berkeley_restaurant:
                result = service.calculate_commute_time(
                    'driving',
                    jesus_address,
                    uc_berkeley_restaurant.get_full_address()
                )
                print(f"Fresh API call to UC Berkeley:")
                print(f"  Text: {result.text}")
                print(f"  Value: {result.value} seconds")
                print(f"  Minutes: {round(result.value / 60)}")
            
            # Test with a better Berkeley address
            result2 = service.calculate_commute_time(
                'driving',
                jesus_address,
                "University of California, Berkeley, CA 94720"
            )
            print(f"\nFresh API call to better Berkeley address:")
            print(f"  Text: {result2.text}")
            print(f"  Value: {result2.value} seconds")
            print(f"  Minutes: {round(result2.value / 60)}")
            
        except Exception as e:
            print(f"Error with fresh API call: {e}")
        
        return uc_berkeley_restaurant
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function"""
    restaurant = investigate_uc_berkeley_address()
    
    print(f"\n" + "="*80)
    print("UC BERKELEY ADDRESS INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
