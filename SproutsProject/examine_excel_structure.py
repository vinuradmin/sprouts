#!/usr/bin/env python3
"""
Examine the Excel file structure to find the actual matches data
"""

import pandas as pd

def examine_excel_structure():
    """Examine Excel file structure in detail"""
    print("=== EXAMINING EXCEL FILE STRUCTURE ===")
    
    # Load the Excel file
    try:
        df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx')
        print(f"Excel file shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Look for non-empty rows
        print("\n=== EXAMINING ROW CONTENT ===")
        
        for idx, row in df.iterrows():
            if idx < 50:  # Check first 50 rows
                row_values = [str(val) if pd.notna(val) else '' for val in row]
                non_empty_values = [val for val in row_values if val.strip() and val.strip().lower() != 'nan']
                
                if non_empty_values:
                    print(f"Row {idx}: {non_empty_values}")
                    
                    # Look for patterns that might indicate matches
                    for val in non_empty_values:
                        if any(keyword in val.lower() for keyword in ['restaurant', 'intern', 'matched', 'assigned']):
                            print(f"  ^^^ Potential match data: {val}")
        
        # Try to find sheets
        print("\n=== CHECKING FOR MULTIPLE SHEETS ===")
        try:
            excel_file = pd.ExcelFile('C:/Users/pierr/Downloads/sprouts data.xlsx')
            print(f"Sheet names: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                print(f"\n--- Sheet: {sheet_name} ---")
                sheet_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name=sheet_name)
                print(f"Shape: {sheet_df.shape}")
                print(f"Columns: {list(sheet_df.columns)}")
                
                # Show first few rows
                for idx, row in sheet_df.iterrows():
                    if idx < 10:
                        row_values = [str(val) if pd.notna(val) else '' for val in row]
                        non_empty_values = [val for val in row_values if val.strip() and val.strip().lower() != 'nan']
                        if non_empty_values:
                            print(f"Row {idx}: {non_empty_values}")
        except Exception as e:
            print(f"Error checking sheets: {e}")
        
        # Look for specific patterns
        print("\n=== SEARCHING FOR MATCH PATTERNS ===")
        
        # Convert entire dataframe to string and search
        df_str = df.astype(str)
        
        for col in df.columns:
            unique_values = df_str[col].unique()
            for val in unique_values:
                if pd.notna(val) and val != 'nan':
                    val_str = str(val)
                    if any(pattern in val_str.lower() for pattern in ['->', 'assigned to', 'matched with', 'works at']):
                        print(f"Found potential match in column '{col}': {val_str}")
        
    except Exception as e:
        print(f"Error examining Excel file: {e}")

if __name__ == "__main__":
    examine_excel_structure()
