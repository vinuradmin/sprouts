"""
List all interns and restaurants for a specific cohort
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import from main module
from main import (
    read_sheet_data,
    filter_by_cohort,
    find_column_index
)

def list_cohort_data(cohort_name):
    """List all interns and restaurants for a cohort"""
    
    print("=" * 80)
    print(f"LISTING DATA FOR: {cohort_name.upper()}")
    print("=" * 80)
    print()
    
    try:
        # Read data from Google Sheets
        print("Reading data from Google Sheets...")
        intern_data = read_sheet_data('Intern Availabilities')
        chef_data = read_sheet_data('Chef Availabilities')
        print()
        
        # Filter by cohort
        print(f"Filtering by cohort: {cohort_name}")
        filtered_interns = filter_by_cohort(intern_data, cohort_name)
        filtered_chefs = filter_by_cohort(chef_data, cohort_name)
        print()
        
        # Display Interns
        print("=" * 80)
        print(f"INTERNS FOR {cohort_name.upper()}")
        print("=" * 80)
        
        if len(filtered_interns) > 1:
            headers = filtered_interns[0]
            
            # Find key columns
            first_name_col = find_column_index(headers, 'First Name')
            last_name_col = find_column_index(headers, 'Last Name')
            email_col = find_column_index(headers, 'Email Address')
            phone_col = find_column_index(headers, 'intern phone')
            city_col = find_column_index(headers, 'City')
            
            print(f"\nTotal Interns: {len(filtered_interns) - 1}")
            print()
            
            for i, row in enumerate(filtered_interns[1:], 1):
                first_name = row[first_name_col] if first_name_col is not None and len(row) > first_name_col else ''
                last_name = row[last_name_col] if last_name_col is not None and len(row) > last_name_col else ''
                email = row[email_col] if email_col is not None and len(row) > email_col else ''
                phone = row[phone_col] if phone_col is not None and len(row) > phone_col else ''
                city = row[city_col] if city_col is not None and len(row) > city_col else ''
                
                print(f"{i}. {first_name} {last_name}")
                if email:
                    print(f"   Email: {email}")
                if phone:
                    print(f"   Phone: {phone}")
                if city:
                    print(f"   City: {city}")
                print()
        else:
            print("No interns found for this cohort.")
        
        print()
        
        # Display Restaurants/Chefs
        print("=" * 80)
        print(f"RESTAURANTS FOR {cohort_name.upper()}")
        print("=" * 80)
        
        if len(filtered_chefs) > 1:
            headers = filtered_chefs[0]
            
            # Find key columns
            restaurant_col = find_column_index(headers, 'Restaurant Name')
            chef_col = find_column_index(headers, "Primary Mentor's Full Name (First and Last)")
            email_col = find_column_index(headers, "Primary Mentor's Email Address")
            phone_col = find_column_index(headers, "Primary Mentor's Cell Phone Number")
            address_col = find_column_index(headers, 'Restaurant Address')
            city_col = find_column_index(headers, 'Restaurant Location')
            
            print(f"\nTotal Restaurants: {len(filtered_chefs) - 1}")
            print()
            
            for i, row in enumerate(filtered_chefs[1:], 1):
                restaurant = row[restaurant_col] if restaurant_col is not None and len(row) > restaurant_col else ''
                chef = row[chef_col] if chef_col is not None and len(row) > chef_col else ''
                email = row[email_col] if email_col is not None and len(row) > email_col else ''
                phone = row[phone_col] if phone_col is not None and len(row) > phone_col else ''
                address = row[address_col] if address_col is not None and len(row) > address_col else ''
                city = row[city_col] if city_col is not None and len(row) > city_col else ''
                
                print(f"{i}. {restaurant}")
                if chef:
                    print(f"   Chef/Mentor: {chef}")
                if email:
                    print(f"   Email: {email}")
                if phone:
                    print(f"   Phone: {phone}")
                if address:
                    print(f"   Address: {address}")
                if city:
                    print(f"   City: {city}")
                print()
        else:
            print("No restaurants found for this cohort.")
        
        print()
        print("=" * 80)
        print("COMPLETE")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        
        import traceback
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    cohort_name = sys.argv[1] if len(sys.argv) > 1 else "Summer 2026"
    success = list_cohort_data(cohort_name)
    sys.exit(0 if success else 1)
