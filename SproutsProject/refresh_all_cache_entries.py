#!/usr/bin/env python3
"""
Refresh all cache entries with fresh Google API calls
To ensure consistent traffic data across all entries
"""

import sys
import os
import json
import time
from datetime import datetime

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def refresh_all_cache_entries():
    """Refresh all cache entries with fresh Google API calls"""
    print("="*80)
    print("REFRESHING ALL CACHE ENTRIES")
    print("Updating with fresh Google API calls for consistent traffic data")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.commute_service import CommuteService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Load current cache
        cache_file = 'cached_commute.json'
        try:
            with open(cache_file, 'r') as f:
                current_cache = json.load(f)
        except FileNotFoundError:
            print("No existing cache file found")
            return
        
        print(f"Current cache has {len(current_cache)} entries")
        
        # Get all unique addresses from cache
        all_addresses = set()
        for cache_key in current_cache.keys():
            origin, destination = cache_key.split('|')
            all_addresses.add(origin)
            all_addresses.add(destination)
        
        print(f"Found {len(all_addresses)} unique addresses")
        
        # Create fresh cache
        fresh_cache = {}
        service = CommuteService()
        
        print(f"\n" + "="*60)
        print("REFRESHING CACHE ENTRIES")
        print("="*60)
        
        # Process all unique address pairs
        address_list = list(all_addresses)
        total_pairs = len(address_list) * len(address_list)
        processed = 0
        errors = 0
        
        for i, origin in enumerate(address_list):
            for j, destination in enumerate(address_list):
                if i == j:  # Skip same address
                    continue
                
                cache_key = f"{origin}|{destination}"
                processed += 1
                
                try:
                    # Get fresh commute data
                    result = service.calculate_commute_time('driving', origin, destination)
                    
                    # Store in fresh cache
                    fresh_cache[cache_key] = result.to_dict()
                    
                    # Progress update
                    if processed % 50 == 0:
                        progress = (processed / total_pairs) * 100
                        print(f"Progress: {processed}/{total_pairs} ({progress:.1f}%) - Last: {result.text}")
                    
                    # Rate limiting to avoid API limits
                    time.sleep(0.1)  # 100ms between calls
                    
                except Exception as e:
                    errors += 1
                    print(f"Error processing {cache_key}: {e}")
                    # Keep old value if available
                    if cache_key in current_cache:
                        fresh_cache[cache_key] = current_cache[cache_key]
        
        print(f"\nCache refresh complete:")
        print(f"  Processed: {processed} pairs")
        print(f"  Errors: {errors}")
        print(f"  Success rate: {((processed - errors) / processed * 100):.1f}%")
        
        # Backup old cache
        backup_file = f"cached_commute_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(current_cache, f, indent=4)
            print(f"  Old cache backed up to: {backup_file}")
        except Exception as e:
            print(f"  Error backing up cache: {e}")
        
        # Save fresh cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(fresh_cache, f, indent=4)
            print(f"  Fresh cache saved to: {cache_file}")
        except Exception as e:
            print(f"  Error saving fresh cache: {e}")
        
        return fresh_cache
        
    except Exception as e:
        print(f"Error refreshing cache: {e}")
        return {}

def refresh_intern_restaurant_pairs_only():
    """Refresh only intern-restaurant pairs (more efficient)"""
    print("="*80)
    print("REFRESHING INTERN-RESTAURANT PAIRS ONLY")
    print("More efficient approach - only refresh needed pairs")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.commute_service import CommuteService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get all interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        print(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Create fresh cache for intern-restaurant pairs
        fresh_cache = {}
        service = CommuteService()
        
        print(f"\n" + "="*60)
        print("REFRESHING INTERN-RESTAURANT COMMUTES")
        print("="*60)
        
        total_pairs = len(interns) * len(restaurants)
        processed = 0
        errors = 0
        
        for intern in interns:
            intern_address = intern.get_full_address()
            
            for restaurant in restaurants:
                restaurant_address = restaurant.get_full_address()
                
                # Skip if same address
                if intern_address == restaurant_address:
                    continue
                
                cache_key = f"{intern_address}|{restaurant_address}"
                processed += 1
                
                try:
                    # Get fresh commute data
                    result = service.calculate_commute_time('driving', intern_address, restaurant_address)
                    
                    # Store in fresh cache
                    fresh_cache[cache_key] = result.to_dict()
                    
                    # Progress update
                    if processed % 20 == 0:
                        progress = (processed / total_pairs) * 100
                        print(f"Progress: {processed}/{total_pairs} ({progress:.1f}%) - {intern.user.full_name} -> {restaurant.name}: {result.text}")
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    errors += 1
                    if processed % 20 == 0 or errors <= 5:
                        print(f"Error {intern.user.full_name} -> {restaurant.name}: {e}")
        
        print(f"\nIntern-restaurant refresh complete:")
        print(f"  Processed: {processed} pairs")
        print(f"  Errors: {errors}")
        print(f"  Success rate: {((processed - errors) / processed * 100):.1f}%")
        
        # Load existing cache and merge
        cache_file = 'cached_commute.json'
        existing_cache = {}
        
        try:
            with open(cache_file, 'r') as f:
                existing_cache = json.load(f)
        except FileNotFoundError:
            print("No existing cache file")
        
        # Backup old cache
        if existing_cache:
            backup_file = f"cached_commute_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w') as f:
                    json.dump(existing_cache, f, indent=4)
                print(f"  Old cache backed up to: {backup_file}")
            except Exception as e:
                print(f"  Error backing up cache: {e}")
        
        # Merge fresh data with existing cache
        merged_cache = existing_cache.copy()
        merged_cache.update(fresh_cache)
        
        # Save merged cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(merged_cache, f, indent=4)
            print(f"  Updated cache saved to: {cache_file}")
            print(f"  Total cache entries: {len(merged_cache)}")
        except Exception as e:
            print(f"  Error saving cache: {e}")
        
        return merged_cache
        
    except Exception as e:
        print(f"Error refreshing intern-restaurant pairs: {e}")
        return {}

def verify_cache_consistency():
    """Verify cache consistency after refresh"""
    print("="*80)
    print("VERIFYING CACHE CONSISTENCY")
    print("Checking for consistent traffic patterns")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Test some key routes
        test_cases = [
            ("Jesus Chavez", "Tarts de Feybesse"),
            ("Jesus Chavez", "UC Berkeley"),
            ("Jesus Chavez", "Burdell"),
            ("Kaylin Lewis", "2 Chix"),
            ("Enrique Marroquin", "Mago")
        ]
        
        print("Testing key routes after cache refresh:")
        
        for intern_name, restaurant_name in test_cases:
            # Find intern and restaurant
            intern = None
            for i in Intern.query.filter_by(is_seeking_internship=True).all():
                if intern_name in i.user.full_name:
                    intern = i
                    break
            
            restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
            
            if intern and restaurant:
                commute = optimizer.get_optimal_commute(
                    intern.get_full_address(),
                    restaurant.get_full_address(),
                    'driving'
                )
                print(f"  {intern_name} -> {restaurant_name}: {commute} minutes")
            else:
                print(f"  {intern_name} -> {restaurant_name}: NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"Error verifying cache: {e}")
        return False

def main():
    """Main function"""
    print("Running comprehensive cache refresh...")
    refresh_all_cache_entries()
    
    print(f"\n" + "="*80)
    verify_cache_consistency()

if __name__ == "__main__":
    main()
