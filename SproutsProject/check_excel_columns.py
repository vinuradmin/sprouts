#!/usr/bin/env python3
"""
Check Excel column names to fix the investigation
"""

import pandas as pd

def check_excel_columns():
    """Check Excel column names"""
    print("="*80)
    print("CHECKING EXCEL COLUMN NAMES")
    print("="*80)
    
    try:
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_file, sheet_name='Active Intern List')
        
        print(f"Excel shape: {df.shape}")
        print(f"Columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        print(f"\nFirst few rows:")
        print(df.head(3).to_string())
        
        return df.columns.tolist()
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    check_excel_columns()
