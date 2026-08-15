#!/usr/bin/env python3
"""
Download Intern and Chef Availabilities for a specific cohort
Filter data by 'Season/Year' column instead of delimiter
"""

from google_sheets_reader import read_google_sheet, SPREADSHEET_ID
import csv
import sys

def download_cohort_data(cohort_name):
    """
    Download intern and chef data for a specific cohort
    Args:
        cohort_name: e.g., "Spring 2026", "Fall 2025"
    Returns:
        tuple: (intern_rows, chef_rows) or (None, None) if error
    """
    print("="*80)
    print(f"DOWNLOADING {cohort_name.upper()} AVAILABILITY DATA")
    print("="*80)
    
    # Sheet names
    INTERN_AVAIL_SHEET = "Intern Availabilities"
    CHEF_AVAIL_SHEET = "Chef Availabilities"
    
    # Download Intern Availabilities
    print(f"\n1. Downloading Intern Availabilities...")
    intern_data = read_google_sheet(SPREADSHEET_ID, INTERN_AVAIL_SHEET)
    
    if not intern_data:
        print("   ERROR: Failed to download intern data")
        return None, None
    
    print(f"   Downloaded {len(intern_data)} rows")
    
    # Find header row and Season/Year column
    header_row = None
    season_year_col = None
    
    for i, row in enumerate(intern_data):
        if row and len(row) > 0:
            # Look for header row (contains "Season/Year")
            for j, cell in enumerate(row):
                if str(cell).strip() == "Season/Year":
                    header_row = i
                    season_year_col = j
                    print(f"   Found 'Season/Year' column at index {j} in row {i+1}")
                    break
            if header_row is not None:
                break
    
    if header_row is None or season_year_col is None:
        print("   ERROR: 'Season/Year' column not found in Intern Availabilities")
        return None, None
    
    # Filter rows by cohort
    cohort_intern_data = [intern_data[header_row]]  # Start with header
    
    for i in range(header_row + 1, len(intern_data)):
        row = intern_data[i]
        if len(row) > season_year_col:
            season_year_value = str(row[season_year_col]).strip()
            if season_year_value == cohort_name:
                cohort_intern_data.append(row)
    
    print(f"   Found {len(cohort_intern_data)-1} intern rows for {cohort_name}")
    
    # Save to CSV
    intern_filename = f'intern_avail_{cohort_name.lower().replace(" ", "_")}.csv'
    with open(intern_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(cohort_intern_data)
    
    print(f"   Saved to: {intern_filename}")
    
    # Download Chef Availabilities
    print(f"\n2. Downloading Chef Availabilities...")
    chef_data = read_google_sheet(SPREADSHEET_ID, CHEF_AVAIL_SHEET)
    
    if not chef_data:
        print("   ERROR: Failed to download chef data")
        return None, None
    
    print(f"   Downloaded {len(chef_data)} rows")
    
    # Find header row and Season/Year column
    header_row = None
    season_year_col = None
    
    for i, row in enumerate(chef_data):
        if row and len(row) > 0:
            # Look for header row (contains "Season/Year")
            for j, cell in enumerate(row):
                if str(cell).strip() == "Season/Year":
                    header_row = i
                    season_year_col = j
                    print(f"   Found 'Season/Year' column at index {j} in row {i+1}")
                    break
            if header_row is not None:
                break
    
    if header_row is None or season_year_col is None:
        print("   ERROR: 'Season/Year' column not found in Chef Availabilities")
        return None, None
    
    # Filter rows by cohort
    cohort_chef_data = [chef_data[header_row]]  # Start with header
    
    for i in range(header_row + 1, len(chef_data)):
        row = chef_data[i]
        if len(row) > season_year_col:
            season_year_value = str(row[season_year_col]).strip()
            if season_year_value == cohort_name:
                cohort_chef_data.append(row)
    
    print(f"   Found {len(cohort_chef_data)-1} chef rows for {cohort_name}")
    
    # Save to CSV
    chef_filename = f'chef_avail_{cohort_name.lower().replace(" ", "_")}.csv'
    with open(chef_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(cohort_chef_data)
    
    print(f"   Saved to: {chef_filename}")
    
    print("\n" + "="*80)
    print("DOWNLOAD COMPLETE")
    print("="*80)
    print(f"\nFiles created:")
    print(f"  - {intern_filename}")
    print(f"  - {chef_filename}")
    
    return cohort_intern_data, cohort_chef_data

if __name__ == "__main__":
    # Get cohort name from command line or use default
    cohort_name = sys.argv[1] if len(sys.argv) > 1 else "Spring 2026"
    download_cohort_data(cohort_name)
