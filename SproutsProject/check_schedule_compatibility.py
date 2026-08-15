#!/usr/bin/env python3
"""
Check detailed schedule compatibility for the remaining unassigned interns
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_schedule_compatibility():
    """Check detailed schedule compatibility"""
    print("="*80)
    print("CHECKING SCHEDULE COMPATIBILITY")
    print("Detailed analysis of schedule overlap requirements")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get data
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        optimizer = TransportationOptimizer()
        
        # The 3 remaining cases
        remaining_cases = [
            {'name': 'Eric Willis', 'email': 'Ericg@foreigncinema.com'},
            {'name': 'Gavin Patane', 'email': 'Gavin@sirene-oak.com'},
            {'name': 'Andrea Caballero', 'email': 'andreacaballeropb@gmail.com'}
        ]
        
        for case in remaining_cases:
            print(f"\n" + "="*60)
            print(f"SCHEDULE ANALYSIS: {case['name']}")
            print("="*60)
            
            # Find intern in database
            intern = None
            for i in interns:
                if case['name'] in i.user.full_name or i.user.full_name in case['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"Not found in database")
                continue
            
            print(f"Intern: {intern.user.full_name}")
            
            # Show intern's availability
            if intern.availability:
                print(f"\nIntern Availability:")
                print(f"  Mon AM: {intern.availability.monday_am}")
                print(f"  Mon PM: {intern.availability.monday_pm}")
                print(f"  Tue AM: {intern.availability.tuesday_am}")
                print(f"  Tue PM: {intern.availability.tuesday_pm}")
                print(f"  Wed AM: {intern.availability.wednesday_am}")
                print(f"  Wed PM: {intern.availability.wednesday_pm}")
                print(f"  Thu AM: {intern.availability.thursday_am}")
                print(f"  Thu PM: {intern.availability.thursday_pm}")
                print(f"  Fri AM: {intern.availability.friday_am}")
                print(f"  Fri PM: {intern.availability.friday_pm}")
                print(f"  Sat AM: {intern.availability.saturday_am}")
                print(f"  Sat PM: {intern.availability.saturday_pm}")
                print(f"  Sun AM: {intern.availability.sunday_am}")
                print(f"  Sun PM: {intern.availability.sunday_pm}")
            else:
                print(f"No availability data")
                continue
            
            # Check detailed compatibility with top restaurants
            print(f"\nDetailed compatibility check:")
            
            # Get top 5 restaurants by commute time
            possible_restaurants = []
            for restaurant in restaurants:
                if restaurant.requires_over_18 and (not intern.age or intern.age < 18):
                    continue
                
                try:
                    commute_time = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        restaurant.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    
                    if commute_time and commute_time <= 90:
                        possible_restaurants.append({
                            'restaurant': restaurant,
                            'commute': commute_time
                        })
                except:
                    pass
            
            # Sort by commute time
            possible_restaurants.sort(key=lambda x: x['commute'])
            
            # Check detailed compatibility for top 3
            matching_service = HungarianMatchingService()
            
            for i, rest_data in enumerate(possible_restaurants[:3]):
                restaurant = rest_data['restaurant']
                commute_time = rest_data['commute']
                
                print(f"\n{i+1}. {restaurant.name} ({commute_time} min):")
                
                # Get restaurant availability from CSV
                try:
                    restaurant_availability = matching_service._parse_restaurant_availability(restaurant)
                    print(f"   Restaurant availability loaded")
                    
                    # Calculate overlap
                    intern_availability = matching_service._parse_intern_availability(intern)
                    total_hours, schedule = matching_service._calculate_weekly_overlap(
                        intern_availability, restaurant_availability
                    )
                    
                    print(f"   Total overlap: {total_hours} hours")
                    
                    if total_hours >= 12:
                        print(f"   STATUS: QUALIFIED (>= 12 hours)")
                        
                        # Show schedule details
                        if schedule:
                            print(f"   Schedule details:")
                            for day, slots in schedule.items():
                                if slots:
                                    for slot in slots:
                                        print(f"     {day}: {slot}")
                    else:
                        print(f"   STATUS: NOT QUALIFIED (< 12 hours)")
                        print(f"   This is why they're not assigned!")
                        
                except Exception as e:
                    print(f"   ERROR checking availability: {e}")
        
        # Try reducing the minimum hours requirement
        print(f"\n" + "="*60)
        print("TESTING WITH REDUCED HOURS REQUIREMENT")
        print("="*60)
        
        # Test with 8 hours instead of 12
        result_8_hours = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            min_hours_per_week=8,  # Reduced from 12
            max_commute_minutes=90,
            restaurant_capacity=2
        )
        
        assignments_8 = result_8_hours.get('assignments', [])
        matched_8 = result_8_hours.get('matched_interns', 0)
        
        print(f"With 8-hour minimum: {matched_8} interns assigned")
        print(f"Improvement: {matched_8 - 23} additional interns")
        
        # Check if our cases are now assigned
        print(f"\nStatus with 8-hour requirement:")
        for case in remaining_cases:
            assigned = False
            assignment_restaurant = None
            
            for assignment in assignments_8:
                if case['name'] in assignment.get('intern_name', ''):
                    assigned = True
                    assignment_restaurant = assignment.get('restaurant_name')
                    break
            
            if assigned:
                print(f"  FIXED {case['name']}: Now assigned to {assignment_restaurant}")
            else:
                print(f"  STILL UNASSIGNED {case['name']}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    check_schedule_compatibility()
    
    print(f"\n" + "="*80)
    print("SCHEDULE COMPATIBILITY CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
