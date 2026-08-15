#!/usr/bin/env python3
"""
Extract Fall 2025 interns from the Internship Duration sheet
"""

import pandas as pd

def extract_fall_2025_interns():
    """Extract Fall 2025 interns"""
    print("=== EXTRACTING FALL 2025 INTERNS ===")
    
    try:
        # Load Internship Duration sheet
        duration_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Internship Duration')
        print(f"Internship Duration sheet shape: {duration_df.shape}")
        print(f"Columns: {list(duration_df.columns)}")
        
        # Look for all Fall columns
        fall_columns = []
        for col in duration_df.columns:
            col_str = str(col).lower()
            if 'fall' in col_str:
                fall_columns.append(col)
        
        print(f"\nFall columns found: {fall_columns}")
        
        # Get the last Fall column (most recent)
        if fall_columns:
            latest_fall_col = fall_columns[-1]
            print(f"Latest Fall column: {latest_fall_col}")
            
            # Extract data from that column
            fall_2025_interns = []
            
            for row_idx, row in duration_df.iterrows():
                # Get intern name from first column
                name_col = duration_df.columns[0]
                intern_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
                
                # Get Fall data
                fall_data = str(row[latest_fall_col]).strip() if pd.notna(row[latest_fall_col]) else ''
                
                if intern_name and intern_name != 'nan' and intern_name.strip():
                    fall_2025_interns.append({
                        'intern_name': intern_name,
                        'fall_data': fall_data,
                        'has_fall': fall_data and fall_data != 'nan' and fall_data.strip()
                    })
            
            print(f"\nFound {len(fall_2025_interns)} total interns")
            
            # Filter for interns with Fall data
            fall_interns = [intern for intern in fall_2025_interns if intern['has_fall']]
            
            print(f"\nFall interns ({len(fall_interns)}):")
            for intern in fall_interns:
                print(f"  - {intern['intern_name']}: {intern['fall_data']}")
            
            return fall_interns
        else:
            print("No Fall columns found")
            return []
            
    except Exception as e:
        print(f"Error extracting Fall 2025 interns: {e}")
        return []

def get_actual_matches_for_fall_interns(fall_interns):
    """Get actual matches for Fall interns"""
    print("\n=== GETTING ACTUAL MATCHES FOR FALL INTERNS ===")
    
    try:
        # Load Contact Info sheet
        contact_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Contact Info')
        print(f"Contact Info sheet shape: {contact_df.shape}")
        
        # Get actual matches
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
        
        # Filter for Fall interns
        fall_actual_matches = []
        
        for fall_intern in fall_interns:
            fall_name = fall_intern['intern_name']
            
            for match in actual_matches:
                actual_name = match['intern_name']
                
                # Check for name match (allowing for variations)
                if (fall_name.lower() in actual_name.lower() or 
                    actual_name.lower() in fall_name.lower() or
                    fall_name.split()[0].lower() in actual_name.lower() or
                    actual_name.split()[0].lower() in fall_name.lower()):
                    
                    fall_actual_matches.append({
                        'fall_intern': fall_intern['intern_name'],
                        'actual_match': actual_name,
                        'restaurant': match['restaurant_name'],
                        'fall_data': fall_intern['fall_data']
                    })
                    break
        
        print(f"\nFall interns with actual matches ({len(fall_actual_matches)}):")
        for match in fall_actual_matches:
            print(f"  - {match['fall_intern']} -> {match['restaurant']} (matched as: {match['actual_match']})")
        
        return fall_actual_matches
        
    except Exception as e:
        print(f"Error getting actual matches: {e}")
        return []

if __name__ == "__main__":
    # Extract Fall 2025 interns
    fall_interns = extract_fall_2025_interns()
    
    if fall_interns:
        # Get actual matches
        fall_actual_matches = get_actual_matches_for_fall_interns(fall_interns)
        
        print(f"\n=== SUMMARY ===")
        print(f"Fall interns: {len(fall_interns)}")
        print(f"With actual matches: {len(fall_actual_matches)}")
        print(f"Without matches: {len(fall_interns) - len(fall_actual_matches)}")
    
    print("\n=== EXTRACTION COMPLETE ===")
