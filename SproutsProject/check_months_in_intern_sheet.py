#!/usr/bin/env python3
"""
Check what months are mentioned in the Intern Availability sheet
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_months_in_intern_sheet():
    """Check what months are mentioned in Intern Availability sheet"""
    print("="*80)
    print("CHECKING MONTHS IN INTERN AVAILABILITY SHEET")
    print("Finding Fall 2025 interns")
    print("="*80)
    
    try:
        # Load Intern Availability sheet
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_intern_avail = pd.read_excel(excel_file, sheet_name='Intern Availability')
        
        print(f"Intern Availability: {len(df_intern_avail)} rows")
        
        # Check the months column
        month_col = 'For what months are you available during the times selected above? (for example: June 1-August 25)'
        
        print(f"\n1. ANALYZING MONTHS COLUMN")
        print("-" * 40)
        
        # Get unique month values
        unique_months = df_intern_avail[month_col].dropna().unique()
        print(f"Found {len(unique_months)} unique month entries:")
        
        for month_entry in unique_months:
            print(f"  '{month_entry}'")
        
        # Look for Fall 2025 keywords
        fall_keywords = ['september', 'october', 'november', 'december', 'fall']
        fall_2025_entries = []
        
        for month_entry in unique_months:
            month_str = str(month_entry).lower()
            if any(keyword in month_str for keyword in fall_keywords):
                fall_2025_entries.append(month_entry)
        
        print(f"\nFall 2025 related entries ({len(fall_2025_entries)}):")
        for entry in fall_2025_entries:
            print(f"  '{entry}'")
        
        # Filter Fall 2025 interns
        if fall_2025_entries:
            fall_mask = df_intern_avail[month_col].astype(str).str.contains('|'.join(fall_keywords), case=False, na=False)
            df_fall_2025 = df_intern_avail[fall_mask]
            print(f"\nFound {len(df_fall_2025)} Fall 2025 interns")
            
            print(f"\nFall 2025 interns:")
            for idx, row in df_fall_2025.iterrows():
                name = f"{row['First Name']} {row['Last Name']}"
                months = row[month_col]
                restaurant = row['Restaurants']
                print(f"  {name}: {months}")
                if pd.notna(restaurant) and str(restaurant) != 'nan':
                    print(f"    Restaurant: {restaurant}")
        else:
            print(f"\nNo Fall 2025 entries found!")
            
            # Check if this might be a different cohort
            print(f"\nChecking other time indicators...")
            
            # Look for any time-related columns
            time_columns = [col for col in df_intern_avail.columns if any(keyword in col.lower() for keyword in ['time', 'date', 'month', 'season', 'year'])]
            print(f"Time-related columns: {time_columns}")
            
            # Check timestamps
            if 'Timestamp' in df_intern_avail.columns:
                timestamps = pd.to_datetime(df_intern_avail['Timestamp'], errors='coerce')
                if not timestamps.isna().all():
                    print(f"\nTimestamp range:")
                    print(f"  Earliest: {timestamps.min()}")
                    print(f"  Latest: {timestamps.max()}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Checking months in Intern Availability sheet...")
    
    success = check_months_in_intern_sheet()
    
    print(f"\n" + "="*80)
    print("MONTHS CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
