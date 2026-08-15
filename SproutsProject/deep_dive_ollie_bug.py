#!/usr/bin/env python3
"""
Deep dive analysis to find the exact bug in original algorithm for Ollie -> Snail Bar
"""

import csv
import re
from app.services.slot import Slot

def deep_dive_ollie_bug():
    """Deep dive to find the exact bug"""
    print("=== DEEP DIVE: OLLIE -> SNAIL BAR BUG ANALYSIS ===")
    
    # Step 1: Get the raw data
    print("\n1. RAW DATA ANALYSIS:")
    
    # Ollie's availability from CSV
    ollie_data = {
        'Monday': '4PM-5PM, 5PM-6PM, 6PM-7PM',
        'Tuesday': '4PM-5PM, 5PM-6PM, 6PM-7PM', 
        'Wednesday': '4PM-5PM, 5PM-6PM, 6PM-7PM',
        'Thursday': '3PM-4PM, Unavailable',
        'Friday': 'Unavailable',
        'Saturday': 'All Day (9AM-9PM)',
        'Sunday': 'All Day (9AM-9PM)'
    }
    
    # Snail Bar's availability from CSV
    snail_data = {
        'Monday': 'All Day (9AM-9PM)',
        'Tuesday': '',
        'Wednesday': '',
        'Thursday': '',
        'Friday': 'All Day (9AM-9PM)',
        'Saturday': 'All Day (9AM-9PM)',
        'Sunday': 'All Day (9AM-9PM)'
    }
    
    print("Ollie's availability:")
    for day, time_str in ollie_data.items():
        print(f"  {day}: '{time_str}'")
    
    print("\nSnail Bar's availability:")
    for day, time_str in snail_data.items():
        print(f"  {day}: '{time_str}'")
    
    # Step 2: Parse using original Slot class logic
    print("\n2. PARSING WITH ORIGINAL SLOT CLASS:")
    
    def parse_with_original_slot(time_str):
        """Parse time string using original Slot class logic"""
        if not time_str or time_str.strip() == '' or time_str.strip() == 'Unavailable':
            return []
        
        # Use the original Slot class
        try:
            slot = Slot(time_str)
            return [slot]
        except:
            # If that fails, try individual slots
            slots = []
            individual_slots = time_str.split(',')
            for slot_str in individual_slots:
                slot_str = slot_str.strip()
                if slot_str:
                    try:
                        slot = Slot(slot_str)
                        slots.append(slot)
                    except:
                        continue
            return slots
    
    # Parse both availabilities
    ollie_parsed = {}
    snail_parsed = {}
    
    for day in ollie_data:
        ollie_parsed[day] = parse_with_original_slot(ollie_data[day])
        snail_parsed[day] = parse_with_original_slot(snail_data[day])
    
    print("\nParsed Ollie availability:")
    for day, slots in ollie_parsed.items():
        print(f"  {day}: {[str(s) for s in slots]}")
    
    print("\nParsed Snail Bar availability:")
    for day, slots in snail_parsed.items():
        print(f"  {day}: {[str(s) for s in slots]}")
    
    # Step 3: Calculate overlaps day by day
    print("\n3. DAILY OVERLAP CALCULATION:")
    
    daily_overlaps = {}
    total_hours = 0
    days_with_4_plus = 0
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        ollie_slots = ollie_parsed.get(day, [])
        snail_slots = snail_parsed.get(day, [])
        
        day_overlaps = []
        day_hours = 0
        
        print(f"\n{day}:")
        print(f"  Ollie: {[str(s) for s in ollie_slots]}")
        print(f"  Snail: {[str(s) for s in snail_slots]}")
        
        for ollie_slot in ollie_slots:
            for snail_slot in snail_slots:
                overlap = ollie_slot.get_overlap(snail_slot)
                if overlap:
                    day_overlaps.append(overlap)
                    day_hours += overlap.duration()
                    print(f"    Overlap: {overlap} ({overlap.duration()} hrs)")
        
        daily_overlaps[day] = day_overlaps
        total_hours += day_hours
        
        if day_hours >= 4:
            days_with_4_plus += 1
            print(f"  Day total: {day_hours} hrs (MEETS 4-HR MIN)")
        else:
            print(f"  Day total: {day_hours} hrs (BELOW 4-HR MIN)")
    
    print(f"\n4. WEEKLY TOTAL:")
    print(f"  Total hours: {total_hours}")
    print(f"  Days with 4+ hours: {days_with_4_plus}")
    print(f"  Meets 12-hour minimum: {'YES' if total_hours >= 12 else 'NO'}")
    print(f"  Meets 2-day minimum: {'YES' if days_with_4_plus >= 2 else 'NO'}")
    
    # Step 4: Compare with original algorithm results
    print("\n5. COMPARISON WITH ORIGINAL ALGORITHM RESULTS:")
    
    # From our earlier analysis, we know:
    # - Saturday: Snail Bar (37 mins): [9-21] (12 hrs)
    # - Sunday: Snail Bar (37 mins): [9-21] (12 hrs)
    
    expected_saturday = 12
    expected_sunday = 12
    expected_total = 24
    
    print(f"Expected Saturday overlap: {expected_saturday} hrs")
    print(f"Expected Sunday overlap: {expected_sunday} hrs")
    print(f"Expected total: {expected_total} hrs")
    
    print(f"\nOur calculation:")
    print(f"Saturday: {daily_overlaps.get('Saturday', [])}")
    saturday_hours = sum(s.duration() for s in daily_overlaps.get('Saturday', []))
    print(f"Saturday hours: {saturday_hours}")
    
    print(f"Sunday: {daily_overlaps.get('Sunday', [])}")
    sunday_hours = sum(s.duration() for s in daily_overlaps.get('Sunday', []))
    print(f"Sunday hours: {sunday_hours}")
    
    print(f"Total: {total_hours} hrs")
    
    # Step 5: Identify the discrepancy
    print("\n6. DISCREPANCY ANALYSIS:")
    
    if saturday_hours != expected_saturday:
        print(f"DISCREPANCY: Saturday calculated {saturday_hours} hrs, expected {expected_saturday} hrs")
        print(f"Difference: {expected_saturday - saturday_hours} hrs")
    
    if sunday_hours != expected_sunday:
        print(f"DISCREPANCY: Sunday calculated {sunday_hours} hrs, expected {expected_sunday} hrs")
        print(f"Difference: {expected_sunday - sunday_hours} hrs")
    
    if total_hours != expected_total:
        print(f"DISCREPANCY: Total calculated {total_hours} hrs, expected {expected_total} hrs")
        print(f"Difference: {expected_total - total_hours} hrs")
    
    # Step 6: Debug the slot merging issue
    print("\n7. SLOT MERGING DEBUG:")
    
    # Check if the issue is in slot merging
    print("Testing slot merging for Saturday:")
    
    saturday_ollie = ollie_parsed['Saturday']
    saturday_snail = snail_parsed['Saturday']
    
    print(f"Ollie Saturday slots: {[str(s) for s in saturday_ollie]}")
    print(f"Snail Saturday slots: {[str(s) for s in saturday_snail]}")
    
    # Test individual overlaps
    for i, ollie_slot in enumerate(saturday_ollie):
        for j, snail_slot in enumerate(saturday_snail):
            overlap = ollie_slot.get_overlap(snail_slot)
            if overlap:
                print(f"  Overlap {i}-{j}: {ollie_slot} ∩ {snail_slot} = {overlap} ({overlap.duration()} hrs)")
            else:
                print(f"  No overlap {i}-{j}: {ollie_slot} ∩ {snail_slot}")

if __name__ == "__main__":
    deep_dive_ollie_bug()
