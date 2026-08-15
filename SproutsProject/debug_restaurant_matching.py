#!/usr/bin/env python3
"""
Debug why we have partial data despite finding all restaurants
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_restaurant_matching():
    """Debug restaurant matching issues"""
    print("="*80)
    print("DEBUGGING RESTAURANT MATCHING ISSUES")
    print("Why partial data despite finding all restaurants?")
    print("="*80)
    
    try:
        # Load actual data from Excel
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Load Chef Availabilities
        chef_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv')
        
        # Get database restaurants
        from app import create_app
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        db_restaurants = Restaurant.query.filter_by(is_active=True).all()
        db_restaurant_names = {rest.name for rest in db_restaurants}
        
        # Extract actual restaurants from Excel
        actual_restaurants = set()
        for idx, row in fall_2025_df.iterrows():
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(restaurant_col):
                restaurant_name = str(restaurant_col).strip()
                if restaurant_name and restaurant_name != 'nan' and restaurant_name != 'Unassigned':
                    actual_restaurants.add(restaurant_name)
        
        # Extract restaurants from Chef Availabilities
        chef_restaurants = set()
        for idx, row in chef_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            restaurant_name = str(row.iloc[3]).strip()  # Column 3 is Restaurant Name
            if restaurant_name and restaurant_name != 'nan':
                chef_restaurants.add(restaurant_name)
        
        print(f"RESTAURANT COMPARISON:")
        print(f"Excel actual restaurants: {len(actual_restaurants)}")
        print(f"Chef Availabilities restaurants: {len(chef_restaurants)}")
        print(f"Database restaurants: {len(db_restaurant_names)}")
        
        print(f"\nEXCEL ACTUAL RESTAURANTS:")
        for rest in sorted(actual_restaurants):
            print(f"  - {rest}")
        
        print(f"\nCHEF AVAILABILITIES RESTAURANTS:")
        for rest in sorted(chef_restaurants):
            print(f"  - {rest}")
        
        print(f"\nDATABASE RESTAURANTS:")
        for rest in sorted(db_restaurant_names):
            print(f"  - {rest}")
        
        # Find matching issues
        excel_in_db = actual_restaurants & db_restaurant_names
        excel_not_in_db = actual_restaurants - db_restaurant_names
        chef_in_db = chef_restaurants & db_restaurant_names
        chef_not_in_db = chef_restaurants - db_restaurant_names
        
        print(f"\nMATCHING ANALYSIS:")
        print(f"Excel restaurants in database: {len(excel_in_db)}")
        print(f"Excel restaurants NOT in database: {len(excel_not_in_db)}")
        print(f"Chef restaurants in database: {len(chef_in_db)}")
        print(f"Chef restaurants NOT in database: {len(chef_not_in_db)}")
        
        if excel_not_in_db:
            print(f"\nEXCEL RESTAURANTS NOT IN DATABASE:")
            for rest in sorted(excel_not_in_db):
                print(f"  MISSING: {rest}")
        
        if chef_not_in_db:
            print(f"\nCHEF RESTAURANTS NOT IN DATABASE:")
            for rest in sorted(chef_not_in_db):
                print(f"  MISSING: {rest}")
        
        # Test specific matching
        print(f"\n" + "="*60)
        print("TESTING RESTAURANT MATCHING LOGIC")
        print("="*60)
        
        def find_restaurant(restaurant_name):
            """Test the restaurant matching logic"""
            restaurant_name = restaurant_name.strip().lower()
            
            for rest_name in db_restaurant_names:
                rest_lower = rest_name.lower()
                
                # Exact match
                if restaurant_name == rest_lower:
                    return rest_name, "Exact match"
                
                # Partial match
                if restaurant_name in rest_lower or rest_lower in restaurant_name:
                    return rest_name, "Partial match"
                
                # Remove common words and match
                clean_actual = restaurant_name.replace('restaurant', '').replace('kitchen', '').strip()
                clean_rest = rest_lower.replace('restaurant', '').replace('kitchen', '').strip()
                
                if clean_actual in clean_rest or clean_rest in clean_actual:
                    return rest_name, "Cleaned match"
            
            return None, "No match"
        
        print(f"Testing Excel restaurant matching:")
        for rest in sorted(actual_restaurants):
            match, method = find_restaurant(rest)
            if match:
                print(f"  {rest} -> {match} ({method})")
            else:
                print(f"  {rest} -> NO MATCH")
        
        # Show specific problematic cases
        print(f"\nPROBLEMATIC CASES ANALYSIS:")
        problematic_restaurants = ['Stanford', 'UC Berkeley', 'Nopa Fish', 'Hahdough bakery']
        
        for rest in problematic_restaurants:
            if rest in actual_restaurants:
                match, method = find_restaurant(rest)
                print(f"\n{rest}:")
                print(f"  Match: {match}")
                print(f"  Method: {method}")
                
                # Show similar database restaurants
                print(f"  Similar database restaurants:")
                for db_rest in sorted(db_restaurant_names):
                    if rest.lower() in db_rest.lower() or db_rest.lower() in rest.lower():
                        print(f"    - {db_rest}")
        
        return actual_restaurants, chef_restaurants, db_restaurant_names
        
    except Exception as e:
        print(f"Error debugging restaurant matching: {e}")
        return set(), set(), set()

def main():
    """Main function"""
    actual, chef, db = debug_restaurant_matching()
    
    print(f"\n" + "="*80)
    print("RESTAURANT MATCHING DEBUG COMPLETE")
    print("="*80)
    print(f"Excel: {len(actual)}, Chef: {len(chef)}, Database: {len(db)}")

if __name__ == "__main__":
    main()
