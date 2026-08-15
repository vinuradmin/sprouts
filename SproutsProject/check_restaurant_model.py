#!/usr/bin/env python3
"""
Check Restaurant model structure and fix the analysis
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_restaurant_model():
    """Check Restaurant model structure"""
    print("="*80)
    print("CHECKING RESTAURANT MODEL STRUCTURE")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get all restaurants
        restaurants = Restaurant.query.all()
        
        print(f"Total restaurants in database: {len(restaurants)}")
        
        print(f"\nRestaurant model columns:")
        for column in Restaurant.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
        print(f"\nCurrent restaurants:")
        for i, rest in enumerate(restaurants):
            print(f"{i+1:2d}. {rest.name}")
        
        return restaurants
        
    except Exception as e:
        print(f"Error checking restaurant model: {e}")
        return []

def fix_chef_availabilities():
    """Fix Chef Availabilities parsing"""
    print("="*80)
    print("FIXING CHEF AVAILABILITIES PARSING")
    print("="*80)
    
    try:
        import pandas as pd
        
        # Load Chef Availabilities with correct column parsing
        chef_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv')
        
        print(f"Chef Availabilities shape: {chef_df.shape}")
        print(f"Columns: {list(chef_df.columns)}")
        
        # Show first few rows of restaurant names
        print(f"\nFirst 10 restaurant names:")
        for idx, row in chef_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            if idx <= 10:  # Show first 10 data rows
                restaurant_name = str(row.iloc[3]).strip()  # Column 3 is Restaurant Name
                print(f"{idx:2d}. '{restaurant_name}'")
            else:
                break
        
        # Extract unique restaurant names
        restaurant_names = set()
        for idx, row in chef_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            restaurant_name = str(row.iloc[3]).strip()
            if restaurant_name and restaurant_name != 'nan' and restaurant_name != '':
                restaurant_names.add(restaurant_name)
        
        print(f"\nUnique restaurant names in Chef Availabilities: {len(restaurant_names)}")
        for name in sorted(restaurant_names):
            print(f"  - {name}")
        
        return restaurant_names
        
    except Exception as e:
        print(f"Error fixing Chef Availabilities: {e}")
        return set()

def main():
    """Main function"""
    restaurants = check_restaurant_model()
    chef_restaurants = fix_chef_availabilities()
    
    print(f"\n" + "="*80)
    print("RESTAURANT ANALYSIS COMPLETE")
    print("="*80)
    print(f"Database restaurants: {len(restaurants)}")
    print(f"Chef Availabilities restaurants: {len(chef_restaurants)}")

if __name__ == "__main__":
    main()
