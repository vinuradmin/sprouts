#!/usr/bin/env python3
"""
Debug weekly overlap calculation
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def debug_weekly_overlap():
    """Debug weekly overlap calculation"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    
    # Find Angel Ruiz and Abaca
    intern = None
    for i in Intern.query.all():
        if "Angel Ruiz" in i.user.full_name:
            intern = i
            break
    
    restaurant = None
    for r in Restaurant.query.all():
        if "Abaca" in r.name:
            restaurant = r
            break
    
    if not intern or not restaurant:
        print("Not found")
        return
    
    print(f"Testing: {intern.user.full_name} -> {restaurant.name}")
    
    # Get availability
    intern_avail = service._parse_intern_availability(intern)
    restaurant_avail = service._parse_restaurant_availability(restaurant)
    
    # Calculate weekly overlap using the service method
    total_hours, schedule = service._calculate_weekly_overlap(intern_avail, restaurant_avail)
    
    print(f"\nWeekly overlap result:")
    print(f"Total hours: {total_hours}")
    print(f"Schedule: {schedule}")
    
    # Manual calculation for verification
    manual_total = 0
    manual_schedule = {}
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        intern_slots = intern_avail.get(day, [])
        restaurant_slots = restaurant_avail.get(day, [])
        
        day_overlaps = []
        for intern_slot in intern_slots:
            for rest_slot in restaurant_slots:
                overlap = intern_slot.get_overlap(rest_slot)
                if overlap:
                    day_overlaps.append(overlap)
                    manual_total += overlap.duration()
        
        if day_overlaps:
            manual_schedule[day] = [slot.to_dict() for slot in day_overlaps]
    
    print(f"\nManual calculation:")
    print(f"Total hours: {manual_total}")
    print(f"Schedule: {manual_schedule}")

if __name__ == "__main__":
    debug_weekly_overlap()
