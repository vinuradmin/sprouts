#!/usr/bin/env python3
"""
Check if availability data issue comes from CSV vs database mismatch
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_csv_availability():
    """Check CSV availability data vs database"""
    print("="*80)
    print("CHECKING CSV AVAILABILITY DATA")
    print("Comparing CSV availability with database availability")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Intern
        
        app = create_app()
        app.app_context().push()
        
        # Load intern availability CSV
        print("\n1. LOADING CSV AVAILABILITY DATA")
        print("-" * 40)
        
        try:
            intern_csv_path = '../intern_avail_fall.csv'
            df_intern = pd.read_csv(intern_csv_path)
            print(f"Loaded intern availability CSV: {len(df_intern)} rows")
            print(f"CSV columns: {list(df_intern.columns)}")
            
            # Show sample data
            print(f"\nSample intern availability data:")
            for idx, row in df_intern.head(3).iterrows():
                print(f"  {row.get('First Name', 'N/A')} {row.get('Last Name', 'N/A')}:")
                for col in df_intern.columns:
                    if col not in ['First Name', 'Last Name', 'Email Address'] and pd.notna(row[col]):
                        if 'Monday' in col or 'Tuesday' in col or 'Wednesday' in col or 'Thursday' in col or 'Friday' in col or 'Saturday' in col or 'Sunday' in col:
                            print(f"    {col}: {row[col]}")
        except Exception as e:
            print(f"Error loading intern CSV: {e}")
            df_intern = None
        
        # Load restaurant availability CSV
        print(f"\n2. LOADING RESTAURANT AVAILABILITY DATA")
        print("-" * 40)
        
        try:
            restaurant_csv_path = '../chef_avail_fall.csv'
            df_restaurant = pd.read_csv(restaurant_csv_path)
            print(f"Loaded restaurant availability CSV: {len(df_restaurant)} rows")
            print(f"CSV columns: {list(df_restaurant.columns)}")
        except Exception as e:
            print(f"Error loading restaurant CSV: {e}")
            df_restaurant = None
        
        # Check our specific problem cases
        print(f"\n3. CHECKING PROBLEM CASES IN CSV")
        print("-" * 40)
        
        problem_cases = [
            {'name': 'Eric Willis', 'email': 'Ericg@foreigncinema.com'},
            {'name': 'Gavin Patane', 'email': 'Gavin@sirene-oak.com'},
            {'name': 'Andrea Caballero', 'email': 'andreacaballeropb@gmail.com'}
        ]
        
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        
        for case in problem_cases:
            print(f"\n{case['name']}:")
            
            # Find intern in database
            intern = None
            for i in interns:
                if case['name'] in i.user.full_name or i.user.full_name in case['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"  Not found in database")
                continue
            
            print(f"  Database: {intern.user.full_name}")
            
            # Show database availability
            if intern.availability:
                print(f"  Database availability:")
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    am = getattr(intern.availability, f'{day}_am')
                    pm = getattr(intern.availability, f'{day}_pm')
                    status = ""
                    if am: status += "AM "
                    if pm: status += "PM "
                    if not status: status = "None"
                    print(f"    {day.capitalize()}: {status}")
            else:
                print(f"  Database availability: NO DATA")
            
            # Check CSV availability
            if df_intern is not None:
                print(f"  CSV availability search:")
                
                # Try different name matching
                csv_matches = []
                
                # Exact match by first name
                first_name = case['name'].split()[0]
                exact_match = df_intern[df_intern['First Name'] == first_name]
                if not exact_match.empty:
                    csv_matches.append(('First Name', exact_match.iloc[0]))
                
                # Email match
                if 'Email Address' in df_intern.columns:
                    email_match = df_intern[df_intern['Email Address'] == case['email']]
                    if not email_match.empty and exact_match.empty:
                        csv_matches.append(('Email', email_match.iloc[0]))
                
                if csv_matches:
                    for match_type, csv_row in csv_matches:
                        print(f"    Found by {match_type} match:")
                        print(f"      CSV Name: '{csv_row.get('Intern Name', 'N/A')}'")
                        
                        # Show CSV availability
                        for col in df_intern.columns:
                            if col != 'Intern Name' and col != 'Email' and pd.notna(csv_row[col]):
                                value = str(csv_row[col]).strip()
                                if value and value != 'nan' and value != 'Unavailable':
                                    print(f"      {col}: {value}")
                else:
                    print(f"    No CSV match found")
        
        # Check Excel data too
        print(f"\n4. CHECKING EXCEL AVAILABILITY DATA")
        print("-" * 40)
        
        try:
            excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
            df_excel = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
            
            print(f"Loaded Excel data: {len(df_excel)} rows")
            
            # Look for availability columns
            availability_cols = [col for col in df_excel.columns if 'avail' in col.lower() or 'schedule' in col.lower() or 'mon' in col.lower() or 'tue' in col.lower()]
            
            if availability_cols:
                print(f"Found availability-related columns: {availability_cols}")
                
                for case in problem_cases:
                    print(f"\n{case['name']} in Excel:")
                    
                    excel_match = df_excel[df_excel['Name'].str.contains(case['name'].split()[0], na=False, case=False)]
                    
                    if not excel_match.empty:
                        for idx, row in excel_match.iterrows():
                            print(f"  Row {idx}: {row['Name']}")
                            for col in availability_cols[:5]:  # Show first 5
                                if pd.notna(row[col]):
                                    print(f"    {col}: {row[col]}")
                    else:
                        print(f"  No match found")
            else:
                print("No availability columns found in Excel")
                
        except Exception as e:
            print(f"Error checking Excel: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    check_csv_availability()
    
    print(f"\n" + "="*80)
    print("CSV AVAILABILITY CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
