#!/usr/bin/env python3
"""
Test Sorrel Restaurant after CSV parsing fix
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def test_sorrel_after_fix():
    """Test Sorrel Restaurant after CSV parsing fix"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    
    print("=== TESTING SORREL AFTER CSV PARSING FIX ===")
    
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
    
    # Check if Sorrel is now in database
    restaurants = Restaurant.query.all()
    sorrel_in_db = False
    for restaurant in restaurants:
        if 'Sorrel' in restaurant.name:
            sorrel_in_db = True
            print(f"Found Sorrel in database: '{restaurant.name}' (ID: {restaurant.id})")
            break
    
    if not sorrel_in_db:
        print("Sorrel not found in database - this is expected")
        print("The database doesn't include Sorrel Restaurant")
        print("But let's test the parsing with a simulated Sorrel")
    
    # Test the parsing directly
    print(f"\nTesting CSV parsing for Sorrel Restaurant:")
    
    # Simulate Sorrel's availability parsing
    sorrel_wednesday = '10AM-11AM, 11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM, 4PM-5PM'
    
    from app.services.csv_data_loader import CSVDataLoader
    loader = CSVDataLoader()
    am, pm = loader._parse_day_slots(sorrel_wednesday)
    
    print(f"Sorrel Wednesday: '{sorrel_wednesday}'")
    print(f"Parsed as: AM={am}, PM={pm}")
    
    # Test Hungarian algorithm's slot merging
    from app.services.slot import Slot
    
    # Create Sorrel slots as they would be parsed from CSV
    sorrel_slots = [
        Slot("10-17"),  # 10AM-5PM as single slot
    ]
    
    # Ollie's Wednesday availability  
    ollie_slots = [
        Slot("16-19"),     # 4PM-7PM as single slot
    ]
    
    print(f"\nTesting slot merging:")
    
    # Find overlaps
    overlaps = []
    for intern_slot in ollie_slots:
        for restaurant_slot in sorrel_slots:
            overlap = intern_slot.get_overlap(restaurant_slot)
            if overlap:
                overlaps.append(overlap)
    
    print(f"Original overlaps: {len(overlaps)}")
    for overlap in overlaps:
        print(f"  {overlap} ({overlap.duration()} hrs)")
    
    # Apply merging fix
    merged_overlaps = service._merge_consecutive_slots(overlaps)
    
    print(f"\nAfter merging: {len(merged_overlaps)}")
    for overlap in merged_overlaps:
        print(f"  {overlap} ({overlap.duration()} hrs)")
    
    # Filter by 4-hour minimum
    filtered_overlaps = [slot for slot in merged_overlaps if slot.duration() >= 4]
    
    print(f"\nAfter 4-hour filter: {len(filtered_overlaps)}")
    for overlap in filtered_overlaps:
        print(f"  {overlap} ({overlap.duration()} hrs)")
    
    if filtered_overlaps:
        print("STATUS: PASS - Would meet 4-hour minimum")
    else:
        print("STATUS: FAIL - Still doesn't meet 4-hour minimum")

if __name__ == "__main__":
    test_sorrel_after_fix()
