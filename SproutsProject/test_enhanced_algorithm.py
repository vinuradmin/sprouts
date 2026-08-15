#!/usr/bin/env python3
"""
Test the enhanced matching algorithm with 1-hour discontinuity tolerance
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_slot import EnhancedSlot
from app.services.hungarian_matching import HungarianMatchingService

def test_enhanced_algorithm():
    """Test the enhanced algorithm with specific cases"""
    print("=== TESTING ENHANCED ALGORITHM ===")
    
    # Test case 1: Snail Bar Saturday (should be valid)
    print("\n1. SNAIL BAR SATURDAY (should be VALID):")
    snail_saturday = "10AM-11AM, 11AM-12PM, 12PM-1PM, 2PM-3PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    merged = EnhancedSlot.combineSlots(snail_saturday, max_gap_hours=1, min_duration_hours=4)
    
    print(f"Input: {snail_saturday}")
    print(f"Merged slots: {[str(s) for s in merged]}")
    print(f"Total duration: {sum(s.duration() for s in merged)} hours")
    print(f"Status: {'VALID' if merged else 'INVALID'}")
    
    # Test case 2: Snail Bar with 2-hour gap (should be invalid)
    print("\n2. SNAIL BAR WITH 2-HOUR GAP (should be INVALID):")
    snail_with_gap = "10AM-11AM, 11AM-12PM, 12PM-1PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    merged_gap = EnhancedSlot.combineSlots(snail_with_gap, max_gap_hours=1, min_duration_hours=4)
    
    print(f"Input: {snail_with_gap}")
    print(f"Merged slots: {[str(s) for s in merged_gap]}")
    print(f"Total duration: {sum(s.duration() for s in merged_gap)} hours")
    print(f"Status: {'VALID' if merged_gap else 'INVALID'}")
    
    # Test case 3: Ollie -> Snail Bar overlap
    print("\n3. OLLIE -> SNAIL BAR OVERLAP:")
    ollie_saturday = "All Day (9AM-9PM)"
    ollie_merged = EnhancedSlot.combineSlots(ollie_saturday, max_gap_hours=1, min_duration_hours=4)
    
    print(f"Ollie: {ollie_saturday} -> {[str(s) for s in ollie_merged]}")
    print(f"Snail: {snail_saturday} -> {[str(s) for s in merged]}")
    
    if ollie_merged and merged:
        total_overlap = EnhancedSlot.calculateTotalOverlap(ollie_merged, merged)
        print(f"Total overlap: {total_overlap} hours")
        print(f"Meets 12-hour weekly minimum: {'YES' if total_overlap >= 12 else 'NO'}")
        print(f"Meets 4-hour daily minimum: {'YES' if total_overlap >= 4 else 'NO'}")
    
    # Test case 4: Different gap scenarios
    print("\n4. DIFFERENT GAP SCENARIOS:")
    
    test_cases = [
        ("9AM-10AM, 11AM-12PM", "1-hour gap", "INVALID"),  # Only 2 hours total
        ("9AM-10AM, 12PM-1PM", "2-hour gap", "INVALID"),  # 2-hour gap
        ("9AM-11AM, 12PM-2PM", "1-hour gap", "VALID"),    # 4 hours total
        ("9AM-1PM, 2PM-6PM", "1-hour gap", "VALID"),      # 8 hours total
    ]
    
    for time_str, description, expected in test_cases:
        result = EnhancedSlot.combineSlots(time_str, max_gap_hours=1, min_duration_hours=4)
        status = "VALID" if result else "INVALID"
        print(f"  {description}: {time_str}")
        print(f"    Result: {[str(s) for s in result]} -> {status} (Expected: {expected})")
    
    print("\n=== ENHANCED ALGORITHM TEST COMPLETE ===")

def test_business_rules():
    """Test all business rules with enhanced algorithm"""
    print("\n=== TESTING BUSINESS RULES ===")
    
    # Test 3x4 rule (3 days with 4+ hours each)
    print("\n1. 3x4 RULE TEST:")
    week_schedule = {
        'Monday': '9AM-1PM',      # 4 hours
        'Tuesday': '9AM-1PM',     # 4 hours  
        'Wednesday': '9AM-1PM',   # 4 hours
        'Thursday': '',           # 0 hours
        'Friday': '',             # 0 hours
        'Saturday': '',           # 0 hours
        'Sunday': '',             # 0 hours
    }
    
    total_hours = 0
    days_with_4_plus = 0
    
    for day, time_str in week_schedule.items():
        if time_str:
            merged = EnhancedSlot.combineSlots(time_str, max_gap_hours=1, min_duration_hours=4)
            day_hours = sum(s.duration() for s in merged)
            total_hours += day_hours
            if day_hours >= 4:
                days_with_4_plus += 1
            print(f"  {day}: {time_str} -> {day_hours} hrs")
    
    print(f"Total: {total_hours} hours, {days_with_4_plus} days with 4+ hrs")
    print(f"3x4 rule: {'PASS' if days_with_4_plus >= 3 else 'FAIL'}")
    
    # Test 2x6 rule (2 days with 6+ hours each)
    print("\n2. 2x6 RULE TEST:")
    week_schedule_2x6 = {
        'Monday': '9AM-3PM',      # 6 hours
        'Tuesday': '9AM-3PM',     # 6 hours
        'Wednesday': '',          # 0 hours
        'Thursday': '',           # 0 hours
        'Friday': '',             # 0 hours
        'Saturday': '',           # 0 hours
        'Sunday': '',             # 0 hours
    }
    
    total_hours = 0
    days_with_6_plus = 0
    
    for day, time_str in week_schedule_2x6.items():
        if time_str:
            merged = EnhancedSlot.combineSlots(time_str, max_gap_hours=1, min_duration_hours=6)
            day_hours = sum(s.duration() for s in merged)
            total_hours += day_hours
            if day_hours >= 6:
                days_with_6_plus += 1
            print(f"  {day}: {time_str} -> {day_hours} hrs")
    
    print(f"Total: {total_hours} hours, {days_with_6_plus} days with 6+ hrs")
    print(f"2x6 rule: {'PASS' if days_with_6_plus >= 2 else 'FAIL'}")
    
    print("\n=== BUSINESS RULES TEST COMPLETE ===")

if __name__ == "__main__":
    test_enhanced_algorithm()
    test_business_rules()
