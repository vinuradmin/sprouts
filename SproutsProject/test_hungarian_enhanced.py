#!/usr/bin/env python3
"""
Test the Hungarian matching service with enhanced slot logic
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def test_hungarian_enhanced():
    """Test Hungarian matching with enhanced logic"""
    print("=== TESTING HUNGARIAN MATCHING WITH ENHANCED LOGIC ===")
    
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    
    # Test specific cases
    test_cases = [
        ("Ollie O'Malley", "Snail Bar"),
        ("Shelsea Vasquez", "Abaca"),
        ("Angel Ruiz", "Teranga"),
    ]
    
    for intern_name, restaurant_name in test_cases:
        print(f"\n--- Testing: {intern_name} -> {restaurant_name} ---")
        
        # Find intern and restaurant
        intern = None
        for i in Intern.query.all():
            if intern_name in i.user.full_name:
                intern = i
                break
        
        restaurant = None
        for r in Restaurant.query.all():
            if restaurant_name in r.name:
                restaurant = r
                break
        
        if not intern or not restaurant:
            print(f"  Not found: intern={intern is not None}, restaurant={restaurant is not None}")
            continue
        
        # Test match with enhanced logic
        match = service._evaluate_match(intern, restaurant, 50, 12)
        
        if match:
            print(f"  ✓ MATCH FOUND")
            print(f"    Total overlap: {match['total_overlap_hours']} hours")
            print(f"    Days matched: {match['days_matched']}")
            print(f"    Commute: {match['commute_minutes']} minutes")
            print(f"    Match score: {match['match_score']}")
        else:
            print(f"  ✗ NO MATCH")
    
    print("\n=== HUNGARIAN ENHANCED TEST COMPLETE ===")

if __name__ == "__main__":
    test_hungarian_enhanced()
