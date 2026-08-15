#!/usr/bin/env python3
"""
Debug slot overlap directly
"""

from app.services.slot import Slot

def debug_slot_overlap():
    """Debug slot overlap issues"""
    print("=== DEBUGGING SLOT OVERLAP ===")
    
    # Test Shelsea's Monday vs Abaca's Monday
    shelsea_monday = Slot("12PM-1PM")  # Should be 12-13
    abaca_slots = [
        Slot("10AM-11AM"),  # 10-11
        Slot("11AM-12PM"),  # 11-12
        Slot("12PM-1PM"),   # 12-13
        Slot("2PM-3PM"),    # 14-15
        Slot("3PM-4PM"),    # 15-16
        Slot("4PM-5PM")     # 16-17
    ]
    
    print(f"Shelsea Monday: {shelsea_monday} ({shelsea_monday.start}-{shelsea_monday.end})")
    print(f"Abaca Monday slots:")
    for i, slot in enumerate(abaca_slots):
        print(f"  {i+1}. {slot} ({slot.start}-{slot.end})")
    
    print(f"\nTesting overlaps:")
    for i, abaca_slot in enumerate(abaca_slots):
        overlap = shelsea_monday.get_overlap(abaca_slot)
        if overlap:
            print(f"  Overlap {i+1}: {overlap} ({overlap.start}-{overlap.end}, {overlap.duration()} hrs)")
        else:
            print(f"  Overlap {i+1}: None")
    
    # Test Shelsea's Saturday parsing
    print(f"\n=== TESTING SHELSEA SATURDAY PARSING ===")
    saturday_all_day = "All Day (9AM-9PM)"
    print(f"Raw string: '{saturday_all_day}'")
    
    # Parse with Slot constructor
    slot = Slot(saturday_all_day)
    print(f"Parsed slot: {slot} ({slot.start}-{slot.end})")
    
    # Test what our parsing produces
    import re
    match = re.search(r'(\d+)AM-(\d+)PM', saturday_all_day)
    if match:
        start_hour = int(match.group(1))
        end_hour = int(match.group(2)) + 12
        print(f"Our parsing: {start_hour}-{end_hour}")
        manual_slot = Slot(f"{start_hour}-{end_hour}")
        print(f"Manual slot: {manual_slot} ({manual_slot.start}-{manual_slot.end})")

if __name__ == "__main__":
    debug_slot_overlap()
