#!/usr/bin/env python3
"""
Check what the Flask Hungarian algorithm actually matched
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def check_actual_flask_matches():
    """Get the actual Flask matches"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
    
    # Run matching algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    
    print(f"\n=== ACTUAL FLASK MATCHES ===")
    for i, assignment in enumerate(matches.get('assignments', []), 1):
        intern_id = assignment.get('intern_id')
        intern = Intern.query.get(intern_id)
        if intern:
            intern_name = intern.user.full_name
            restaurant_id = assignment.get('restaurant_id')
            restaurant = Restaurant.query.get(restaurant_id)
            if restaurant:
                total_hours = assignment.get('total_hours', 0)
                score = assignment.get('match_score', 0)
                print(f"{i:2d}. '{intern_name}' -> '{restaurant.name}' (Hours: {total_hours}, Score: {score})")
    
    return matches

if __name__ == "__main__":
    check_actual_flask_matches()
