#!/usr/bin/env python3
"""
Simplified matching for Spring 2026 data
Lists restaurant options for each intern sorted by commute time
Outputs to CSV format
"""

import csv
import json
import sys
import os

# Add path for Commute class
sys.path.append('C:/Users/pierr/OneDrive/Documents')
from commute import Commute

def load_cached_commute():
    """Load cached commute data"""
    try:
        with open('cached_commute.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cached_commute(cache):
    """Save cached commute data"""
    with open('cached_commute.json', 'w') as f:
        json.dump(cache, f, indent=4)

def parse_availability(avail_str):
    """Parse availability string like '10AM-11AM, 11AM-12PM, ...' into list of time slots"""
    if not avail_str or avail_str == 'Unavailable' or avail_str.strip() == '':
        return []
    
    # Split by comma and clean up
    slots = [s.strip() for s in avail_str.split(',')]
    return [s for s in slots if s and s != 'Unavailable']

def calculate_day_overlaps(intern_avail, chef_avail):
    """Calculate which days have overlapping availability between intern and chef"""
    overlapping_days = []
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        intern_slots = intern_avail.get(day, [])
        chef_slots = chef_avail.get(day, [])
        
        # If both have availability on this day, it's an overlap
        if intern_slots and chef_slots:
            overlapping_days.append(day)
    
    return overlapping_days

def format_overlap_display(overlapping_days, intern_avail):
    """Format the overlap information for display"""
    if not overlapping_days:
        return "No overlap"
    
    # Show days with sample time windows
    result = []
    for day in overlapping_days:
        slots = intern_avail.get(day, [])
        if slots:
            # Show first and last slot as range
            if len(slots) > 1:
                result.append(f"{day[:3]} {slots[0]}-{slots[-1].split('-')[-1]}")
            else:
                result.append(f"{day[:3]} {slots[0]}")
    
    return "; ".join(result) if result else "Multiple days"

def main():
    print("="*80)
    print("SPRING 2026 SIMPLIFIED MATCHING ALGORITHM")
    print("Restaurant options for each intern, sorted by commute time")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    
    with open('intern_avail_spring_2026.csv', encoding='utf-8') as f:
        intern_rows = list(csv.reader(f))
    
    with open('chef_avail_spring_2026.csv', encoding='utf-8') as f:
        chef_rows = list(csv.reader(f))
    
    print(f"Loaded {len(intern_rows)} intern rows")
    print(f"Loaded {len(chef_rows)} chef rows")
    
    # Load commute cache
    cached_commute = load_cached_commute()
    
    # Prepare output
    output_rows = []
    header = ['Intern Name', 'Restaurant', 'Commute (min)', 'Commute Text', 'Days with Overlap']
    
    print("\nProcessing interns...")
    
    # Process each intern
    for intern_row in intern_rows:
        if len(intern_row) < 45:
            continue
        
        # Extract intern info
        first_name = intern_row[1].strip() if len(intern_row) > 1 else ''
        last_name = intern_row[2].strip() if len(intern_row) > 2 else ''
        
        if not first_name or not last_name:
            continue
        
        intern_name = f"{first_name} {last_name}"
        intern_address = f"{intern_row[32]}, {intern_row[33]}, {intern_row[34]}" if len(intern_row) > 34 else ''
        intern_transport = intern_row[37] if len(intern_row) > 37 else 'driving'
        intern_over_18 = intern_row[35] == 'Yes' if len(intern_row) > 35 else False
        
        # Parse intern availability (columns 39-45 are Mon-Sun)
        intern_avail = {
            'Monday': parse_availability(intern_row[39] if len(intern_row) > 39 else ''),
            'Tuesday': parse_availability(intern_row[40] if len(intern_row) > 40 else ''),
            'Wednesday': parse_availability(intern_row[41] if len(intern_row) > 41 else ''),
            'Thursday': parse_availability(intern_row[42] if len(intern_row) > 42 else ''),
            'Friday': parse_availability(intern_row[43] if len(intern_row) > 43 else ''),
            'Saturday': parse_availability(intern_row[44] if len(intern_row) > 44 else ''),
            'Sunday': parse_availability(intern_row[45] if len(intern_row) > 45 else '')
        }
        
        print(f"\n{intern_name}")
        print(f"  Address: {intern_address}")
        print(f"  Transport: {intern_transport}")
        
        # Find restaurant options
        restaurant_options = []
        restaurants_checked = 0
        
        for chef_row in chef_rows:
            if len(chef_row) < 33:  # Need at least 33 columns to access day columns (26-32)
                continue
            
            restaurant_name = chef_row[1].strip() if len(chef_row) > 1 else ''
            restaurant_address = chef_row[7].strip() if len(chef_row) > 7 else ''
            requires_18 = chef_row[5] == 'Yes' if len(chef_row) > 5 else False
            
            if not restaurant_name or not restaurant_address:
                continue
            
            restaurants_checked += 1
            
            # Check age restriction
            if requires_18 and not intern_over_18:
                continue
            
            # Parse chef availability from columns 26-32 (AA-AG = Mon-Sun)
            chef_avail = {
                'Monday': parse_availability(chef_row[26] if len(chef_row) > 26 else ''),
                'Tuesday': parse_availability(chef_row[27] if len(chef_row) > 27 else ''),
                'Wednesday': parse_availability(chef_row[28] if len(chef_row) > 28 else ''),
                'Thursday': parse_availability(chef_row[29] if len(chef_row) > 29 else ''),
                'Friday': parse_availability(chef_row[30] if len(chef_row) > 30 else ''),
                'Saturday': parse_availability(chef_row[31] if len(chef_row) > 31 else ''),
                'Sunday': parse_availability(chef_row[32] if len(chef_row) > 32 else '')
            }
            
            # Calculate overlapping days
            overlapping_days = calculate_day_overlaps(intern_avail, chef_avail)
            
            # Skip if no overlapping days
            if not overlapping_days:
                continue
            
            # Calculate commute
            com_key = f"{intern_address}|{restaurant_address}"
            
            if com_key in cached_commute:
                commute = Commute.from_dict(cached_commute[com_key])
            else:
                try:
                    commute = Commute.getCommuteTime(intern_transport, intern_address, restaurant_address)
                    cached_commute[com_key] = commute.to_dict()
                except Exception as e:
                    print(f"  Error calculating commute to {restaurant_name}: {e}")
                    continue
            
            # Skip if commute too long (90 minutes = 5400 seconds)
            if commute.value > 5400:
                print(f"  Skipped {restaurant_name}: commute too long ({commute.value // 60} min)")
                continue
            
            # Skip if error commute
            if commute.value >= 100000:
                print(f"  Skipped {restaurant_name}: commute error")
                continue
            
            # Format overlap display
            overlap_display = format_overlap_display(overlapping_days, intern_avail)
            
            restaurant_options.append({
                'name': restaurant_name,
                'commute_min': commute.value // 60,
                'commute_text': commute.text,
                'days': overlap_display
            })
        
        # Sort by commute time
        restaurant_options.sort(key=lambda x: x['commute_min'])
        
        print(f"  Checked {restaurants_checked} restaurants, found {len(restaurant_options)} options")
        
        # Add to output (top 10 options per intern)
        for option in restaurant_options[:10]:
            output_rows.append({
                'Intern Name': intern_name,
                'Restaurant': option['name'],
                'Commute (min)': option['commute_min'],
                'Commute Text': option['commute_text'],
                'Days with Overlap': option['days']
            })
    
    # Save output
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")
    
    with open('spring_2026_intern_restaurant_options_with_overlaps.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(output_rows)
    
    # Save updated cache
    save_cached_commute(cached_commute)
    
    print(f"\nSaved {len(output_rows)} restaurant options to: spring_2026_intern_restaurant_options_with_overlaps.csv")
    print(f"Updated commute cache: cached_commute.json")
    
    print(f"\n{'='*80}")
    print("COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
