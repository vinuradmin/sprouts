#!/usr/bin/env python3
"""
Examine all sheets in the Excel file to find Fall 2025 data
"""

import pandas as pd

def examine_all_sheets():
    """Examine all sheets to find Fall 2025 data"""
    print("=== EXAMINING ALL SHEETS ===")
    
    try:
        excel_file = pd.ExcelFile('C:/Users/pierr/Downloads/sprouts data.xlsx')
        print(f"Sheet names: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            sheet_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name=sheet_name)
            print(f"Shape: {sheet_df.shape}")
            print(f"Columns: {list(sheet_df.columns)}")
            
            # Look for Fall-related content
            fall_content = []
            
            for col_idx, col in enumerate(sheet_df.columns):
                for row_idx, value in enumerate(sheet_df[col]):
                    if pd.notna(value):
                        val_str = str(value).lower()
                        if 'fall' in val_str:
                            fall_content.append({
                                'column': col,
                                'row': row_idx,
                                'value': str(value),
                                'col_idx': col_idx,
                                'row_idx': row_idx
                            })
            
            if fall_content:
                print(f"Found {len(fall_content)} Fall-related entries:")
                for item in fall_content[:10]:  # Show first 10
                    print(f"  Row {item['row']}, Col {item['col_idx']}: {item['value']}")
                
                # Look for the most recent Fall data
                if fall_content:
                    # Find the rightmost Fall column (most recent)
                    max_col_idx = max(item['col_idx'] for item in fall_content)
                    latest_fall_col = None
                    
                    for item in fall_content:
                        if item['col_idx'] == max_col_idx:
                            latest_fall_col = item['column']
                            break
                    
                    print(f"Latest Fall column: {latest_fall_col}")
                    
                    # Extract data from that column
                    if latest_fall_col:
                        print(f"\nData from {latest_fall_col}:")
                        for row_idx, value in enumerate(sheet_df[latest_fall_col]):
                            if pd.notna(value) and str(value).strip() and str(value).lower() != 'nan':
                                # Also get the name from the first column
                                name_val = sheet_df.iloc[row_idx, 0] if row_idx < len(sheet_df) else ''
                                if pd.notna(name_val) and str(name_val).strip() and str(name_val).lower() != 'nan':
                                    print(f"  {name_val} -> {value}")
            else:
                print("No Fall-related content found")
    
    except Exception as e:
        print(f"Error examining sheets: {e}")

if __name__ == "__main__":
    examine_all_sheets()
