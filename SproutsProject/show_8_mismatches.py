#!/usr/bin/env python3
"""
Show the 8 Flask matches that weren't in original CSV with their overlap details
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant, User

def show_8_mismatches():
    """Show the 8 mismatched cases with overlap details"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    # Run matching algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    
    # The 8 mismatches from our verification
    mismatched_restaurants = {
        "Angel Ruiz": "Abaca ",
        "Shelsea Vasquez": "Teranga ",
        "Asslin Espinal": "Ssal",
        "Giovanni Giacomazzi": "Ssal", 
        "Eljanae Robinson": "Teranga ",
        "Andrea Caballero ": "Tarts de Feybesse",
        "Cristina Cubias ": "alaMar Dominican Kitchen",
        "Maryam Washington": "alaMar Dominican Kitchen"
    }
    
    print("=== THE 8 FLASK MATCHES NOT IN ORIGINAL CSV ===\n")
    
    count = 0
    for assignment in matches.get('assignments', []):
        intern_id = assignment.get('intern_id')
        intern = Intern.query.get(intern_id)
        
        if intern:
            intern_name = intern.user.full_name
            restaurant_id = assignment.get('restaurant_id')
            restaurant = Restaurant.query.get(restaurant_id)
            
            if restaurant and intern_name in mismatched_restaurants:
                count += 1
                total_hours = assignment.get('total_hours', 0)
                score = assignment.get('match_score', 0)
                
                print(f"{count}. {intern_name} -> {restaurant.name}")
                print(f"   Total Overlap: {total_hours} hours")
                print(f"   Match Score: {score}")
                
                # Get detailed overlap schedule
                intern_avail = service._parse_intern_availability(intern)
                restaurant_avail = service._parse_restaurant_availability(restaurant)
                overlap_hours, schedule = service._calculate_weekly_overlap(intern_avail, restaurant_avail)
                
                print(f"   Schedule:")
                for day, slots in schedule.items():
                    if slots:
                        for slot in slots:
                            print(f"     {day}: {slot['start']}-{slot['end']} ({slot['duration']} hrs)")
                
                # Get commute info
                try:
                    commute = service.commute_cache.get_commute(
                        intern.transportation_method or 'driving',
                        intern.get_full_address(),
                        restaurant.get_full_address()
                    )
                    print(f"   Commute: {commute.minutes} minutes")
                except Exception as e:
                    print(f"   Commute: Error - {e}")
                
                print()
    
    print(f"Total: {count} matches shown")

if __name__ == "__main__":
    show_8_mismatches()
