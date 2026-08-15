#!/usr/bin/env python3
"""
Test if Sorrel Restaurant fix works for Ollie
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def test_sorrel_fix():
    """Test if Sorrel Restaurant is now valid for Ollie"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print("=== TESTING SORREL RESTAURANT FIX ===")
    
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
    
    # Find Sorrel Restaurant
    sorrel = None
    for restaurant in restaurants:
        if 'Sorrel' in restaurant.name:
            sorrel = restaurant
            print(f"Found Sorrel: '{restaurant.name}' (ID: {restaurant.id})")
            break
    
    if not sorrel:
        print("Sorrel not found")
        return
    
    # Test the match
    print(f"\nTesting Ollie -> Sorrel Restaurant:")
    match = service._evaluate_match(ollie, sorrel, 50, 12)
    
    if match:
        print(f"  ✅ VALID MATCH FOUND!")
        print(f"  Commute: {match['commute_minutes']} minutes")
        print(f"  Hours: {match['total_overlap_hours']}")
        print(f"  Days: {match['days_matched']}")
        print(f"  Score: {match['match_score']}")
    else:
        print(f"  ❌ STILL INVALID MATCH")
    
    # Check all valid matches for Ollie again
    print(f"\nAll valid matches for Ollie (after fix):")
    valid_matches = []
    for restaurant in restaurants:
        match = service._evaluate_match(ollie, restaurant, 50, 12)
        if match:
            valid_matches.append((restaurant.name, match['commute_minutes'], match['total_overlap_hours']))
    
    # Sort by commute time
    valid_matches.sort(key=lambda x: x[1])
    
    for i, (rest_name, commute, hours) in enumerate(valid_matches, 1):
        marker = "★" if 'Sorrel' in rest_name else "  "
        print(f"{marker} {i}. {rest_name}: {commute} mins, {hours} hrs")

if __name__ == "__main__":
    test_sorrel_fix()
