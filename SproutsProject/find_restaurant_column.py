#!/usr/bin/env python3
"""
Find the correct "restaurant" column in the Active Intern List sheet
"""

import pandas as pd

def find_restaurant_column():
    """Find the restaurant column we discussed before"""
    print("="*80)
    print("FINDING THE CORRECT 'RESTAURANT' COLUMN")
    print("As we discussed in previous sessions")
    print("="*80)
    
    try:
        # Load the Excel file
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        print(f"Excel sheet shape: {df.shape}")
        print(f"Total columns: {len(df.columns)}")
        
        # Look for column with 'restaurant' in the header
        restaurant_columns = []
        for i, col in enumerate(df.columns):
            if 'restaurant' in str(col).lower():
                restaurant_columns.append((i, col))
        
        print(f"\nColumns with 'restaurant' in header:")
        for idx, col in restaurant_columns:
            print(f"  Column {idx}: '{col}'")
        
        # If no explicit restaurant column, look for it in the data
        if not restaurant_columns:
            print(f"\nNo explicit 'restaurant' column found. Searching in data...")
            
            # Look for restaurant names in each column
            restaurant_names = [
                "Millennium", "Snail Bar", "alaMar", "Burdell", "Tarts", "Teranga", 
                "Abaca", "Ofena", "Ssal", "Arquet", "Holbrook", "2 Chix", "Nudibranch",
                "Mago", "Sirene", "Dalida", "Sorrel", "Rethink", "Foreign Cinema"
            ]
            
            for col_idx in range(len(df.columns)):
                found_restaurants = []
                for restaurant in restaurant_names:
                    # Check if this column contains the restaurant name
                    for idx, row in df.iterrows():
                        cell_value = str(row.iloc[col_idx]).lower()
                        if restaurant.lower() in cell_value and cell_value != 'nan':
                            found_restaurants.append(restaurant)
                            break
                
                if len(found_restaurants) > 2:  # If column has multiple restaurant names
                    print(f"\nColumn {col_idx+1} (Index {col_idx}): '{df.columns[col_idx]}'")
                    print(f"  Contains restaurants: {found_restaurants[:5]}")
                    
                    # Show Fall 2025 data for this column
                    fall_2025_df = df.iloc[337:367].copy()
                    print(f"  Fall 2025 values:")
                    for idx, row in fall_2025_df.iterrows():
                        cell_value = row.iloc[col_idx]
                        if pd.notna(cell_value) and str(cell_value).strip() != '' and str(cell_value) != 'nan':
                            name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
                            print(f"    Row {idx+338}: {name} -> '{cell_value}'")
        
        # Check around column 14-15 where we found restaurants before
        print(f"\n" + "="*60)
        print("CHECKING COLUMNS AROUND RESTAURANT DATA")
        print("="*60)
        
        fall_2025_df = df.iloc[337:367].copy()
        
        # Check columns 12-18 for restaurant assignments
        for col_idx in range(11, 19):
            if col_idx < len(df.columns):
                col_header = df.columns[col_idx]
                print(f"\nColumn {col_idx+1} (Index {col_idx}): '{col_header}'")
                
                # Show Fall 2025 data
                non_empty_values = []
                for idx, row in fall_2025_df.iterrows():
                    cell_value = row.iloc[col_idx]
                    if pd.notna(cell_value) and str(cell_value).strip() != '' and str(cell_value) != 'nan':
                        name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
                        non_empty_values.append(f"{name} -> '{cell_value}'")
                
                if non_empty_values:
                    print(f"  Fall 2025 assignments:")
                    for val in non_empty_values[:10]:
                        print(f"    {val}")
                else:
                    print(f"  All values empty")
        
        # Look specifically for the pattern we discussed
        print(f"\n" + "="*60)
        print("LOOKING FOR THE RESTAURANT ASSIGNMENT PATTERN")
        print("="*60)
        
        # Check if there's a column that has restaurant names for Fall 2025 interns
        for col_idx in range(len(df.columns)):
            restaurant_count = 0
            assignments = []
            
            for idx, row in fall_2025_df.iterrows():
                cell_value = str(row.iloc[col_idx]).strip()
                name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
                
                # Check if this looks like a restaurant assignment
                if (cell_value != '' and cell_value != 'nan' and 
                    any(restaurant.lower() in cell_value.lower() for restaurant in restaurant_names)):
                    restaurant_count += 1
                    assignments.append(f"{name} -> {cell_value}")
            
            if restaurant_count >= 5:  # If this column has 5+ restaurant assignments
                print(f"\nColumn {col_idx+1} (Index {col_idx}): '{df.columns[col_idx]}'")
                print(f"  Restaurant assignments found: {restaurant_count}")
                for assignment in assignments[:8]:
                    print(f"    {assignment}")
        
        return df
        
    except Exception as e:
        print(f"Error finding restaurant column: {e}")
        return None

def check_specific_column():
    """Check the specific column we should be using"""
    print(f"\n" + "="*60)
    print("CHECKING SPECIFIC COLUMN FOR RESTAURANT ASSIGNMENTS")
    print("="*60)
    
    try:
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Let's check column 14 (index 13) which might be the restaurant column
        col_idx = 13  # Column 14
        col_header = df.columns[col_idx]
        
        print(f"Checking Column {col_idx+1} (Index {col_idx}): '{col_header}'")
        print(f"Fall 2025 assignments:")
        
        assignments = []
        for idx, row in fall_2025_df.iterrows():
            cell_value = row.iloc[col_idx]
            name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
            
            if pd.notna(cell_value) and str(cell_value).strip() != '' and str(cell_value) != 'nan':
                assignments.append(f"Row {idx+338}: {name} -> '{cell_value}'")
        
        for assignment in assignments:
            print(f"  {assignment}")
        
        # Also check column 15 (index 14) to compare
        col_idx_2 = 14  # Column 15
        col_header_2 = df.columns[col_idx_2]
        
        print(f"\nColumn {col_idx_2+1} (Index {col_idx_2}): '{col_header_2}'")
        print(f"Fall 2025 assignments:")
        
        assignments_2 = []
        for idx, row in fall_2025_df.iterrows():
            cell_value = row.iloc[col_idx_2]
            name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
            
            if pd.notna(cell_value) and str(cell_value).strip() != '' and str(cell_value) != 'nan':
                assignments_2.append(f"Row {idx+338}: {name} -> '{cell_value}'")
        
        for assignment in assignments_2:
            print(f"  {assignment}")
        
    except Exception as e:
        print(f"Error checking specific column: {e}")

def main():
    """Main function"""
    df = find_restaurant_column()
    check_specific_column()
    
    print(f"\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("Based on our previous discussions, I need to identify the correct")
    print("'restaurant' column in the Active Intern List sheet.")
    print("Let me check which column actually contains the restaurant assignments.")

if __name__ == "__main__":
    main()
