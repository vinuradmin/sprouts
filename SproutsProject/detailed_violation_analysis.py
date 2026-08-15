#!/usr/bin/env python3
"""
Detailed analysis of business rule violations
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def detailed_violation_analysis():
    """Get detailed violation information"""
    print("=== DETAILED VIOLATION ANALYSIS ===")
    
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
        
        # Check each violation case
        violation_cases = [
            "Shelsea Vasquez -> Burdell",
            "Kaylin Lewis -> Rethink Food Sustainable Community Kitchen", 
            "Roni Velasquez -> Teranga"
        ]
        
        for case in violation_cases:
            print(f"\n{'='*60}")
            print(f"ANALYZING: {case}")
            print(f"{'='*60}")
            
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
            
            if not target_intern or not target_restaurant:
                print(f"Could not find intern/restaurant in database")
                continue
            
            print(f"Intern: {target_intern.user.full_name}")
            print(f"Age: {target_intern.age}")
            print(f"Restaurant: {target_restaurant.name}")
            
            # Check age restriction
            print(f"\n--- AGE RESTRICTION CHECK ---")
            intern_over_18 = target_intern.age >= 18
            print(f"Intern is 18+: {intern_over_18}")
            
            # Get restaurant age restriction from restaurant model
            try:
                restaurant_over_18 = target_restaurant.over_18_only if hasattr(target_restaurant, 'over_18_only') else False
                print(f"Restaurant requires 18+: {restaurant_over_18}")
                
                if restaurant_over_18 and not intern_over_18:
                    print(f"❌ VIOLATION: Age restriction - Intern is {target_intern.age}, restaurant requires 18+")
                else:
                    print(f"✅ Age restriction: OK")
            except:
                print(f"Could not check restaurant age restriction")
            
            # Check availability
            print(f"\n--- AVAILABILITY CHECK ---")
            
            # Get availability data
            intern_availability = service._parse_intern_availability(target_intern)
            restaurant_availability = service._parse_restaurant_availability(target_restaurant)
            
            print(f"Intern availability:")
            for day, slots in intern_availability.items():
                if slots:
                    hours = sum(slot.duration() for slot in slots)
                    print(f"  {day}: {hours} hours")
            
            print(f"\nRestaurant availability:")
            for day, slots in restaurant_availability.items():
                if slots:
                    hours = sum(slot.duration() for slot in slots)
                    print(f"  {day}: {hours} hours")
            
            # Calculate overlap
            print(f"\n--- OVERLAP ANALYSIS ---")
            total_hours = 0
            days_with_4_plus = 0
            daily_overlaps = {}
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern_availability.get(day, [])
                restaurant_slots = restaurant_availability.get(day, [])
                
                day_overlaps = service._find_day_overlap(intern_slots, restaurant_slots)
                day_hours = sum(slot.duration() for slot in day_overlaps)
                
                total_hours += day_hours
                if day_hours >= 4:
                    days_with_4_plus += 1
                
                daily_overlaps[day] = day_hours
                
                if day_hours > 0:
                    print(f"  {day}: {day_hours} hours {'✅' if day_hours >= 4 else '❌ (<4 hrs)'}")
            
            print(f"\n--- BUSINESS RULES CHECK ---")
            print(f"Total weekly hours: {total_hours} {'✅' if total_hours >= 12 else f'❌ (<12 hrs)'}")
            print(f"Days with 4+ hours: {days_with_4_plus} {'✅' if days_with_4_plus >= 2 else f'❌ (<2 days)'}")
            
            # Specific violations
            violations = []
            
            if total_hours < 12:
                violations.append(f"Weekly hours insufficient: {total_hours} < 12")
            
            if days_with_4_plus < 2:
                violations.append(f"Insufficient 4+ hour days: {days_with_4_plus} < 2")
            
            for day, hours in daily_overlaps.items():
                if 0 < hours < 4:
                    violations.append(f"{day} has {hours} hours (< 4 minimum)")
            
            if violations:
                print(f"\n❌ VIOLATIONS FOUND:")
                for violation in violations:
                    print(f"  - {violation}")
            else:
                print(f"\n✅ No business rule violations detected")
            
            # Final evaluation
            print(f"\n--- FINAL EVALUATION ---")
            match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
            
            if match:
                print(f"✅ Match is VALID")
                print(f"  Score: {match.get('match_score', 'N/A')}")
                print(f"  Hours: {match['total_overlap_hours']}")
                print(f"  Days: {match['days_matched']}")
                print(f"  Commute: {match['commute_minutes']} minutes")
            else:
                print(f"❌ Match is INVALID")
                print(f"  This placement violates business rules")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"VIOLATION SUMMARY")
        print(f"{'='*60}")
        print(f"3 actual placements violate business rules:")
        print(f"1. Shelsea Vasquez -> Burdell")
        print(f"2. Kaylin Lewis -> Rethink Food Sustainable Community Kitchen")
        print(f"3. Roni Velasquez -> Teranga")
        print(f"\nThese placements likely fail due to:")
        print(f"- Insufficient weekly availability (< 12 hours)")
        print(f"- Insufficient 4+ hour days (< 2 days)")
        print(f"- Individual days with < 4 hours overlap")
        
    except Exception as e:
        print(f"Error in detailed analysis: {e}")

if __name__ == "__main__":
    detailed_violation_analysis()
    print("\n=== DETAILED ANALYSIS COMPLETE ===")
