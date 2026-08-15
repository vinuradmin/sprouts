#!/usr/bin/env python3
"""
Check overlap details for Angel Ruiz and Shelsea Vasquez with Abaca Restaurant
"""

import csv
import re

def parse_time_slots(time_str):
    """Parse time slots like '11AM-12PM, 12PM-1PM, 1PM-2PM, 2PM-3PM, 3PM-4PM'"""
    if not time_str or time_str.strip() == '' or time_str.strip() == 'Unavailable':
        return []
    
    time_str = time_str.upper()
    
    # Handle "All Day (9AM-9PM)" format
    if 'ALL DAY' in time_str:
        match = re.search(r'(\d+)AM-(\d+)PM', time_str)
        if match:
            start_hour = int(match.group(1))
            end_hour = int(match.group(2)) + 12
            return [(start_hour, end_hour)]
    
    # Parse individual time slots
    slots = []
    individual_slots = time_str.split(',')
    for slot in individual_slots:
        slot = slot.strip()
        match = re.match(r'(\d+)(AM|PM)-(\d+)(AM|PM)', slot)
        if match:
            start_hour = int(match.group(1))
            start_period = match.group(2)
            end_hour = int(match.group(3))
            end_period = match.group(4)
            
            # Convert to 24-hour format
            if start_period == 'AM':
                if start_hour == 12:
                    start_hour = 0
            else:
                if start_hour != 12:
                    start_hour += 12
            
            if end_period == 'AM':
                if end_hour == 12:
                    end_hour = 0
            else:
                if end_hour != 12:
                    end_hour += 12
            
            slots.append((start_hour, end_hour))
    
    return slots

def check_abaca_overlap():
    """Check overlap for Angel Ruiz and Shelsea Vasquez with Abaca"""
    print("=== ABACA RESTAURANT OVERLAP ANALYSIS ===")
    
    interns_to_check = [
        ("Angel Ruiz", "Angel"),
        ("Shelsea Vasquez", "Shelsea")
    ]
    
    for intern_full_name, intern_first_name in interns_to_check:
        print(f"\n{intern_full_name} -> Abaca Restaurant")
        print("=" * 50)
        
        # Get intern availability
        intern_avail = {}
        try:
            with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                    if intern_first_name in full_name:
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        for day in days:
                            time_str = row.get(day, '').strip()
                            intern_avail[day] = parse_time_slots(time_str)
                        break
        except Exception as e:
            print(f"Error reading intern CSV: {e}")
            continue
        
        # Get Abaca availability
        abaca_avail = {}
        try:
            with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    restaurant_name = row.get('Restaurant Name', '').strip()
                    if 'Abaca' in restaurant_name:
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        for day in days:
                            time_str = row.get(day, '').strip()
                            abaca_avail[day] = parse_time_slots(time_str)
                        break
        except Exception as e:
            print(f"Error reading chef CSV: {e}")
            continue
        
        # Calculate overlap
        total_overlap = 0
        days_with_4_plus = 0
        overlap_details = {}
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            intern_slots = intern_avail.get(day, [])
            abaca_slots = abaca_avail.get(day, [])
            
            if intern_slots and abaca_slots:
                print(f"  {day}:")
                day_overlap = 0
                day_overlaps = []
                
                for i_start, i_end in intern_slots:
                    for a_start, a_end in abaca_slots:
                        overlap_start = max(i_start, a_start)
                        overlap_end = min(i_end, a_end)
                        
                        if overlap_end > overlap_start:
                            overlap_hours = overlap_end - overlap_start
                            total_overlap += overlap_hours
                            day_overlap += overlap_hours
                            day_overlaps.append(f"{overlap_start:02d}:00-{overlap_end:02d}:00 ({overlap_hours} hrs)")
                
                if day_overlaps:
                    for overlap in day_overlaps:
                        print(f"    {overlap}")
                    print(f"    Day total: {day_overlap} hrs")
                    
                    if day_overlap >= 4:
                        days_with_4_plus += 1
                        print(f"    Meets 4-hour minimum")
                    else:
                        print(f"    Does NOT meet 4-hour minimum")
                else:
                    print(f"    No overlap")
            else:
                print(f"  {day}: No availability")
        
        print(f"\n  SUMMARY:")
        print(f"    Total weekly overlap: {total_overlap} hours")
        print(f"    Days with 4+ hours: {days_with_4_plus}")
        
        if total_overlap >= 12:
            print(f"    Meets 12-hour weekly minimum")
        else:
            print(f"    Does NOT meet 12-hour weekly minimum")
        
        if days_with_4_plus >= 2:
            print(f"    Meets 2-day minimum")
        else:
            print(f"    Does NOT meet 2-day minimum")
        
        # Final status
        if total_overlap >= 12 and days_with_4_plus >= 2:
            print(f"    VALID MATCH")
        else:
            print(f"    INVALID MATCH")

if __name__ == "__main__":
    check_abaca_overlap()
