#!/usr/bin/env python3
"""
Debug the refreshed cache - why some routes return None
"""

import sys
import os
import json

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_refreshed_cache():
    """Debug why some routes return None after cache refresh"""
    print("="*80)
    print("DEBUGGING REFRESHED CACHE")
    print("Why some routes return None after refresh")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Find Jesus and test restaurants
        jesus_intern = None
        for intern in Intern.query.filter_by(is_seeking_internship=True).all():
            if 'Jesus' in intern.user.full_name:
                jesus_intern = intern
                break
        
        test_restaurants = ['Tarts de Feybesse', 'UC Berkeley', 'Burdell']
        
        print(f"Jesus intern found: {jesus_intern is not None}")
        if jesus_intern:
            print(f"Jesus address: {jesus_intern.get_full_address()}")
        
        print(f"\n" + "="*60)
        print("TESTING CACHE LOOKUP")
        print("="*60)
        
        for rest_name in test_restaurants:
            restaurant = Restaurant.query.filter_by(name=rest_name).first()
            if restaurant:
                print(f"\n{rest_name}:")
                print(f"  Restaurant address: {restaurant.get_full_address()}")
                
                # Check cache
                cache_key = f"{jesus_intern.get_full_address()}|{restaurant.get_full_address()}"
                has_cache = optimizer.commute_cache.has_cached_commute(
                    jesus_intern.get_full_address(),
                    restaurant.get_full_address()
                )
                print(f"  In cache: {has_cache}")
                print(f"  Cache key: {cache_key}")
                
                if has_cache:
                    # Get cached value
                    try:
                        with open('cached_commute.json', 'r') as f:
                            cache = json.load(f)
                        
                        if cache_key in cache:
                            cached_data = cache[cache_key]
                            seconds = cached_data['value']
                            minutes = round(seconds / 60)
                            print(f"  Cached: {seconds} seconds = {minutes} minutes")
                            print(f"  Text: {cached_data['text']}")
                        else:
                            print(f"  Cache key not found in file")
                    except Exception as e:
                        print(f"  Error reading cache: {e}")
                
                # Test commute calculation
                try:
                    commute = optimizer.get_optimal_commute(
                        jesus_intern.get_full_address(),
                        restaurant.get_full_address(),
                        'driving'
                    )
                    print(f"  Commute result: {commute} minutes")
                except Exception as e:
                    print(f"  Commute error: {e}")
            else:
                print(f"\n{rest_name}: NOT FOUND")
        
        # Check cache file size and some entries
        print(f"\n" + "="*60)
        print("CACHE FILE ANALYSIS")
        print("="*60)
        
        try:
            with open('cached_commute.json', 'r') as f:
                cache = json.load(f)
            
            print(f"Total cache entries: {len(cache)}")
            
            # Check some Jesus entries
            jesus_entries = [k for k in cache.keys() if '4271 N First St' in k]
            print(f"Jesus-related entries: {len(jesus_entries)}")
            
            # Show a few Jesus entries
            for i, key in enumerate(jesus_entries[:5]):
                data = cache[key]
                seconds = data['value']
                minutes = round(seconds / 60)
                print(f"  {key[:50]}... -> {minutes} min ({data['text']})")
        
        except Exception as e:
            print(f"Error analyzing cache: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error debugging cache: {e}")
        return False

def main():
    """Main function"""
    debug_refreshed_cache()

if __name__ == "__main__":
    main()
