#!/usr/bin/env python3
"""
Examine the restaurant column in Active Intern List for Fall 2025 matches
"""

import pandas as pd

def examine_restaurant_column():
    """Examine the restaurant column for Fall 2025 interns"""
    print("=== EXAMINING RESTAURANT COLUMN FOR FALL 2025 ===")
    
    try:
        # Load Active Intern List sheet
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        print(f"Active Intern List shape: {active_df.shape}")
        print(f"Columns: {list(active_df.columns)}")
        
        # Look at the header row to understand column structure
        print(f"\n--- HEADER ROW (Row 337) ---")
        if 337 < len(active_df):
            header_row = active_df.iloc[337]
            for col_idx, value in enumerate(header_row):
                if pd.notna(value) and str(value).strip():
                    print(f"Column {col_idx}: {value}")
        
        # Examine Fall 2025 section (rows 338-367)
        print(f"\n--- FALL 2025 INTERNS WITH RESTAURANT ASSIGNMENTS ---")
        
        fall_2025_interns = []
        
        for idx in range(338, 367):
            if idx < len(active_df):
                row = active_df.iloc[idx]
                
                # Get intern name (first column)
                intern_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                
                if intern_name and intern_name.lower() != 'nan' and 'latitude' not in intern_name.lower():
                    # Look through all columns for restaurant assignment
                    restaurant_assignment = None
                    restaurant_col_idx = None
                    
                    for col_idx in range(len(row)):
                        value = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ''
                        
                        # Look for restaurant names (not empty, not generic codes)
                        if (value and value.lower() != 'nan' and 
                            value not in ['960', 'Success Centers', ''] and
                            len(value) > 3 and
                            not any(char.isdigit() for char in value[:4])):  # Not starting with numbers
                            
                            restaurant_assignment = value
                            restaurant_col_idx = col_idx
                            break
                    
                    fall_2025_interns.append({
                        'row': idx,
                        'name': intern_name,
                        'restaurant': restaurant_assignment,
                        'restaurant_col': restaurant_col_idx,
                        'all_values': [str(val) if pd.notna(val) else '' for val in row]
                    })
        
        print(f"Found {len(fall_2025_interns)} Fall 2025 interns:")
        
        for intern in fall_2025_interns:
            print(f"Row {intern['row']}: {intern['name']} -> {intern['restaurant']}")
            
            # Show some context around the restaurant column
            if intern['restaurant_col']:
                print(f"  Restaurant column: {intern['restaurant_col']}")
                # Show values around the restaurant column
                start_col = max(0, intern['restaurant_col'] - 2)
                end_col = min(len(intern['all_values']), intern['restaurant_col'] + 3)
                context_values = intern['all_values'][start_col:end_col]
                print(f"  Context: {context_values}")
        
        return fall_2025_interns
        
    except Exception as e:
        print(f"Error examining restaurant column: {e}")
        return []

def find_restaurant_column_pattern():
    """Find the pattern of restaurant assignments"""
    print("\n=== FINDING RESTAURANT COLUMN PATTERN ===")
    
    try:
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Look at a few specific rows to understand the pattern
        sample_rows = [338, 340, 342, 345, 348, 350, 355, 358]
        
        for row_idx in sample_rows:
            if row_idx < len(active_df):
                row = active_df.iloc[row_idx]
                intern_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                
                print(f"\nRow {row_idx}: {intern_name}")
                
                # Show all non-empty values
                for col_idx, value in enumerate(row):
                    if pd.notna(value):
                        val_str = str(value).strip()
                        if val_str and val_str.lower() != 'nan':
                            print(f"  Col {col_idx}: {val_str}")
        
        # Look for the restaurant column by examining the header
        print(f"\n--- HEADER ANALYSIS ---")
        if 337 < len(active_df):
            header_row = active_df.iloc[337]
            for col_idx, value in enumerate(header_row):
                if pd.notna(value) and str(value).strip():
                    val_str = str(value).strip()
                    if 'restaurant' in val_str.lower() or 'placement' in val_str.lower():
                        print(f"Potential restaurant column: {col_idx} = {val_str}")
                        
                        # Show some examples from this column
                        print(f"  Examples from this column:")
                        for row_idx in range(338, 348):
                            if row_idx < len(active_df):
                                cell_value = active_df.iloc[row_idx, col_idx]
                                if pd.notna(cell_value):
                                    intern_name = str(active_df.iloc[row_idx, 0]).strip()
                                    restaurant = str(cell_value).strip()
                                    print(f"    {intern_name} -> {restaurant}")
        
    except Exception as e:
        print(f"Error finding restaurant column pattern: {e}")

if __name__ == "__main__":
    fall_2025_interns = examine_restaurant_column()
    find_restaurant_column_pattern()
    
    print(f"\n=== RESTAURANT COLUMN ANALYSIS COMPLETE ===")
