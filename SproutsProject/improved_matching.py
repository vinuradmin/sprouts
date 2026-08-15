#!/usr/bin/env python3
"""
Test improved matching that only generates valid matches from the start
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def test_improved_matching():
    """Test improved matching logic"""
    app = create_app()
    app.app_context().push()
    
    print("=== TESTING IMPROVED MATCHING LOGIC ===")
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
    
    # Test specific cases to see what's happening
    test_cases = [
        ("Angel Ruiz", "Abaca "),
        ("Shelsea Vasquez", "Teranga "),
        ("Asslin Espinal", "Ssal")
    ]
    
    for intern_name, restaurant_name in test_cases:
        print(f"\n--- Testing: {intern_name} -> {restaurant_name} ---")
        
        # Find intern and restaurant
        intern = None
        for i in interns:
            if intern_name in i.user.full_name:
                intern = i
                break
        
        restaurant = None
        for r in restaurants:
            if restaurant_name.strip() in r.name.strip():
                restaurant = r
                break
        
        if not intern or not restaurant:
            print("  Not found")
            continue
        
        # Check raw overlap before any filtering
        raw_match = service._evaluate_match_raw(intern, restaurant, 50, 12)
        if raw_match:
            print(f"  Raw overlap: {raw_match['total_overlap_hours']} hours, {raw_match['days_matched']} days")
            print(f"  Raw score: {raw_match['match_score']}")
        else:
            print("  No raw overlap found")
        
        # Check evaluated match (with 12-hour filter)
        eval_match = service._evaluate_match(intern, restaurant, 50, 12)
        if eval_match:
            print(f"  Evaluated match: {eval_match['total_overlap_hours']} hours, {eval_match['days_matched']} days")
        else:
            print("  Evaluated match: REJECTED (insufficient hours)")
    
    # Now let's see what valid matches we should be finding
    print(f"\n=== FINDING VALID MATCHES FOR TEST CASES ===")
    
    for intern_name, restaurant_name in test_cases:
        print(f"\n{intern_name}:")
        
        # Find intern
        intern = None
        for i in interns:
            if intern_name in i.user.full_name:
                intern = i
                break
        
        if not intern:
            continue
        
        # Check all restaurants for this intern
        valid_matches = []
        for restaurant in restaurants:
            match = service._evaluate_match(intern, restaurant, 50, 12)
            if match:
                valid_matches.append((restaurant.name, match['total_overlap_hours'], match['commute_minutes']))
        
        if valid_matches:
            print(f"  Valid matches found:")
            for rest_name, hours, commute in sorted(valid_matches, key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {rest_name}: {hours} hours, {commute} mins")
        else:
            print(f"  No valid matches found (needs 12+ hours)")

if __name__ == "__main__":
    test_improved_matching()
