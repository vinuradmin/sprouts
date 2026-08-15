#!/usr/bin/env python3
"""
Find the most recent Fall data in the Excel file
"""

import pandas as pd
from datetime import datetime

def find_recent_fall_data():
    """Find the most recent Fall data"""
    print("=== FINDING RECENT FALL DATA ===")
    
    try:
        excel_file = pd.ExcelFile('C:/Users/pierr/Downloads/sprouts data.xlsx')
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Check each sheet for recent data
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Examining sheet: {sheet_name} ---")
            
            try:
                sheet_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name=sheet_name)
                print(f"Shape: {sheet_df.shape}")
                
                # Look for date patterns that might indicate recent data
                recent_entries = []
                
                for col_idx, col in enumerate(sheet_df.columns):
                    for row_idx, value in enumerate(sheet_df[col]):
                        if pd.notna(value):
                            val_str = str(value)
                            
                            # Look for 2024 or 2025 dates
                            if '2024' in val_str or '2025' in val_str:
                                recent_entries.append({
                                    'column': col,
                                    'row': row_idx,
                                    'value': val_str,
                                    'col_idx': col_idx,
                                    'row_idx': row_idx
                                })
                
                if recent_entries:
                    print(f"Found {len(recent_entries)} recent entries:")
                    for item in recent_entries[:10]:
                        print(f"  Row {item['row']}, Col {item['col_idx']}: {item['value']}")
                
                # Look for Fall specifically with recent years
                fall_recent = []
                for col_idx, col in enumerate(sheet_df.columns):
                    col_str = str(col).lower()
                    if 'fall' in col_str:
                        for row_idx, value in enumerate(sheet_df[col]):
                            if pd.notna(value):
                                val_str = str(value)
                                if '2024' in val_str or '2025' in val_str:
                                    fall_recent.append({
                                        'column': col,
                                        'row': row_idx,
                                        'value': val_str,
                                        'col_idx': col_idx,
                                        'row_idx': row_idx
                                    })
                
                if fall_recent:
                    print(f"Found {len(fall_recent)} recent Fall entries:")
                    for item in fall_recent:
                        print(f"  Row {item['row']}, Col {item['col_idx']}: {item['value']}")
                        
                        # Get the intern name from first column
                        if row_idx < len(sheet_df):
                            name_val = sheet_df.iloc[row_idx, 0]
                            if pd.notna(name_val):
                                print(f"    Intern: {name_val}")
                
            except Exception as e:
                print(f"Error examining sheet {sheet_name}: {e}")
    
    except Exception as e:
        print(f"Error: {e}")

def check_for_2025_fall():
    """Specifically check for 2025 Fall data"""
    print("\n=== CHECKING FOR 2025 FALL DATA ===")
    
    try:
        # Check if there's a sheet with 2025 data
        excel_file = pd.ExcelFile('C:/Users/pierr/Downloads/sprouts data.xlsx')
        
        for sheet_name in excel_file.sheet_names:
            if '2025' in sheet_name.lower() or 'fall' in sheet_name.lower():
                print(f"Checking sheet: {sheet_name}")
                
                try:
                    sheet_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name=sheet_name)
                    print(f"Shape: {sheet_df.shape}")
                    print(f"Columns: {list(sheet_df.columns)}")
                    
                    # Show first few rows
                    print("First few rows:")
                    for idx, row in sheet_df.iterrows():
                        if idx < 5:
                            row_values = [str(val) if pd.notna(val) else '' for val in row]
                            non_empty = [val for val in row_values if val.strip() and val.strip().lower() != 'nan']
                            if non_empty:
                                print(f"  Row {idx}: {non_empty}")
                        else:
                            break
                            
                except Exception as e:
                    print(f"Error reading sheet {sheet_name}: {e}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_recent_fall_data()
    check_for_2025_fall()
    print("\n=== SEARCH COMPLETE ===")
