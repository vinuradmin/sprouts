#!/usr/bin/env python3
"""
Download Intern and Chef Availabilities for Spring 2026
Filter data after "Spring 2026" separator
For interns: only include rows with timestamp, first name, and last name
"""

from google_sheets_reader import read_google_sheet, SPREADSHEET_ID
import csv
import re

print("="*80)
print("DOWNLOADING SPRING 2026 AVAILABILITY DATA (FILTERED)")
print("="*80)

# Sheet names
INTERN_AVAIL_SHEET = "Intern Availabilities"
CHEF_AVAIL_SHEET = "Chef Availabilities"

def has_timestamp(value):
    """Check if value looks like a timestamp"""
    if not value:
        return False
    value_str = str(value).strip()
    # Check for date patterns like "1/22/2026 12:25:31" or similar
    return bool(re.match(r'\d{1,2}/\d{1,2}/\d{4}', value_str))

def has_valid_name(value):
    """Check if value is a non-empty name"""
    if not value:
        return False
    value_str = str(value).strip()
    return len(value_str) > 0 and value_str.lower() not in ['', 'nan', 'none']

print("\n1. Downloading Intern Availabilities...")
intern_data = read_google_sheet(SPREADSHEET_ID, INTERN_AVAIL_SHEET)

if intern_data:
    print(f"   Downloaded {len(intern_data)} rows")
    
    # Find "Spring 2026" separator
    spring_2026_start = None
    spring_2026_end = None
    
    for i, row in enumerate(intern_data):
        if row and len(row) > 0:
            first_cell = str(row[0]).strip()
            # Only check first column for delimiter
            if first_cell == "Spring 2026":
                spring_2026_start = i + 1  # Data starts after separator
                print(f"   Found 'Spring 2026' delimiter in first column at row {i+1}")
            elif spring_2026_start and first_cell in ["Fall 2026", "Summer 2026", "Winter 2026", "Spring 2027", "Fall 2027"]:
                spring_2026_end = i
                print(f"   Found next delimiter '{first_cell}' at row {i+1}")
                break
    
    if spring_2026_start:
        if not spring_2026_end:
            spring_2026_end = len(intern_data)
        
        # Extract and filter rows
        spring_2026_intern_data = []
        header_row = None
        
        for i in range(spring_2026_start, spring_2026_end):
            row = intern_data[i]
            if not row or len(row) < 3:
                continue
            
            # Check if this is a header row (first valid row after separator)
            if header_row is None:
                header_row = row
                spring_2026_intern_data.append(row)
                print(f"   Header row: {row[:5]}...")
                continue
            
            # Filter: must have timestamp (col 0), first name (col 1), last name (col 2)
            if has_timestamp(row[0]) and has_valid_name(row[1]) and has_valid_name(row[2]):
                spring_2026_intern_data.append(row)
        
        print(f"   Extracted {len(spring_2026_intern_data)-1} valid intern rows for Spring 2026 (plus header)")
        
        # Save to CSV
        with open('intern_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(spring_2026_intern_data)
        
        print(f"   Saved to: intern_avail_spring_2026.csv")
        
        # Show sample
        print(f"\n   Sample valid intern data (first 5 rows after header):")
        for i, row in enumerate(spring_2026_intern_data[1:6]):  # Skip header
            timestamp = row[0] if len(row) > 0 else ''
            first_name = row[1] if len(row) > 1 else ''
            last_name = row[2] if len(row) > 2 else ''
            print(f"      Row {i+1}: {timestamp} | {first_name} {last_name}")
    else:
        print("   WARNING: 'Spring 2026' separator not found")

print("\n2. Downloading Chef Availabilities...")
chef_data = read_google_sheet(SPREADSHEET_ID, CHEF_AVAIL_SHEET)

if chef_data:
    print(f"   Downloaded {len(chef_data)} rows")
    
    # Find "Spring 2026" separator
    spring_2026_start = None
    spring_2026_end = None
    
    for i, row in enumerate(chef_data):
        if row and len(row) > 0:
            first_cell = str(row[0]).strip()
            # Only check first column for delimiter
            if first_cell == "Spring 2026":
                spring_2026_start = i + 1  # Data starts after separator
                print(f"   Found 'Spring 2026' delimiter in first column at row {i+1}")
            elif spring_2026_start and first_cell in ["Fall 2026", "Summer 2026", "Winter 2026", "Spring 2027", "Fall 2027"]:
                spring_2026_end = i
                print(f"   Found next delimiter '{first_cell}' at row {i+1}")
                break
    
    if spring_2026_start:
        if not spring_2026_end:
            spring_2026_end = len(chef_data)
        
        spring_2026_chef_data = chef_data[spring_2026_start:spring_2026_end]
        
        # Filter out empty rows
        spring_2026_chef_data = [row for row in spring_2026_chef_data if row and any(cell for cell in row)]
        
        print(f"   Extracted {len(spring_2026_chef_data)} chef/restaurant rows for Spring 2026")
        
        # Save to CSV
        with open('chef_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(spring_2026_chef_data)
        
        print(f"   Saved to: chef_avail_spring_2026.csv")
        
        # Show sample
        print(f"\n   Sample chef data (first 5 rows):")
        for i, row in enumerate(spring_2026_chef_data[:5]):
            restaurant = row[1] if len(row) > 1 else ''
            status = row[4] if len(row) > 4 else ''
            print(f"      Row {i+1}: {restaurant} | Status: {status}")
    else:
        print("   WARNING: 'Spring 2026' separator not found")

print("\n" + "="*80)
print("DOWNLOAD COMPLETE")
print("="*80)
print("\nFiles created:")
print("  - intern_avail_spring_2026.csv")
print("  - chef_avail_spring_2026.csv")
