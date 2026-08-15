#!/usr/bin/env python3
"""
Debug why Eric and Gavin are still unassigned even with new availability
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_schedule_overlap():
    """Debug schedule overlap calculation for Eric and Gavin"""
    print("="*80)
    print("DEBUGGING SCHEDULE OVERLAP")
    print("Why Eric and Gavin are still unassigned with new availability")
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
        matching_service = HungarianMatchingService()
        
        # Focus on Eric and Gavin
        debug_cases = [
            {'name': 'Eric Willis', 'email': 'Ericg@foreigncinema.com'},
            {'name': 'Gavin Patane', 'email': 'Gavin@sirene-oak.com'}
        ]
        
        for case in debug_cases:
            print(f"\n" + "="*60)
            print(f"DEBUGGING: {case['name']}")
            print("="*60)
            
            # Find intern
            intern = None
            for i in interns:
                if case['name'] in i.user.full_name or i.user.full_name in case['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"Not found in database")
                continue
            
            print(f"Intern: {intern.user.full_name}")
            print(f"Address: {intern.get_full_address()}")
            
            # Show their new availability
            print(f"\nTheir availability:")
            if intern.availability:
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    am = getattr(intern.availability, f'{day}_am')
                    pm = getattr(intern.availability, f'{day}_pm')
                    status = ""
                    if am: status += "9AM-1PM "
                    if pm: status += "1PM-9PM"
                    if not status: status = "None"
                    print(f"  {day.capitalize()}: {status}")
            
            # Check top 5 restaurants by commute
            print(f"\nTop 5 restaurants by commute time:")
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
            
            possible_restaurants.sort(key=lambda x: x['commute'])
            
            for i, rest_data in enumerate(possible_restaurants[:5]):
                restaurant = rest_data['restaurant']
                commute_time = rest_data['commute']
                
                print(f"\n{i+1}. {restaurant.name} ({commute_time} min):")
                
                # Get restaurant availability
                try:
                    restaurant_availability = matching_service._parse_restaurant_availability(restaurant)
                    
                    if not restaurant_availability:
                        print(f"   ERROR: No restaurant availability data")
                        continue
                    
                    print(f"   Restaurant has availability for {len(restaurant_availability)} days")
                    
                    # Calculate overlap
                    intern_availability = matching_service._parse_intern_availability(intern)
                    total_hours, schedule = matching_service._calculate_weekly_overlap(
                        intern_availability, restaurant_availability
                    )
                    
                    print(f"   Total overlap: {total_hours} hours")
                    
                    if total_hours >= 12:
                        print(f"   STATUS: QUALIFIED (>= 12 hours)")
                        
                        # Show detailed schedule
                        if schedule:
                            print(f"   Detailed schedule:")
                            for day, slots in schedule.items():
                                if slots:
                                    for slot in slots:
                                        print(f"     {day}: {slot}")
                    else:
                        print(f"   STATUS: NOT QUALIFIED ({total_hours} < 12 hours)")
                        
                        # Show why it's failing
                        print(f"   Debugging overlap calculation:")
                        
                        # Show intern vs restaurant availability side by side
                        print(f"   Intern vs Restaurant availability:")
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        for day in days:
                            intern_avail = intern_availability.get(day.lower(), [])
                            rest_avail = restaurant_availability.get(day, [])
                            
                            intern_str = f"{len(intern_avail)} slots" if intern_avail else "None"
                            rest_str = f"{len(rest_avail)} slots" if rest_avail else "None"
                            
                            print(f"     {day}: Intern={intern_str}, Restaurant={rest_str}")
                        
                except Exception as e:
                    print(f"   ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    debug_schedule_overlap()
    
    print(f"\n" + "="*80)
    print("SCHEDULE OVERLAP DEBUG COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
