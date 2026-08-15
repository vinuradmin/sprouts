#!/usr/bin/env python3
"""
Debug availability parsing and slot overlap calculation
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def debug_availability_parsing():
    """Debug what's happening with availability parsing"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    
    # Test Angel Ruiz specifically
    print("=== DEBUGGING AVAILABILITY PARSING ===")
    
    # Find Angel Ruiz
    intern = None
    for i in Intern.query.all():
        if "Angel Ruiz" in i.user.full_name:
            intern = i
            break
    
    if not intern:
        print("Angel Ruiz not found")
        return
    
    print(f"Intern: {intern.user.full_name}")
    
    # Parse intern availability
    intern_avail = service._parse_intern_availability(intern)
    print(f"\nIntern availability parsed:")
    for day, slots in intern_avail.items():
        if slots:
            print(f"  {day}: {len(slots)} slots")
            for slot in slots:
                print(f"    {slot}")
    
    # Test with a few restaurants
    test_restaurants = ["Abaca ", "Snail Bar", "The Holbrook House"]
    
    for rest_name in test_restaurants:
        restaurant = None
        for r in Restaurant.query.all():
            if rest_name.strip() in r.name.strip():
                restaurant = r
                break
        
        if not restaurant:
            continue
        
        print(f"\n--- Testing with {restaurant.name} ---")
        
        # Parse restaurant availability
        restaurant_avail = service._parse_restaurant_availability(restaurant)
        print(f"Restaurant availability:")
        for day, slots in restaurant_avail.items():
            if slots:
                print(f"  {day}: {len(slots)} slots")
                for slot in slots:
                    print(f"    {slot}")
        
        # Check overlap for each day
        total_overlap = 0
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            intern_slots = intern_avail.get(day, [])
            restaurant_slots = restaurant_avail.get(day, [])
            
            if intern_slots and restaurant_slots:
                print(f"\n{day} overlap:")
                for intern_slot in intern_slots:
                    for rest_slot in restaurant_slots:
                        overlap = intern_slot.get_overlap(rest_slot)
                        if overlap:
                            hours = overlap.duration()
                            total_overlap += hours
                            print(f"  {intern_slot} + {rest_slot} = {overlap} ({hours} hrs)")
                        else:
                            print(f"  {intern_slot} + {rest_slot} = NO OVERLAP")
        
        print(f"Total overlap: {total_overlap} hours")

if __name__ == "__main__":
    debug_availability_parsing()
