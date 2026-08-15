#!/usr/bin/env python3
"""
Check the Intern Availability sheet and use its Restaurant column
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_intern_availability_sheet():
    """Check the Intern Availability sheet structure"""
    print("="*80)
    print("CHECKING INTERN AVAILABILITY SHEET")
    print("Looking at Restaurant column in Intern Availability")
    print("="*80)
    
    try:
        # Load Intern Availability sheet
        print("\n1. LOADING INTERN AVAILABILITY SHEET")
        print("-" * 40)
        
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        
        # Try different sheet names
        sheet_names = ['Intern Availability', 'Intern-availability', 'Intern Availability Sheet', 'Intern-Availability']
        
        df_intern_avail = None
        sheet_used = None
        
        for sheet_name in sheet_names:
            try:
                df_intern_avail = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheet_used = sheet_name
                print(f"Successfully loaded sheet: '{sheet_name}'")
                break
            except:
                continue
        
        if df_intern_avail is None:
            print("Could not find Intern Availability sheet. Trying all sheets...")
            xl_file = pd.ExcelFile(excel_file)
            print(f"Available sheets: {xl_file.sheet_names}")
            
            for sheet_name in xl_file.sheet_names:
                if 'intern' in sheet_name.lower() and 'avail' in sheet_name.lower():
                    try:
                        df_intern_avail = pd.read_excel(excel_file, sheet_name=sheet_name)
                        sheet_used = sheet_name
                        print(f"Found and loaded: '{sheet_name}'")
                        break
                    except:
                        continue
        
        if df_intern_avail is None:
            print("ERROR: Could not find any Intern Availability sheet")
            return False
        
        print(f"Loaded {len(df_intern_avail)} rows from '{sheet_used}'")
        print(f"Columns: {list(df_intern_avail.columns)}")
        
        # Look for Restaurant column
        restaurant_columns = [col for col in df_intern_avail.columns if 'restaurant' in col.lower()]
        print(f"Restaurant-related columns: {restaurant_columns}")
        
        # Show sample data
        print(f"\n2. SAMPLE DATA FROM INTERN AVAILABILITY")
        print("-" * 40)
        
        # Find name columns
        name_columns = [col for col in df_intern_avail.columns if 'name' in col.lower() or 'intern' in col.lower()]
        print(f"Name-related columns: {name_columns}")
        
        # Show first few rows with relevant columns
        relevant_cols = name_columns + restaurant_columns
        if relevant_cols:
            print("Sample data:")
            for idx, row in df_intern_avail.head(5).iterrows():
                print(f"  Row {idx}:")
                for col in relevant_cols:
                    if col in df_intern_avail.columns:
                        value = row[col]
                        if pd.notna(value):
                            print(f"    {col}: {value}")
                print()
        
        return df_intern_avail, sheet_used
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def compare_restaurant_columns():
    """Compare restaurant columns between Active Intern List and Intern Availability"""
    print("="*80)
    print("COMPARING RESTAURANT COLUMNS")
    print("Active Intern List vs Intern Availability")
    print("="*80)
    
    try:
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        
        # Load Active Intern List
        df_active = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        print(f"Active Intern List: {len(df_active)} rows")
        print(f"Columns: {list(df_active.columns)}")
        
        # Load Intern Availability
        df_avail, sheet_name = check_intern_availability_sheet()
        
        if df_avail is None:
            return False
        
        print(f"\nIntern Availability ({sheet_name}): {len(df_avail)} rows")
        print(f"Columns: {list(df_avail.columns)}")
        
        # Find restaurant columns
        active_restaurant_col = None
        for col in df_active.columns:
            if 'restaurant' in col.lower():
                active_restaurant_col = col
                break
        
        avail_restaurant_col = None
        for col in df_avail.columns:
            if 'restaurant' in col.lower():
                avail_restaurant_col = col
                break
        
        print(f"\nActive Intern List restaurant column: {active_restaurant_col}")
        print(f"Intern Availability restaurant column: {avail_restaurant_col}")
        
        # Compare data for some interns
        print(f"\n3. COMPARING RESTAURANT ASSIGNMENTS")
        print("-" * 40)
        
        # Find name columns
        active_name_col = None
        for col in df_active.columns:
            if 'name' in col.lower():
                active_name_col = col
                break
        
        avail_name_col = None
        for col in df_avail.columns:
            if 'name' in col.lower() or 'intern' in col.lower():
                avail_name_col = col
                break
        
        print(f"Active name column: {active_name_col}")
        print(f"Availability name column: {avail_name_col}")
        
        if active_restaurant_col and avail_restaurant_col and active_name_col and avail_name_col:
            # Compare first 10 interns
            print("\nComparing restaurant assignments:")
            for idx, row in df_active.head(10).iterrows():
                active_name = str(row[active_name_col]).strip()
                active_restaurant = str(row[active_restaurant_col]).strip()
                
                # Find matching intern in availability sheet
                match = df_avail[df_avail[avail_name_col].str.contains(active_name.split()[0], na=False, case=False)]
                
                if not match.empty:
                    avail_name = str(match.iloc[0][avail_name_col]).strip()
                    avail_restaurant = str(match.iloc[0][avail_restaurant_col]).strip()
                    
                    print(f"  {active_name}:")
                    print(f"    Active List: {active_restaurant}")
                    print(f"    Availability: {avail_restaurant}")
                    
                    if active_restaurant != avail_restaurant:
                        print(f"    *** DIFFERENT ***")
                    else:
                        print(f"    *** SAME ***")
                    print()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Checking Intern Availability sheet for restaurant data...")
    
    success = compare_restaurant_columns()
    
    print(f"\n" + "="*80)
    print("INTERN AVAILABILITY SHEET CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
