#!/usr/bin/env python3
"""
Check Excel structure more carefully
"""

import pandas as pd

def check_excel_structure():
    """Check Excel structure in detail"""
    print("="*80)
    print("CHECKING EXCEL STRUCTURE IN DETAIL")
    print("="*80)
    
    try:
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        
        # Try different header rows
        for header_row in [0, 1, 2]:
            print(f"\n--- Trying header row {header_row} ---")
            try:
                df = pd.read_excel(excel_file, sheet_name='Active Intern List', header=header_row)
                print(f"Columns with header {header_row}:")
                for i, col in enumerate(df.columns[:20]):  # Show first 20
                    print(f"  {i}: {col}")
                
                # Look for name and restaurant in first few rows
                if not df.empty:
                    print(f"\nFirst row data:")
                    for i, (col, val) in enumerate(df.iloc[0].items()):
                        if i < 20:  # Show first 20
                            print(f"  {col}: {val}")
                
            except Exception as e:
                print(f"Error with header {header_row}: {e}")
        
        # Try without header and look at raw data
        print(f"\n--- Raw data (no header) ---")
        df = pd.read_excel(excel_file, sheet_name='Active Intern List', header=None)
        print(f"Shape: {df.shape}")
        
        # Show first few rows of raw data
        print(f"\nFirst 3 rows of raw data:")
        for i in range(min(3, len(df))):
            print(f"Row {i}:")
            for j, val in enumerate(df.iloc[i]):
                if j < 15:  # Show first 15 columns
                    print(f"  Col {j}: {val}")
                if j == 14:  # Column 15 (index 14) - this should be restaurant
                    print(f"  ^^^ This should be restaurant column")
        
        return
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_excel_structure()
