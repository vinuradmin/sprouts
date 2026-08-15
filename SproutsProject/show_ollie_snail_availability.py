#!/usr/bin/env python3
"""
Show availability for Ollie O'Malley and Snail Bar
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

def show_ollie_snail_availability():
    """Show availability for Ollie and Snail Bar"""
    print("=== OLLIE O'MALLEY & SNAIL BAR AVAILABILITY ===")
    
    # Get Ollie's availability from intern CSV
    print("\n1. OLLIE O'MALLEY AVAILABILITY:")
    try:
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Ollie' in full_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    total_hours = 0
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = parse_time_slots(time_str)
                        
                        if slots:
                            print(f"  {day}:")
                            for start, end in slots:
                                hours = end - start
                                total_hours += hours
                                print(f"    {start:02d}:00-{end:02d}:00 ({hours} hrs)")
                        else:
                            print(f"  {day}: Unavailable")
                    
                    print(f"  Total weekly hours: {total_hours}")
                    break
                    
    except Exception as e:
        print(f"Error reading intern CSV: {e}")
    
    # Get Snail Bar availability from chef CSV
    print("\n2. SNAIL BAR AVAILABILITY:")
    try:
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Snail Bar' in restaurant_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    total_hours = 0
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = parse_time_slots(time_str)
                        
                        if slots:
                            print(f"  {day}:")
                            for start, end in slots:
                                hours = end - start
                                total_hours += hours
                                print(f"    {start:02d}:00-{end:02d}:00 ({hours} hrs)")
                        else:
                            print(f"  {day}: Unavailable")
                    
                    print(f"  Total weekly hours: {total_hours}")
                    break
                    
    except Exception as e:
        print(f"Error reading chef CSV: {e}")
    
    # Calculate overlap
    print("\n3. OVERLAP ANALYSIS:")
    try:
        # Ollie availability
        ollie_avail = {}
        with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if 'Ollie' in full_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for day in days:
                        time_str = row.get(day, '').strip()
                        ollie_avail[day] = parse_time_slots(time_str)
                    break
        
        # Snail Bar availability
        snail_avail = {}
        with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                restaurant_name = row.get('Restaurant Name', '').strip()
                if 'Snail Bar' in restaurant_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for day in days:
                        time_str = row.get(day, '').strip()
                        snail_avail[day] = parse_time_slots(time_str)
                    break
        
        # Calculate overlap
        total_overlap = 0
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            ollie_slots = ollie_avail.get(day, [])
            snail_slots = snail_avail.get(day, [])
            
            if ollie_slots and snail_slots:
                print(f"  {day} overlap:")
                for o_start, o_end in ollie_slots:
                    for s_start, s_end in snail_slots:
                        overlap_start = max(o_start, s_start)
                        overlap_end = min(o_end, s_end)
                        
                        if overlap_end > overlap_start:
                            overlap_hours = overlap_end - overlap_start
                            total_overlap += overlap_hours
                            print(f"    {overlap_start:02d}:00-{overlap_end:02d}:00 ({overlap_hours} hrs)")
        
        print(f"\nTotal weekly overlap: {total_overlap} hours")
        
        if total_overlap >= 12:
            print("  STATUS: Meets 12-hour minimum")
        else:
            print("  STATUS: Does NOT meet 12-hour minimum")
            
        # Check days with 4+ hours
        days_with_4_plus = 0
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            ollie_slots = ollie_avail.get(day, [])
            snail_slots = snail_avail.get(day, [])
            
            day_overlap = 0
            if ollie_slots and snail_slots:
                for o_start, o_end in ollie_slots:
                    for s_start, s_end in snail_slots:
                        overlap_start = max(o_start, s_start)
                        overlap_end = min(o_end, s_end)
                        if overlap_end > overlap_start:
                            day_overlap += overlap_end - overlap_start
            
            if day_overlap >= 4:
                days_with_4_plus += 1
        
        print(f"Days with 4+ hours: {days_with_4_plus}")
        if days_with_4_plus >= 2:
            print("  STATUS: Meets 2-day minimum")
        else:
            print("  STATUS: Does NOT meet 2-day minimum")
        
    except Exception as e:
        print(f"Error calculating overlap: {e}")

if __name__ == "__main__":
    show_ollie_snail_availability()
