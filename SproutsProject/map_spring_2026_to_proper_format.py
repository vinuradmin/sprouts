#!/usr/bin/env python3
"""
Map Spring 2026 CSV data to the proper format expected by Chef and Intern classes
"""

import csv
import pandas as pd

def map_chef_csv():
    """Map Spring 2026 chef CSV to proper format"""
    print("Mapping chef CSV...")
    
    # Read Spring 2026 chef data
    df = pd.read_csv('chef_avail_spring_2026_with_headers.csv')
    
    # Create properly formatted rows
    mapped_rows = []
    
    for idx, row in df.iterrows():
        mapped_row = {
            '': '',
            'Season/Year': 'Spring 2026',
            'Timestamp': row['Timestamp'],
            'Restaurant Name': row['Restaurant Name'],
            'Do interns need to be over 18 to work in your kitchen?': row['Over 18'],
            'Restaurant Location': row['City'],
            'Restaurant Address': row['Restaurant Address'],
            "Primary Mentor's Full Name (First and Last)": row['Chef Name'],
            "Primary Mentor's Cell Phone Number": row['Chef Phone'],
            "Primary Mentor's Email Address": row['Chef Email'],
            'Monday': row['Monday'],
            'Tuesday': row['Tuesday'],
            'Wednesday': row['Wednesday'],
            'Thursday': row['Thursday'],
            'Friday': row['Friday'],
            'Saturday': row['Saturday'],
            'Sunday': row['Sunday']
        }
        mapped_rows.append(mapped_row)
    
    # Write to new CSV
    fieldnames = ['', 'Season/Year', 'Timestamp', 'Restaurant Name', 'Do interns need to be over 18 to work in your kitchen?', 
                  'Restaurant Location', 'Restaurant Address', "Primary Mentor's Full Name (First and Last)", 
                  "Primary Mentor's Cell Phone Number", "Primary Mentor's Email Address", 
                  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    with open('chef_avail_spring_2026_formatted.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mapped_rows)
    
    print(f"  Created chef_avail_spring_2026_formatted.csv with {len(mapped_rows)} rows")

def map_intern_csv():
    """Map Spring 2026 intern CSV to proper format (already has correct headers)"""
    print("Intern CSV already has proper headers, copying...")
    
    # The intern CSV already has the right structure, just copy it
    df = pd.read_csv('intern_avail_spring_2026_with_headers.csv')
    df.to_csv('intern_avail_spring_2026_formatted.csv', index=False)
    
    print(f"  Created intern_avail_spring_2026_formatted.csv with {len(df)} rows")

def main():
    print("="*80)
    print("MAPPING SPRING 2026 CSVs TO PROPER FORMAT")
    print("="*80)
    print()
    
    map_chef_csv()
    print()
    map_intern_csv()
    
    print()
    print("="*80)
    print("COMPLETE")
    print("="*80)
    print("\nCreated files:")
    print("  - chef_avail_spring_2026_formatted.csv")
    print("  - intern_avail_spring_2026_formatted.csv")

if __name__ == "__main__":
    main()
