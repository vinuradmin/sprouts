#!/usr/bin/env python3
"""
Investigate specific business rule violations in actual placements
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_specific_violations():
    """Investigate specific violations in detail"""
    print("=== INVESTIGATING SPECIFIC VIOLATIONS ===")
    
    try:
        # Load actual assignments
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Get optimal assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        # Violation cases
        violation_cases = [
            "Shelsea Vasquez -> Burdell",
            "Kaylin Lewis -> Rethink Food Sustainable Community Kitchen", 
            "Roni Velasquez -> Teranga"
        ]
        
        for case in violation_cases:
            print(f"\n--- {case} ---")
            
            # Parse the case
            parts = case.split(" -> ")
            intern_name = parts[0]
            restaurant_name = parts[1]
            
            # Find intern and restaurant
            target_intern = None
            for intern in interns:
                if (intern_name.lower() in intern.user.full_name.lower() or 
                    intern.user.full_name.lower() in intern_name.lower()):
                    target_intern = intern
                    break
            
            target_restaurant = None
            for restaurant in restaurants:
                if (restaurant_name.lower() in restaurant.name.lower() or 
                    restaurant.name.lower() in restaurant_name.lower()):
                    target_restaurant = restaurant
                    break
            
            if not target_intern:
                print(f"  Intern not found in database")
                continue
                
            if not target_restaurant:
                print(f"  Restaurant not found in database")
                continue
            
            print(f"  Intern: {target_intern.user.full_name}")
            print(f"  Restaurant: {target_restaurant.name}")
            
            # Check business rules
            print(f"  Age: {target_intern.age} (Over 18: {target_intern.is_over_18})")
            print(f"  Restaurant requires 18+: {target_restaurant.over_18_only}")
            
            if target_restaurant.over_18_only and not target_intern.is_over_18:
                print(f"  ❌ VIOLATION: Age restriction - Intern is {target_intern.age}, restaurant requires 18+")
            
            # Check availability overlap
            print(f"  Checking availability overlap...")
            
            # Parse intern availability
            intern_availability = service._parse_intern_availability(target_intern)
            restaurant_availability = service._parse_restaurant_availability(target_restaurant)
            
            total_hours = 0
            days_with_4_plus = 0
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern_availability.get(day, [])
                restaurant_slots = restaurant_availability.get(day, [])
                
                day_overlaps = service._find_day_overlap(intern_slots, restaurant_slots)
                day_hours = sum(slot.duration() for slot in day_overlaps)
                
                total_hours += day_hours
                if day_hours >= 4:
                    days_with_4_plus += 1
                
                if day_hours > 0:
                    print(f"    {day}: {day_hours} hours")
            
            print(f"  Total weekly hours: {total_hours}")
            print(f"  Days with 4+ hours: {days_with_4_plus}")
            
            # Check business rules
            if total_hours < 12:
                print(f"  ❌ VIOLATION: Insufficient weekly hours - {total_hours} < 12 required")
            
            if days_with_4_plus < 2:
                print(f"  ❌ VIOLATION: Insufficient days with 4+ hours - {days_with_4_plus} < 2 required")
            
            # Check individual days
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern_availability.get(day, [])
                restaurant_slots = restaurant_availability.get(day, [])
                
                day_overlaps = service._find_day_overlap(intern_slots, restaurant_slots)
                day_hours = sum(slot.duration() for slot in day_overlaps)
                
                if day_hours > 0 and day_hours < 4:
                    print(f"  ❌ VIOLATION: {day} has {day_hours} hours (< 4 minimum)")
            
            # Try to evaluate the match
            match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
            if match:
                print(f"  ✅ Match evaluation: VALID")
                print(f"    Score: {match.get('match_score', 'N/A')}")
                print(f"    Hours: {match['total_overlap_hours']}")
                print(f"    Days: {match['days_matched']}")
            else:
                print(f"  ❌ Match evaluation: INVALID")
            
    except Exception as e:
        print(f"Error investigating violations: {e}")

def check_all_actual_placements():
    """Check all actual placements for violations"""
    print("\n=== CHECKING ALL ACTUAL PLACEMENTS ===")
    
    try:
        # Load actual assignments
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Get optimal assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        violations = []
        valid_placements = []
        
        for idx in range(338, 367):  # Fall 2025 section
            if idx < len(active_df):
                row = active_df.iloc[idx]
                intern_name = str(row.iloc[0]).strip()
                actual_restaurant = str(row.iloc[14]).strip()
                
                if intern_name and actual_restaurant and intern_name.lower() != 'nan':
                    # Find intern and restaurant
                    target_intern = None
                    for intern in interns:
                        if (intern_name.lower() in intern.user.full_name.lower() or 
                            intern.user.full_name.lower() in intern_name.lower()):
                            target_intern = intern
                            break
                    
                    target_restaurant = None
                    for restaurant in restaurants:
                        if (actual_restaurant.lower() in restaurant.name.lower() or 
                            restaurant.name.lower() in actual_restaurant.lower()):
                            target_restaurant = restaurant
                            break
                    
                    if target_intern and target_restaurant:
                        # Check if this match is valid
                        match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
                        
                        if match:
                            valid_placements.append({
                                'intern': intern_name,
                                'restaurant': actual_restaurant,
                                'hours': match['total_overlap_hours'],
                                'days': match['days_matched']
                            })
                        else:
                            violations.append({
                                'intern': intern_name,
                                'restaurant': actual_restaurant
                            })
        
        print(f"Valid placements: {len(valid_placements)}")
        print(f"Violations: {len(violations)}")
        
        if violations:
            print(f"\nAll violations:")
            for v in violations:
                print(f"  {v['intern']} -> {v['restaurant']}")
        
        if valid_placements:
            print(f"\nValid placements:")
            for v in valid_placements[:5]:
                print(f"  {v['intern']} -> {v['restaurant']} ({v['hours']} hrs, {v['days']} days)")
        
    except Exception as e:
        print(f"Error checking all placements: {e}")

if __name__ == "__main__":
    investigate_specific_violations()
    check_all_actual_placements()
    
    print("\n=== VIOLATION INVESTIGATION COMPLETE ===")
