#!/usr/bin/env python3
"""
Debug CSV parsing for Angel Ruiz and Abaca
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def debug_csv_parsing():
    """Debug CSV parsing for specific case"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    
    # Find Angel Ruiz
    intern = None
    for i in Intern.query.all():
        if "Angel Ruiz" in i.user.full_name:
            intern = i
            break
    
    if not intern:
        print("Angel Ruiz not found")
        return
    
    # Find Abaca
    restaurant = None
    for r in Restaurant.query.all():
        if "Abaca" in r.name:
            restaurant = r
            break
    
    if not restaurant:
        print("Abaca not found")
        return
    
    print(f"Testing: {intern.user.full_name} -> {restaurant.name}")
    print(f"Restaurant name in DB: '{restaurant.name}'")
    
    # Parse intern availability
    intern_avail = service._parse_intern_availability(intern)
    print(f"\nIntern availability:")
    for day, slots in intern_avail.items():
        if slots:
            print(f"  {day}: {len(slots)} slots")
            for slot in slots:
                print(f"    {slot}")
    
    # Parse restaurant availability
    print(f"\nLooking for restaurant: '{restaurant.name}'")
    
    restaurant_avail = service._parse_restaurant_availability(restaurant)
    print(f"Restaurant availability found: {len(restaurant_avail)} days")
    for day, slots in restaurant_avail.items():
        if slots:
            print(f"  {day}: {len(slots)} slots")
            for slot in slots:
                print(f"    {slot}")
    
    # If no slots found, try fallback
    if not any(restaurant_avail.values()):
        print("No restaurant availability found - using fallback")
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            restaurant_avail[day] = [Slot("9AM-9PM")]
    
    print(f"\nFinal restaurant availability:")
    for day, slots in restaurant_avail.items():
        if slots:
            print(f"  {day}: {len(slots)} slots")
            for slot in slots:
                print(f"    {slot}")
    
    # Check overlap for Monday specifically
    print(f"\nMonday overlap details:")
    intern_slots = intern_avail.get('Monday', [])
    restaurant_slots = restaurant_avail.get('Monday', [])
    
    print(f"Intern slots: {intern_slots}")
    print(f"Restaurant slots: {restaurant_slots}")
    
    for intern_slot in intern_slots:
        for rest_slot in restaurant_slots:
            overlap = intern_slot.get_overlap(rest_slot)
            if overlap:
                print(f"  OVERLAP: {intern_slot} + {rest_slot} = {overlap} ({overlap.duration()} hrs)")
            else:
                print(f"  NO OVERLAP: {intern_slot} + {rest_slot}")

if __name__ == "__main__":
    debug_csv_parsing()
