#!/usr/bin/env python3
"""
Extract Fall 2022 interns from Excel file
"""

import pandas as pd

def extract_fall_interns():
    """Extract Fall 2022 interns"""
    print("=== EXTRACTING FALL 2022 INTERNS ===")
    
    try:
        # Load Internship Duration sheet
        duration_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Internship Duration')
        print(f"Internship Duration sheet shape: {duration_df.shape}")
        print(f"Columns: {list(duration_df.columns)}")
        
        # Display first few rows to understand structure
        print("\nFirst few rows:")
        for idx, row in duration_df.iterrows():
            if idx < 10:
                row_values = [str(val) if pd.notna(val) else '' for val in row]
                non_empty_values = [val for val in row_values if val.strip() and val.strip().lower() != 'nan']
                print(f"Row {idx}: {non_empty_values}")
        
        # Find Fall 2022 column
        fall_col = None
        name_col = None
        
        for col in duration_df.columns:
            col_lower = str(col).lower()
            if 'fall' in col_lower and '22' in col_lower:
                fall_col = col
            elif 'name' in col_lower:
                name_col = col
        
        print(f"\nDetected columns:")
        print(f"Name column: {name_col}")
        print(f"Fall 2022 column: {fall_col}")
        
        if name_col and fall_col:
            fall_interns = []
            for idx, row in duration_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                intern_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
                fall_info = str(row[fall_col]).strip() if pd.notna(row[fall_col]) else ''
                
                if intern_name and intern_name != 'nan' and intern_name.strip():
                    fall_interns.append({
                        'intern_name': intern_name,
                        'fall_info': fall_info,
                        'has_fall': fall_info and fall_info != 'nan' and fall_info.strip()
                    })
            
            print(f"\nFound {len(fall_interns)} total interns:")
            
            # Filter for Fall 2022 interns
            fall_2022_interns = [intern for intern in fall_interns if intern['has_fall']]
            
            print(f"Fall 2022 interns ({len(fall_2022_interns)}):")
            for intern in fall_2022_interns:
                print(f"  - {intern['intern_name']}: {intern['fall_info']}")
            
            return fall_2022_interns
        else:
            print("Could not identify name or Fall 2022 columns")
            return []
            
    except Exception as e:
        print(f"Error extracting Fall interns: {e}")
        return []

if __name__ == "__main__":
    fall_interns = extract_fall_interns()
    print(f"\nExtracted {len(fall_interns)} Fall 2022 interns")
