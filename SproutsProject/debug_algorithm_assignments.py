#!/usr/bin/env python3
"""
Debug algorithm assignments - why restaurant names not found in database
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_algorithm_assignments():
    """Debug why algorithm restaurant names aren't found in database"""
    print("="*80)
    print("DEBUGGING ALGORITHM ASSIGNMENTS")
    print("Why restaurant names not found in database")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Load latest analysis file with proper header handling
        analysis_df = pd.read_csv('ultimate_complete_analysis_final.csv', header=23)  # Skip to data section
        
        print(f"Analysis file shape: {analysis_df.shape}")
        print(f"Columns: {list(analysis_df.columns)}")
        
        # Find the algorithm restaurant column
        algorithm_col = 'Algorithm Restaurant'
        if algorithm_col not in analysis_df.columns:
            print(f"Algorithm restaurant column not found. Available columns: {list(analysis_df.columns)}")
            return set()
        
        # Get unique algorithm restaurant names
        unique_algorithm_restaurants = analysis_df[algorithm_col].dropna().unique()
        print(f"\nUnique algorithm restaurants: {len(unique_algorithm_restaurants)}")
        
        for rest in unique_algorithm_restaurants:
            print(f"  - '{rest}'")
        
        # Get all database restaurants
        db_restaurants = Restaurant.query.filter_by(is_active=True).all()
        db_restaurant_names = {r.name for r in db_restaurants}
        
        print(f"\nDatabase restaurants: {len(db_restaurant_names)}")
        for name in sorted(db_restaurant_names):
            print(f"  - {name}")
        
        # Find algorithm restaurants not in database
        algorithm_restaurants = set(unique_algorithm_restaurants)
        missing_restaurants = algorithm_restaurants - db_restaurant_names
            
            print(f"\nAlgorithm restaurants NOT in database: {len(missing_restaurants)}")
            for rest in missing_restaurants:
                print(f"  - {rest}")
                
                # Find similar names in database
                similar = [db_name for db_name in db_restaurant_names 
                          if rest.lower() in db_name.lower() or db_name.lower() in rest.lower()]
                if similar:
                    print(f"    Similar in DB: {similar}")
        
        # Check specific problematic cases
        print(f"\n" + "="*60)
        print("CHECKING SPECIFIC CASES")
        print("="*60)
        
        if algorithm_col:
            # Get intern names with missing algorithm restaurants
            missing_cases = analysis_df[analysis_df[algorithm_col].isin(missing_restaurants)]
            
            print(f"Interns with missing algorithm restaurants: {len(missing_cases)}")
            
            for idx, row in missing_cases.iterrows():
                intern_name = str(row.iloc[0]) if len(row) > 0 else "Unknown"
                algorithm_rest = str(row[algorithm_col])
                
                print(f"\n{intern_name}:")
                print(f"  Algorithm restaurant: '{algorithm_rest}'")
                
                # Try to find this intern in the analysis
                intern_rows = analysis_df[analysis_df.iloc[:, 0].str.contains(intern_name, na=False, case=False)]
                if not intern_rows.empty:
                    actual_rest = str(intern_rows.iloc[0].get('Actual Restaurant', '')).strip()
                    print(f"  Actual restaurant: '{actual_rest}'")
        
        return missing_restaurants
        
    except Exception as e:
        print(f"Error: {e}")
        return set()

def main():
    """Main function"""
    missing = debug_algorithm_assignments()
    
    print(f"\n" + "="*80)
    print("ALGORITHM ASSIGNMENTS DEBUG COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
