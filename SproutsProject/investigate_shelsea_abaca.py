#!/usr/bin/env python3
"""
Investigate why Hungarian algorithm thinks Shelsea Vasquez -> Abaca is valid
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def investigate_shelsea_abaca():
    """Investigate Shelsea Vasquez -> Abaca discrepancy"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print("=== INVESTIGATING SHELSEA VASQUEZ -> ABACA DISCREPANCY ===")
    
    # Find Shelsea Vasquez
    shelsea = None
    for intern in interns:
        if 'Shelsea' in intern.user.full_name:
            shelsea = intern
            print(f"Found Shelsea: '{intern.user.full_name}' (ID: {intern.id})")
            break
    
    if not shelsea:
        print("Shelsea not found")
        return
    
    # Find Abaca Restaurant
    abaca = None
    for restaurant in restaurants:
        if 'Abaca' in restaurant.name:
            abaca = restaurant
            print(f"Found Abaca: '{restaurant.name}' (ID: {restaurant.id})")
            break
    
    if not abaca:
        print("Abaca not found")
        return
    
    # Test the match directly
    print(f"\n=== DIRECT MATCH EVALUATION ===")
    match = service._evaluate_match(shelsea, abaca, 50, 12)
    
    if match:
        print(f"Hungarian algorithm result: VALID MATCH")
        print(f"  Commute: {match['commute_minutes']} minutes")
        print(f"  Total overlap: {match['total_overlap_hours']} hours")
        print(f"  Days matched: {match['days_matched']}")
        print(f"  Match score: {match['match_score']}")
        
        # Show the schedule
        schedule = match.get('schedule', {})
        print(f"\nSchedule:")
        for day, slots in schedule.items():
            if slots:
                print(f"  {day}:")
                for slot in slots:
                    print(f"    {slot}")
    else:
        print(f"Hungarian algorithm result: INVALID MATCH")
    
    # Check what the Hungarian algorithm sees for availability
    print(f"\n=== HUNGARIAN ALGORITHM AVAILABILITY PARSING ===")
    
    # Shelsea's availability (as seen by Hungarian algorithm)
    shelsea_avail = service._parse_intern_availability(shelsea)
    print(f"\nShelsea's availability:")
    for day, slots in shelsea_avail.items():
        if slots:
            print(f"  {day}: {[str(slot) for slot in slots]}")
        else:
            print(f"  {day}: []")
    
    # Abaca's availability (as seen by Hungarian algorithm)
    abaca_avail = service._parse_restaurant_availability(abaca)
    print(f"\nAbaca's availability:")
    for day, slots in abaca_avail.items():
        if slots:
            print(f"  {day}: {[str(slot) for slot in slots]}")
        else:
            print(f"  {day}: []")
    
    # Calculate overlap day by day
    print(f"\n=== DAY BY DAY OVERLAP ANALYSIS ===")
    total_hours = 0
    days_with_4_plus = 0
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        shelsea_slots = shelsea_avail.get(day, [])
        abaca_slots = abaca_avail.get(day, [])
        
        if shelsea_slots and abaca_slots:
            print(f"\n{day}:")
            print(f"  Shelsea: {[str(slot) for slot in shelsea_slots]}")
            print(f"  Abaca: {[str(slot) for slot in abaca_slots]}")
            
            # Find overlaps
            overlaps = service._find_day_overlap(shelsea_slots, abaca_slots)
            print(f"  Overlaps: {[str(slot) for slot in overlaps]}")
            
            day_total = sum(slot.duration() for slot in overlaps)
            total_hours += day_total
            
            if day_total >= 4:
                days_with_4_plus += 1
                print(f"  Day total: {day_total} hrs (MEETS 4-HR MIN)")
            else:
                print(f"  Day total: {day_total} hrs (BELOW 4-HR MIN)")
        else:
            print(f"\n{day}: No availability for one or both")
    
    print(f"\n=== FINAL CALCULATION ===")
    print(f"Total hours: {total_hours}")
    print(f"Days with 4+ hours: {days_with_4_plus}")
    print(f"Meets 12-hour minimum: {'YES' if total_hours >= 12 else 'NO'}")
    print(f"Meets 2-day minimum: {'YES' if days_with_4_plus >= 2 else 'NO'}")
    
    # Compare with our CSV analysis
    print(f"\n=== COMPARISON WITH CSV ANALYSIS ===")
    print(f"CSV analysis showed: 10 hours total, 1 day with 4+ hours")
    print(f"Hungarian algorithm shows: {total_hours} hours total, {days_with_4_plus} days with 4+ hours")
    
    if total_hours != 10 or days_with_4_plus != 1:
        print(f"DISCREPANCY DETECTED!")
        print(f"The Hungarian algorithm is parsing availability differently than our CSV analysis.")
    else:
        print(f"Results match our CSV analysis.")

if __name__ == "__main__":
    investigate_shelsea_abaca()
