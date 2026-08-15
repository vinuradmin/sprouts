#!/usr/bin/env python3
"""
Test the slot merging fix directly
"""

from app.services.slot import Slot

def test_slot_merging():
    """Test the slot merging functionality"""
    print("=== TESTING SLOT MERGING FIX ===")
    
    # Simulate Sorrel Restaurant's Wednesday availability
    # Seven 1-hour slots: 10AM-11AM, 11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM, 4PM-5PM
    sorrel_slots = [
        Slot("10AM-11AM"),  # (10, 11)
        Slot("11AM-12PM"),  # (11, 12)
        Slot("12PM-1PM"),   # (12, 13)
        Slot("1PM-2PM"),    # (13, 14)
        Slot("2PM-3PM"),    # (14, 15)
        Slot("3PM-4PM"),    # (15, 16)
        Slot("4PM-5PM")     # (16, 17)
    ]
    
    # Simulate Ollie's Wednesday availability
    ollie_slots = [
        Slot("4PM-5PM"),     # (16, 17)
        Slot("5PM-6PM"),     # (17, 18)
        Slot("6PM-7PM")      # (18, 19)
    ]
    
    print("1. ORIGINAL SLOTS:")
    print(f"   Sorrel: {[str(slot) for slot in sorrel_slots]}")
    print(f"   Ollie: {[str(slot) for slot in ollie_slots]}")
    
    # Find overlaps
    overlaps = []
    for intern_slot in ollie_slots:
        for restaurant_slot in sorrel_slots:
            overlap = intern_slot.get_overlap(restaurant_slot)
            if overlap:
                overlaps.append(overlap)
    
    print(f"\n2. OVERLAPS FOUND:")
    for overlap in overlaps:
        print(f"   {overlap} ({overlap.duration()} hrs)")
    
    # Test merging
    from app.services.hungarian_matching import HungarianMatchingService
    service = HungarianMatchingService()
    
    merged_overlaps = service._merge_consecutive_slots(overlaps)
    
    print(f"\n3. MERGED OVERLAPS:")
    for overlap in merged_overlaps:
        print(f"   {overlap} ({overlap.duration()} hrs)")
    
    # Filter by 4-hour minimum
    filtered_overlaps = [slot for slot in merged_overlaps if slot.duration() >= 4]
    
    print(f"\n4. FILTERED (4+ hours):")
    if filtered_overlaps:
        for overlap in filtered_overlaps:
            print(f"   {overlap} ({overlap.duration()} hrs)")
        print("   STATUS: PASS - Meets 4-hour minimum")
    else:
        print("   STATUS: FAIL - No 4+ hour slots")
    
    # Test Saturday (should be 12-hour overlap)
    print(f"\n5. SATURDAY TEST:")
    ollie_saturday = [Slot("9AM-9PM")]  # (9, 21)
    sorrel_saturday = sorrel_slots  # Same as Wednesday
    
    saturday_overlaps = []
    for intern_slot in ollie_saturday:
        for restaurant_slot in sorrel_saturday:
            overlap = intern_slot.get_overlap(restaurant_slot)
            if overlap:
                saturday_overlaps.append(overlap)
    
    print(f"   Saturday overlaps: {len(saturday_overlaps)}")
    
    merged_saturday = service._merge_consecutive_slots(saturday_overlaps)
    print(f"   Merged Saturday: {[str(slot) for slot in merged_saturday]}")
    
    if merged_saturday:
        total_hours = sum(slot.duration() for slot in merged_saturday)
        print(f"   Total Saturday hours: {total_hours}")
        print(f"   STATUS: {'PASS' if total_hours >= 4 else 'FAIL'}")

if __name__ == "__main__":
    test_slot_merging()
