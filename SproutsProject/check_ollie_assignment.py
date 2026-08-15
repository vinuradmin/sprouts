#!/usr/bin/env python3
"""
Check what our Hungarian algorithm assigned to Ollie
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def check_ollie_assignment():
    """Check Ollie's assignment in Hungarian algorithm"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print("=== CHECKING OLLIE'S HUNGARIAN ASSIGNMENT ===")
    
    # Find Ollie
    ollie = None
    for intern in interns:
        if 'Ollie' in intern.user.full_name:
            ollie = intern
            print(f"Found Ollie: '{intern.user.full_name}' (ID: {intern.id})")
            break
    
    if not ollie:
        print("Ollie not found")
        return
    
    # Run algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    assignments = matches.get('assignments', [])
    
    # Find Ollie's assignment
    ollie_assignment = None
    for assignment in assignments:
        if assignment.get('intern_id') == ollie.id:
            ollie_assignment = assignment
            break
    
    if ollie_assignment:
        print(f"\nOllie's Hungarian assignment:")
        print(f"  Restaurant: {ollie_assignment.get('restaurant_name')}")
        print(f"  Commute: {ollie_assignment.get('commute_minutes')} minutes")
        print(f"  Hours: {ollie_assignment.get('total_overlap_hours')}")
        print(f"  Days: {ollie_assignment.get('days_matched')}")
    else:
        print(f"\nOllie was not assigned by Hungarian algorithm")
    
    # Check all valid matches for Ollie
    print(f"\nAll valid matches for Ollie:")
    valid_matches = []
    for restaurant in restaurants:
        match = service._evaluate_match(ollie, restaurant, 50, 12)
        if match:
            valid_matches.append((restaurant.name, match['commute_minutes'], match['total_overlap_hours']))
    
    # Sort by commute time
    valid_matches.sort(key=lambda x: x[1])
    
    for i, (rest_name, commute, hours) in enumerate(valid_matches, 1):
        print(f"  {i}. {rest_name}: {commute} mins, {hours} hrs")

if __name__ == "__main__":
    check_ollie_assignment()
