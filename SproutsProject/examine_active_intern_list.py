#!/usr/bin/env python3
"""
Examine the Active Intern List sheet around rows 339-368 for Fall 2025 data
"""

import pandas as pd

def examine_active_intern_list():
    """Examine Active Intern List around rows 339-368"""
    print("=== EXAMINING ACTIVE INTERN LIST ===")
    
    try:
        # Load Active Intern List sheet
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        print(f"Active Intern List sheet shape: {active_df.shape}")
        print(f"Columns: {list(active_df.columns)}")
        
        # Examine rows around 339-368
        start_row = 330
        end_row = 380
        
        print(f"\n--- Rows {start_row} to {end_row} ---")
        
        for idx in range(start_row, end_row + 1):
            if idx < len(active_df):
                row = active_df.iloc[idx]
                row_values = [str(val) if pd.notna(val) else '' for val in row]
                non_empty_values = [val for val in row_values if val.strip() and val.strip().lower() != 'nan']
                
                if non_empty_values:
                    print(f"Row {idx}: {non_empty_values}")
                    
                    # Look for Fall 2025 indicators
                    for val in non_empty_values:
                        if 'fall' in val.lower() and ('2025' in val or '25' in val):
                            print(f"  ^^^ FALL 2025 INDICATOR: {val}")
        
        # Look for delimitation patterns
        print(f"\n--- LOOKING FOR FALL 2025 DELIMITATION ---")
        
        fall_2025_start = None
        fall_2025_interns = []
        
        for idx in range(start_row, end_row + 1):
            if idx < len(active_df):
                row = active_df.iloc[idx]
                row_values = [str(val) if pd.notna(val) else '' for val in row]
                
                # Check for delimitation markers
                for col_idx, val in enumerate(row_values):
                    if 'fall' in val.lower() and ('2025' in val or '25' in val):
                        fall_2025_start = idx
                        print(f"Found Fall 2025 delimitation at Row {idx}, Column {col_idx}: {val}")
                        break
                
                if fall_2025_start:
                    # Collect intern names after delimitation
                    first_col_val = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
                    if first_col_val and first_col_val.strip() and first_col_val.lower() != 'nan':
                        # Check if this looks like an intern name (not a header)
                        if not any(keyword in first_col_val.lower() for keyword in ['fall', '2025', 'total', 'summary', 'name']):
                            fall_2025_interns.append({
                                'row': idx,
                                'name': first_col_val,
                                'full_row': row_values
                            })
        
        if fall_2025_interns:
            print(f"\nFound {len(fall_2025_interns)} potential Fall 2025 interns:")
            for intern in fall_2025_interns:
                print(f"  Row {intern['row']}: {intern['name']}")
                # Show some additional info from the row
                if len(intern['full_row']) > 1:
                    additional_info = [val for val in intern['full_row'][1:5] if val.strip() and val.strip().lower() != 'nan']
                    if additional_info:
                        print(f"    Additional info: {additional_info}")
        else:
            print("No Fall 2025 interns found in the specified range")
        
        return fall_2025_interns
        
    except Exception as e:
        print(f"Error examining Active Intern List: {e}")
        return []

def get_fall_2025_matches(fall_2025_interns):
    """Get actual matches for Fall 2025 interns"""
    print("\n=== GETTING FALL 2025 MATCHES ===")
    
    if not fall_2025_interns:
        print("No Fall 2025 interns to match")
        return []
    
    try:
        # Load Contact Info sheet
        contact_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Contact Info')
        print(f"Contact Info sheet shape: {contact_df.shape}")
        
        # Get all actual matches
        actual_matches = []
        
        for idx, row in contact_df.iterrows():
            intern_name = str(row['CT Intern']).strip() if pd.notna(row['CT Intern']) else ''
            restaurant_name = str(row['Restaurant Host']).strip() if pd.notna(row['Restaurant Host']) else ''
            
            if intern_name and restaurant_name and intern_name != 'nan' and restaurant_name != 'nan':
                actual_matches.append({
                    'intern_name': intern_name,
                    'restaurant_name': restaurant_name
                })
        
        print(f"Found {len(actual_matches)} total actual matches")
        
        # Match Fall 2025 interns with actual matches
        fall_2025_matches = []
        
        for fall_intern in fall_2025_interns:
            fall_name = fall_intern['name']
            
            for match in actual_matches:
                actual_name = match['intern_name']
                
                # Check for name match
                if (fall_name.lower() in actual_name.lower() or 
                    actual_name.lower() in fall_name.lower() or
                    fall_name.split()[0].lower() in actual_name.lower() or
                    actual_name.split()[0].lower() in fall_name.lower()):
                    
                    fall_2025_matches.append({
                        'fall_intern': fall_name,
                        'actual_match': actual_name,
                        'restaurant': match['restaurant_name'],
                        'row': fall_intern['row']
                    })
                    break
        
        print(f"\nFall 2025 interns with actual matches ({len(fall_2025_matches)}):")
        for match in fall_2025_matches:
            print(f"  - {match['fall_intern']} -> {match['restaurant']} (matched as: {match['actual_match']})")
        
        return fall_2025_matches
        
    except Exception as e:
        print(f"Error getting Fall 2025 matches: {e}")
        return []

if __name__ == "__main__":
    # Examine Active Intern List
    fall_2025_interns = examine_active_intern_list()
    
    if fall_2025_interns:
        # Get matches
        fall_2025_matches = get_fall_2025_matches(fall_2025_interns)
        
        print(f"\n=== SUMMARY ===")
        print(f"Fall 2025 interns found: {len(fall_2025_interns)}")
        print(f"With actual matches: {len(fall_2025_matches)}")
        print(f"Without matches: {len(fall_2025_interns) - len(fall_2025_matches)}")
    
    print("\n=== EXAMINATION COMPLETE ===")
