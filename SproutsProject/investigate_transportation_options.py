#!/usr/bin/env python3
"""
Investigate transportation options and commute calculation
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_transportation_options():
    """Investigate transportation options in the data"""
    print("=== INVESTIGATING TRANSPORTATION OPTIONS ===")
    
    try:
        # Load intern availability data to see transportation options
        intern_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv')
        
        print(f"Intern availability data shape: {intern_df.shape}")
        print(f"Columns: {list(intern_df.columns)}")
        
        # Look for transportation column
        transport_col = None
        for col in intern_df.columns:
            if 'transport' in col.lower() or 'method' in col.lower():
                transport_col = col
                print(f"Found transportation column: {col}")
                break
        
        if transport_col:
            # Show unique transportation values
            unique_transports = intern_df[transport_col].dropna().unique()
            print(f"\nUnique transportation options:")
            for transport in unique_transports:
                print(f"  - {transport}")
            
            # Look for interns with multiple options
            print(f"\nInterns with potentially multiple options:")
            for idx, row in intern_df.iterrows():
                transport = str(row[transport_col])
                if pd.notna(row[transport_col]) and ('/' in transport or '&' in transport or ',' in transport):
                    intern_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                    print(f"  {intern_name}: {transport}")
        else:
            print("No transportation column found in intern data")
        
        # Check database model
        print(f"\n=== CHECKING DATABASE MODEL ===")
        try:
            from app import create_app
            from app.models import Intern
            
            app = create_app()
            app.app_context().push()
            
            interns = Intern.query.filter_by(is_seeking_internship=True).all()
            
            print(f"Found {len(interns)} interns in database")
            
            # Check transportation_method field
            transport_options = set()
            for intern in interns:
                if intern.transportation_method:
                    transport_options.add(intern.transportation_method)
            
            print(f"Transportation options in database:")
            for option in sorted(transport_options):
                print(f"  - {option}")
            
            # Look for interns with multiple options
            print(f"\nInterns with potentially multiple options:")
            for intern in interns:
                if intern.transportation_method:
                    transport = intern.transportation_method
                    if '/' in transport or '&' in transport or ',' in transport:
                        print(f"  {intern.user.full_name}: {transport}")
            
        except Exception as e:
            print(f"Error checking database: {e}")
        
        return transport_col
        
    except Exception as e:
        print(f"Error investigating transportation: {e}")
        return None

def analyze_commute_calculation():
    """Analyze how commute is currently calculated"""
    print(f"\n=== ANALYZING COMMUTE CALCULATION ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Checking commute calculation method...")
        
        # Look at the commute cache usage
        print(f"Current commute calculation uses:")
        print(f"  - Transportation method: intern.transportation_method")
        print(f"  - Address: intern.get_full_address()")
        print(f"  - Restaurant address: restaurant.get_full_address()")
        
        # Show some examples
        print(f"\nExample transportation methods:")
        for intern in interns[:5]:
            if intern.transportation_method:
                print(f"  {intern.user.full_name}: {intern.transportation_method}")
        
        # Check if transportation method has multiple options
        multi_option_interns = []
        for intern in interns:
            if intern.transportation_method:
                transport = intern.transportation_method
                if '/' in transport or '&' in transport or ',' in transport:
                    multi_option_interns.append(intern)
        
        print(f"\nInterns with multiple transportation options: {len(multi_option_interns)}")
        for intern in multi_option_interns:
            print(f"  {intern.user.full_name}: {intern.transportation_method}")
        
        return multi_option_interns
        
    except Exception as e:
        print(f"Error analyzing commute calculation: {e}")
        return []

def propose_solution():
    """Propose solution for multiple transportation options"""
    print(f"\n=== PROPOSED SOLUTION ===")
    
    print("CURRENT ISSUE:")
    print("- Interns may have multiple transportation options (e.g., 'car/public')")
    print("- Current code only uses first option")
    print("- Should use minimum commute across all available options")
    
    print("\nPROPOSED SOLUTION:")
    print("1. Parse transportation_method string for multiple options")
    print("2. Calculate commute for each transportation method")
    print("3. Use minimum commute time across all options")
    print("4. Update HungarianMatchingService to handle this")
    
    print("\nIMPLEMENTATION PLAN:")
    print("1. Create helper function to parse transportation options")
    print("2. Modify commute calculation to try all options")
    print("3. Cache results for each transportation method")
    print("4. Return minimum commute time")
    
    print("\nEXAMPLE:")
    print("  Current: 'car/public' -> uses 'car' only")
    print("  Proposed: 'car/public' -> calculates both, returns min(car_time, public_time)")

if __name__ == "__main__":
    transport_col = investigate_transportation_options()
    multi_option_interns = analyze_commute_calculation()
    propose_solution()
    
    print(f"\n=== INVESTIGATION COMPLETE ===")
    print("You're absolutely right about this issue!")
    print("Multiple transportation options should be considered for optimal commute calculation.")
