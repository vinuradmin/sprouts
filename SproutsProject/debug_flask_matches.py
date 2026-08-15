#!/usr/bin/env python3
"""
Debug why Flask Hungarian algorithm is matching interns with no availability overlap
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant, User

def debug_flask_match(intern_name, restaurant_name):
    """Debug a specific Flask match"""
    app = create_app()
    app.app_context().push()
    
    # Find intern and restaurant
    intern = Intern.query.join(User).filter(User.full_name == intern_name).first()
    restaurant = Restaurant.query.filter(Restaurant.name == restaurant_name).first()
    
    if not intern:
        print(f"Intern not found: {intern_name}")
        return
    
    if not restaurant:
        print(f"Restaurant not found: {restaurant_name}")
        return
    
    print(f"=== DEBUGGING: {intern_name} -> {restaurant_name} ===")
    
    service = HungarianMatchingService()
    
    # Parse availability using Flask's method
    intern_avail = service._parse_intern_availability(intern)
    restaurant_avail = service._parse_restaurant_availability(restaurant)
    
    print(f"\nFlask parsed intern availability:")
    for day, avail in intern_avail.items():
        if avail:
            print(f"  {day}: {avail}")
    
    print(f"\nFlask parsed restaurant availability:")
    for day, avail in restaurant_avail.items():
        if avail:
            print(f"  {day}: {avail}")
    
    # Calculate overlap using Flask's method
    total_hours, schedule = service._calculate_weekly_overlap(intern_avail, restaurant_avail)
    print(f"\nFlask overlap calculation:")
    print(f"Total hours: {total_hours}")
    print(f"Schedule: {schedule}")
    
    # Check commute
    try:
        commute = service.commute_cache.get_commute(
            intern.transportation_method or 'driving',
            intern.get_full_address(),
            restaurant.get_full_address()
        )
        print(f"\nCommute: {commute.minutes} minutes")
    except Exception as e:
        print(f"Commute error: {e}")
    
    # Check intern and restaurant details
    print(f"\nIntern details:")
    print(f"  Address: {intern.get_full_address()}")
    print(f"  Transportation: {intern.transportation_method}")
    print(f"  Max commute: {intern.max_commute_minutes}")
    
    print(f"\nRestaurant details:")
    print(f"  Address: {restaurant.get_full_address()}")
    print(f"  Age restriction: {restaurant.age_restriction}")
    print(f"  Max interns: {restaurant.max_interns}")

def main():
    """Debug the mismatched cases"""
    # Use exact names from actual Flask matches
    mismatches = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga ")
    ]
    
    for intern_name, restaurant_name in mismatches:
        print(f"Trying to find: '{intern_name}' -> '{restaurant_name}'")
        debug_flask_match(intern_name, restaurant_name)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
