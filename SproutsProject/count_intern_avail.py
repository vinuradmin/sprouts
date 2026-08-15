#!/usr/bin/env python3
"""
Count interns in intern_avail_fall.csv
"""

import pandas as pd

def count_interns():
    """Count interns in intern_avail_fall.csv"""
    print("="*60)
    print("COUNTING INTERNS IN intern_avail_fall.csv")
    print("="*60)
    
    try:
        # Load the CSV file
        df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv')
        
        print(f"Total rows in CSV: {len(df)}")
        print(f"Total columns in CSV: {len(df.columns)}")
        
        # Count non-empty intern names (excluding header)
        intern_names = []
        for idx, row in df.iterrows():
            if idx == 0:  # Skip header
                continue
                
            first_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            last_name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
            
            if first_name and first_name != 'nan' and first_name != '':
                full_name = f"{first_name} {last_name}".strip()
                if full_name and full_name != 'nan':
                    intern_names.append(full_name)
        
        print(f"\nInterns with names: {len(intern_names)}")
        
        # Show first few intern names
        print(f"\nFirst 10 intern names:")
        for i, name in enumerate(intern_names[:10]):
            print(f"{i+1}. {name}")
        
        # Check for Fall 2025 specific data
        print(f"\nChecking for Fall 2025 cohort data...")
        fall_2025_count = 0
        
        for idx, row in df.iterrows():
            if idx == 0:  # Skip header
                continue
                
            # Look for Fall 2025 confirmation
            confirmation_col = None
            for col_idx in range(len(df.columns)):
                cell_value = str(row.iloc[col_idx]).lower()
                if 'fall 2025' in cell_value or 'fakk 2025' in cell_value:
                    confirmation_col = col_idx
                    break
            
            if confirmation_col is not None:
                fall_2025_count += 1
        
        print(f"Fall 2025 cohort confirmations: {fall_2025_count}")
        
        # Check availability data
        print(f"\nChecking availability data...")
        availability_cols = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        interns_with_availability = 0
        for idx, row in df.iterrows():
            if idx == 0:  # Skip header
                continue
                
            has_availability = False
            for day in availability_cols:
                if day in df.columns:
                    availability = str(row[day]).strip()
                    if availability and availability != 'nan' and availability != '':
                        has_availability = True
                        break
            
            if has_availability:
                interns_with_availability += 1
        
        print(f"Interns with availability data: {interns_with_availability}")
        
        # Check transportation data
        transportation_col = None
        for col_idx, col_name in enumerate(df.columns):
            if 'transportation' in str(col_name).lower():
                transportation_col = col_idx
                break
        
        if transportation_col is not None:
            interns_with_transportation = 0
            for idx, row in df.iterrows():
                if idx == 0:  # Skip header
                    continue
                    
                transport = str(row.iloc[transportation_col]).strip()
                if transport and transport != 'nan' and transport != '':
                    interns_with_transportation += 1
            
            print(f"Interns with transportation data: {interns_with_transportation}")
        
        return len(intern_names)
        
    except Exception as e:
        print(f"Error counting interns: {e}")
        return 0

def main():
    """Main function"""
    count = count_interns()
    
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total interns in intern_avail_fall.csv: {count}")
    print(f"This represents the total pool of Fall 2025 applicants")

if __name__ == "__main__":
    main()
