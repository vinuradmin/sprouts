#!/usr/bin/env python3
"""
Verify age restrictions and commute optimization are working
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def verify_restrictions():
    """Verify age restrictions and commute optimization"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print("=== VERIFYING AGE RESTRICTIONS & COMMUTE OPTIMIZATION ===")
    
    # Check age restrictions
    print(f"\n1. AGE RESTRICTIONS:")
    underage_interns = []
    age_restricted_restaurants = []
    
    for intern in interns:
        if not intern.is_over_18():
            underage_interns.append(intern.user.full_name)
    
    for restaurant in restaurants:
        if restaurant.requires_over_18:
            age_restricted_restaurants.append(restaurant.name)
    
    print(f"Underage interns: {underage_interns}")
    print(f"Age-restricted restaurants: {age_restricted_restaurants}")
    
    # Test age restriction enforcement
    if underage_interns and age_restricted_restaurants:
        print(f"\nTesting age restriction enforcement:")
        underage_intern = None
        for i in interns:
            if not i.is_over_18():
                underage_intern = i
                break
        
        restricted_restaurant = None
        for r in restaurants:
            if r.requires_over_18:
                restricted_restaurant = r
                break
        
        if underage_intern and restricted_restaurant:
            match = service._evaluate_match(underage_intern, restricted_restaurant, 50, 12)
            if match:
                print(f"  ERROR: {underage_intern.user.full_name} -> {restricted_restaurant.name} should be REJECTED")
            else:
                print(f"  CORRECT: {underage_intern.user.full_name} -> {restricted_restaurant.name} was REJECTED (age restriction)")
    
    # Check commute optimization
    print(f"\n2. COMMUTE OPTIMIZATION:")
    matches = service.find_optimal_assignments(interns, restaurants)
    
    assignments = matches.get('assignments', [])
    if assignments:
        print(f"Total matches: {len(assignments)}")
        print(f"Average commute: {matches.get('average_commute_time', 0):.1f} minutes")
        
        # Sort by commute time to show optimization
        sorted_assignments = sorted(assignments, key=lambda x: x.get('commute_minutes', 999))
        
        print(f"\nCommute times (sorted by optimization):")
        for i, assignment in enumerate(sorted_assignments[:10], 1):
            intern_name = assignment.get('intern_name', 'Unknown')
            restaurant_name = assignment.get('restaurant_name', 'Unknown')
            commute = assignment.get('commute_minutes', 0)
            hours = assignment.get('total_overlap_hours', 0)
            days = assignment.get('days_matched', 0)
            
            print(f"  {i:2d}. {intern_name} -> {restaurant_name}")
            print(f"      Commute: {commute} mins, Hours: {hours}, Days: {days}")
        
        # Check if algorithm is actually optimizing (not just random)
        total_commute = sum(a.get('commute_minutes', 0) for a in assignments)
        min_possible = len(assignments) * 5  # Assume 5 mins is theoretical minimum
        max_acceptable = len(assignments) * 60  # 60 mins max
        
        print(f"\nCommute optimization analysis:")
        print(f"Total commute: {total_commute} minutes")
        print(f"Average: {total_commute/len(assignments):.1f} minutes")
        print(f"Theoretical minimum: {min_possible} minutes")
        print(f"Maximum acceptable: {max_acceptable} minutes")
        
        if total_commute < max_acceptable * 0.7:  # Less than 70% of max
            print(f"Commute optimization appears to be working")
        else:
            print(f"Commute optimization may need improvement")
    
    # Test specific cases
    print(f"\n3. SPECIFIC TEST CASES:")
    
    test_cases = [
        ("Zhijian Liu", "Millennium Restaurant"),
        ("Samuel  Gonzalez ", "Tarts de Feybesse"),
        ("Enrique Marroquin", "Tarts de Feybesse")
    ]
    
    for intern_name, restaurant_name in test_cases:
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
        
        if intern and restaurant:
            match = service._evaluate_match(intern, restaurant, 50, 12)
            if match:
                print(f"  {intern_name} -> {restaurant_name}: {match['commute_minutes']} mins, {match['total_overlap_hours']} hrs")
                
                # Check if this is actually optimal
                # Find all valid matches for this intern
                valid_matches = []
                for r in restaurants:
                    m = service._evaluate_match(intern, r, 50, 12)
                    if m:
                        valid_matches.append((r.name, m['commute_minutes'], m['total_overlap_hours']))
                
                valid_matches.sort(key=lambda x: x[1])  # Sort by commute
                best_match = valid_matches[0] if valid_matches else None
                
                if best_match and best_match[0] == restaurant.name:
                    print(f"      This is the optimal commute choice ({best_match[1]} mins)")
                elif best_match:
                    print(f"      Better option exists: {best_match[0]} ({best_match[1]} mins)")

if __name__ == "__main__":
    verify_restrictions()
