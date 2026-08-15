#!/usr/bin/env python3
"""
Debug geographic distances - Tarts de Feybesse vs UC Berkeley
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_geographic_distances():
    """Debug geographic distances between key locations"""
    print("="*80)
    print("DEBUGGING GEOGRAPHIC DISTANCES")
    print("Tarts de Feybesse vs UC Berkeley - should be close!")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Find Jesus
        jesus_intern = None
        for intern in Intern.query.filter_by(is_seeking_internship=True).all():
            if 'Jesus' in intern.user.full_name:
                jesus_intern = intern
                break
        
        if not jesus_intern:
            print("Jesus not found")
            return
        
        print(f"Jesus address: {jesus_intern.get_full_address()}")
        
        # Get key restaurants
        tarts_restaurant = Restaurant.query.filter_by(name='Tarts de Feybesse').first()
        uc_berkeley_restaurant = Restaurant.query.filter_by(name='UC Berkeley').first()
        burdell_restaurant = Restaurant.query.filter_by(name='Burdell').first()
        
        restaurants = {
            'Tarts de Feybesse': tarts_restaurant,
            'UC Berkeley': uc_berkeley_restaurant,
            'Burdell': burdell_restaurant
        }
        
        print(f"\n" + "="*60)
        print("RESTAURANT ADDRESSES")
        print("="*60)
        
        for name, restaurant in restaurants.items():
            if restaurant:
                print(f"{name}: {restaurant.get_full_address()}")
            else:
                print(f"{name}: NOT FOUND")
        
        print(f"\n" + "="*60)
        print("COMMUTES FROM JESUS TO EACH RESTAURANT")
        print("="*60)
        
        for name, restaurant in restaurants.items():
            if restaurant:
                commute = optimizer.get_optimal_commute(
                    jesus_intern.get_full_address(),
                    restaurant.get_full_address(),
                    'driving'
                )
                print(f"Jesus -> {name}: {commute} minutes")
        
        print(f"\n" + "="*60)
        print("COMMUTES BETWEEN RESTAURANTS")
        print("="*60)
        
        # Test commutes between restaurants
        restaurant_pairs = [
            ('Tarts de Feybesse', 'UC Berkeley'),
            ('Tarts de Feybesse', 'Burdell'),
            ('UC Berkeley', 'Burdell')
        ]
        
        for rest1_name, rest2_name in restaurant_pairs:
            rest1 = restaurants[rest1_name]
            rest2 = restaurants[rest2_name]
            
            if rest1 and rest2:
                commute = optimizer.get_optimal_commute(
                    rest1.get_full_address(),
                    rest2.get_full_address(),
                    'driving'
                )
                print(f"{rest1_name} -> {rest2_name}: {commute} minutes")
        
        print(f"\n" + "="*60)
        print("CHECKING CACHE VALUES")
        print("="*60)
        
        # Check cache for Jesus to each restaurant
        for name, restaurant in restaurants.items():
            if restaurant:
                cache_key = f"{jesus_intern.get_full_address()}|{restaurant.get_full_address()}"
                has_cache = optimizer.commute_cache.has_cached_commute(
                    jesus_intern.get_full_address(),
                    restaurant.get_full_address()
                )
                print(f"{name} in cache: {has_cache}")
                print(f"  Cache key: {cache_key}")
                
                if has_cache:
                    # Get the cached value
                    try:
                        import json
                        with open('cached_commute.json', 'r') as f:
                            cache = json.load(f)
                        
                        if cache_key in cache:
                            cached_data = cache[cache_key]
                            seconds = cached_data['value']
                            minutes = round(seconds / 60)
                            print(f"  Cached: {seconds} seconds = {minutes} minutes")
                            print(f"  Text: {cached_data['text']}")
                    except Exception as e:
                        print(f"  Error reading cache: {e}")
        
        print(f"\n" + "="*60)
        print("GEOGRAPHIC REALITY CHECK")
        print("="*60)
        
        print("Expected distances:")
        print("- San Jose to Oakland: ~45-60 minutes")
        print("- San Jose to Berkeley: ~45-60 minutes") 
        print("- Oakland to Berkeley: ~15-25 minutes")
        print("- Tarts de Feybesse (Oakland) to UC Berkeley: ~15-25 minutes")
        
        return restaurants
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    """Main function"""
    restaurants = debug_geographic_distances()
    
    print(f"\n" + "="*80)
    print("GEOGRAPHIC DISTANCES DEBUG COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
