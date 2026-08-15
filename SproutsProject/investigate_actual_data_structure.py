#!/usr/bin/env python3
"""
Investigate exactly where assignments are located in the actual Excel data
"""

import pandas as pd

def investigate_excel_structure():
    """Investigate the Excel structure to find assignment column"""
    print("="*80)
    print("INVESTIGATING EXCEL DATA STRUCTURE")
    print("Finding exactly where assignments are stored")
    print("="*80)
    
    try:
        # Load the Excel file
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        
        print(f"Excel sheet shape: {df.shape}")
        print(f"Total columns: {len(df.columns)}")
        
        # Show column headers (first few rows)
        print(f"\nCOLUMN HEADERS (First 20 columns):")
        for i, col in enumerate(df.columns[:20]):
            print(f"Column {i}: '{col}'")
        
        print(f"\nCOLUMN HEADERS (Columns 10-20):")
        for i, col in enumerate(df.columns[10:20]):
            print(f"Column {i+10}: '{col}'")
        
        print(f"\nCOLUMN HEADERS (Columns 20-30):")
        for i, col in enumerate(df.columns[20:30]):
            print(f"Column {i+20}: '{col}'")
        
        # Look for Fall 2025 interns (rows 338-367)
        print(f"\n" + "="*60)
        print("FALL 2025 INTERNS (Rows 338-367)")
        print("="*60)
        
        fall_2025_df = df.iloc[337:367].copy()
        print(f"Fall 2025 interns shape: {fall_2025_df.shape}")
        
        # Show sample rows with all columns to identify assignment column
        print(f"\nSAMPLE FALL 2025 DATA (First 5 interns):")
        print("Row | Name | Potential Assignment Columns")
        print("-" * 80)
        
        for idx, row in fall_2025_df.head(5).iterrows():
            actual_row_num = idx + 1  # Excel row number
            name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
            
            # Check various columns for assignments
            potential_assignments = []
            for col_idx in range(5, 25):  # Check columns 5-24
                cell_value = row.iloc[col_idx]
                if pd.notna(cell_value) and str(cell_value).strip() != '':
                    potential_assignments.append(f"Col{col_idx}:{str(cell_value)[:20]}")
            
            print(f"{actual_row_num} | {name:<20} | {' | '.join(potential_assignments[:3])}")
        
        # Look specifically at column 13 (index 12) which I used
        print(f"\n" + "="*60)
        print("INVESTIGATING COLUMN 13 (Index 12)")
        print("="*60)
        
        print(f"\nColumn 13 header: '{df.columns[12]}'")
        print(f"Sample values in column 13 for Fall 2025 interns:")
        
        for idx, row in fall_2025_df.iterrows():
            actual_row_num = idx + 1
            name = row.iloc[1] if pd.notna(row.iloc[1]) else 'No Name'
            col13_value = row.iloc[13] if pd.notna(row.iloc[13]) else 'Empty'
            
            if col13_value != 'Empty':
                print(f"Row {actual_row_num}: {name} -> '{col13_value}'")
        
        # Check other potential assignment columns
        print(f"\n" + "="*60)
        print("CHECKING OTHER POTENTIAL ASSIGNMENT COLUMNS")
        print("="*60)
        
        potential_assignment_cols = [10, 11, 12, 13, 14, 15, 16, 17, 18]
        
        for col_idx in potential_assignment_cols:
            if col_idx < len(df.columns):
                col_header = df.columns[col_idx]
                print(f"\nColumn {col_idx+1} (Index {col_idx}): '{col_header}'")
                
                # Show non-empty values for Fall 2025 interns
                non_empty_values = []
                for idx, row in fall_2025_df.iterrows():
                    cell_value = row.iloc[col_idx]
                    if pd.notna(cell_value) and str(cell_value).strip() != '' and str(cell_value) != 'nan':
                        non_empty_values.append(str(cell_value))
                
                if non_empty_values:
                    print(f"  Non-empty values: {non_empty_values[:5]}")
                else:
                    print(f"  All values are empty")
        
        # Look for restaurant names in the data
        print(f"\n" + "="*60)
        print("SEARCHING FOR RESTAURANT NAMES")
        print("="*60)
        
        restaurant_names = [
            "Millennium", "Snail Bar", "alaMar", "Burdell", "Tarts", "Teranga", 
            "Abaca", "Ofena", "Ssal", "Arquet", "Holbrook", "2 Chix", "Nudibranch"
        ]
        
        print(f"Searching for restaurant names in Fall 2025 data...")
        
        for restaurant in restaurant_names:
            found = False
            for col_idx in range(len(df.columns)):
                for idx, row in fall_2025_df.iterrows():
                    cell_value = str(row.iloc[col_idx]).lower()
                    if restaurant.lower() in cell_value and cell_value != 'nan':
                        if not found:
                            print(f"\n{restaurant} found in:")
                            found = True
                        print(f"  Column {col_idx+1}, Row {idx+338}: '{row.iloc[col_idx]}'")
                        break
                if found:
                    break
        
        return fall_2025_df
        
    except Exception as e:
        print(f"Error investigating Excel structure: {e}")
        return None

def show_specific_assignment_columns():
    """Show specific columns that likely contain assignments"""
    print(f"\n" + "="*80)
    print("SPECIFIC ASSIGNMENT COLUMN ANALYSIS")
    print("="*80)
    
    try:
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Focus on columns around 13-15 which likely contain assignments
        focus_columns = [11, 12, 13, 14, 15, 16, 17, 18]
        
        print(f"\nFall 2025 interns - Assignment columns analysis:")
        print(f"{'Row':<4} | {'Name':<20} | {'Col12':<15} | {'Col13':<15} | {'Col14':<15} | {'Col15':<15}")
        print("-" * 90)
        
        for idx, row in fall_2025_df.iterrows():
            actual_row_num = idx + 338
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else 'No Name'
            
            col12 = str(row.iloc[12]).strip()[:15] if pd.notna(row.iloc[12]) else 'Empty'
            col13 = str(row.iloc[13]).strip()[:15] if pd.notna(row.iloc[13]) else 'Empty'
            col14 = str(row.iloc[14]).strip()[:15] if pd.notna(row.iloc[14]) else 'Empty'
            col15 = str(row.iloc[15]).strip()[:15] if pd.notna(row.iloc[15]) else 'Empty'
            
            # Only show rows that have some data
            if col12 != 'Empty' or col13 != 'Empty' or col14 != 'Empty' or col15 != 'Empty':
                print(f"{actual_row_num:<4} | {name:<20} | {col12:<15} | {col13:<15} | {col14:<15} | {col15:<15}")
        
        # Show column headers
        print(f"\nColumn Headers:")
        for col_idx in focus_columns:
            if col_idx < len(df.columns):
                print(f"Column {col_idx+1}: '{df.columns[col_idx]}'")
        
    except Exception as e:
        print(f"Error showing specific columns: {e}")

def main():
    """Main function"""
    fall_2025_df = investigate_excel_structure()
    show_specific_assignment_columns()
    
    print(f"\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print(f"I looked for assignments in column 13 (index 12) of the Excel sheet.")
    print(f"This column appears to contain restaurant assignments for Fall 2025 interns.")
    print(f"However, many interns show 'Unassigned' or 'Offered Job' statuses.")
    print(f"The assignment column is: '{df.columns[12] if 'df' in locals() else 'Unknown'}'")

if __name__ == "__main__":
    main()
