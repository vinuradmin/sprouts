#!/usr/bin/env python3
"""
Test the fixed Hungarian algorithm with 12-hour minimum enforcement
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def test_fixed_algorithm():
    """Test the algorithm with proper CSV parsing"""
    app = create_app()
    app.app_context().push()
    
    print("=== TESTING FIXED HUNGARIAN ALGORITHM ===")
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
    
    # Test specific cases
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
        
        # Test the evaluation
        match_data = service._evaluate_match(intern, restaurant, 50, 12)
        
        if match_data:
            print(f"  VALID MATCH: {match_data['total_overlap_hours']} hours, {match_data['days_matched']} days")
            print(f"  Score: {match_data['match_score']}")
        else:
            print(f"  INVALID MATCH - insufficient hours or days")
    
    # Run full algorithm
    print(f"\n=== RUNNING FULL ALGORITHM ===")
    matches = service.find_optimal_assignments(interns, restaurants)
    
    print(f"Total matches: {len(matches.get('assignments', []))}")
    print(f"Matched interns: {matches.get('matched_interns', 0)}")
    print(f"Average commute: {matches.get('average_commute_time', 0):.1f} minutes")
    
    # Show a few matches
    for i, assignment in enumerate(matches.get('assignments', [])[:5], 1):
        print(f"\n{i}. {assignment.get('intern_name')} -> {assignment.get('restaurant_name')}")
        print(f"   Hours: {assignment.get('total_overlap_hours')}, Days: {assignment.get('days_matched')}")
        print(f"   Commute: {assignment.get('commute_minutes')} minutes")

if __name__ == "__main__":
    test_fixed_algorithm()
