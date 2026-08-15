#!/usr/bin/env python3
"""
Debug specific Flask matches by ID
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant, User

def debug_by_id():
    """Debug Flask matches by database ID"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    # Run matching algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    
    # Debug first few matches by ID
    for i, assignment in enumerate(matches.get('assignments', [])[:3], 1):
        intern_id = assignment.get('intern_id')
        restaurant_id = assignment.get('restaurant_id')
        
        intern = Intern.query.get(intern_id)
        restaurant = Restaurant.query.get(restaurant_id)
        
        if intern and restaurant:
            print(f"=== MATCH {i}: ID {intern_id} -> ID {restaurant_id} ===")
            print(f"Intern: '{intern.user.full_name}' (ID: {intern_id})")
            print(f"Restaurant: '{restaurant.name}' (ID: {restaurant_id})")
            
            # Parse availability using Flask's method
            intern_avail = service._parse_intern_availability(intern)
            restaurant_avail = service._parse_restaurant_availability(restaurant)
            
            print(f"\nIntern availability:")
            for day, avail in intern_avail.items():
                if avail:
                    print(f"  {day}: {avail}")
            
            print(f"\nRestaurant availability:")
            for day, avail in restaurant_avail.items():
                if avail:
                    print(f"  {day}: {avail}")
            
            # Calculate overlap
            total_hours, schedule = service._calculate_weekly_overlap(intern_avail, restaurant_avail)
            print(f"\nOverlap: {total_hours} hours")
            print(f"Schedule: {schedule}")
            
            print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    debug_by_id()
