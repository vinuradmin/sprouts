#!/usr/bin/env python3
"""
Download Intern and Chef Availabilities for Spring 2026
Filter data after "Spring 2026" separator
"""

from google_sheets_reader import read_google_sheet, SPREADSHEET_ID
import csv

print("="*80)
print("DOWNLOADING SPRING 2026 AVAILABILITY DATA")
print("="*80)

# Sheet names and GIDs
INTERN_AVAIL_SHEET = "Intern Availabilities"  # GID: 977712289
CHEF_AVAIL_SHEET = "Chef Availabilities"      # GID: 521208104

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
            if "Spring 2026" in first_cell:
                spring_2026_start = i + 1  # Data starts after separator
                print(f"   Found 'Spring 2026' separator at row {i+1}")
            elif spring_2026_start and first_cell and any(keyword in first_cell for keyword in ["Fall 2026", "Summer 2026", "Winter 2026", "Spring 2027"]):
                spring_2026_end = i
                print(f"   Found next separator at row {i+1}")
                break
    
    if spring_2026_start:
        if not spring_2026_end:
            spring_2026_end = len(intern_data)
        
        spring_2026_intern_data = intern_data[spring_2026_start:spring_2026_end]
        print(f"   Extracted {len(spring_2026_intern_data)} rows for Spring 2026")
        
        # Save to CSV
        with open('intern_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(spring_2026_intern_data)
        
        print(f"   Saved to: intern_avail_spring_2026.csv")
        
        # Show sample
        print(f"\n   Sample data (first 3 rows):")
        for i, row in enumerate(spring_2026_intern_data[:3]):
            print(f"      Row {i+1}: {row[:5]}...")  # Show first 5 columns
    else:
        print("   WARNING: 'Spring 2026' separator not found")
        print("   Showing first 10 rows to help identify structure:")
        for i, row in enumerate(intern_data[:10]):
            if row:
                print(f"      Row {i+1}: {row[0] if row else ''}")

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
            if "Spring 2026" in first_cell:
                spring_2026_start = i + 1  # Data starts after separator
                print(f"   Found 'Spring 2026' separator at row {i+1}")
            elif spring_2026_start and first_cell and any(keyword in first_cell for keyword in ["Fall 2026", "Summer 2026", "Winter 2026", "Spring 2027"]):
                spring_2026_end = i
                print(f"   Found next separator at row {i+1}")
                break
    
    if spring_2026_start:
        if not spring_2026_end:
            spring_2026_end = len(chef_data)
        
        spring_2026_chef_data = chef_data[spring_2026_start:spring_2026_end]
        print(f"   Extracted {len(spring_2026_chef_data)} rows for Spring 2026")
        
        # Save to CSV
        with open('chef_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(spring_2026_chef_data)
        
        print(f"   Saved to: chef_avail_spring_2026.csv")
        
        # Show sample
        print(f"\n   Sample data (first 3 rows):")
        for i, row in enumerate(spring_2026_chef_data[:3]):
            print(f"      Row {i+1}: {row[:5]}...")  # Show first 5 columns
    else:
        print("   WARNING: 'Spring 2026' separator not found")
        print("   Showing first 10 rows to help identify structure:")
        for i, row in enumerate(chef_data[:10]):
            if row:
                print(f"      Row {i+1}: {row[0] if row else ''}")

print("\n" + "="*80)
print("DOWNLOAD COMPLETE")
print("="*80)
print("\nFiles created:")
print("  - intern_avail_spring_2026.csv")
print("  - chef_avail_spring_2026.csv")
