#!/usr/bin/env python3
"""
Investigate remaining partial data issues after cache refresh
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_partial_data():
    """Investigate why we still have partial data"""
    print("="*80)
    print("INVESTIGATING REMAINING PARTIAL DATA")
    print("Why 8 interns still have partial data after cache refresh")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        import pandas as pd
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Load Excel data with proper header handling
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)  # Skip first 2 rows, use third as header
        
        print(f"Excel columns found: {list(df.columns[:15])}")  # Show first 15 columns
        
        # Use the correct column names
        name_col = 'Name'
        restaurant_col = 'Restaurant'
        
        print(f"Using columns: Name='{name_col}', Restaurant='{restaurant_col}'")
        
        print(f"Excel interns: {len(df)}")
        print(f"Database interns: {Intern.query.filter_by(is_seeking_internship=True).count()}")
        print(f"Database restaurants: {Restaurant.query.filter_by(is_active=True).count()}")
        
        print(f"\n" + "="*60)
        print("PARTIAL DATA ANALYSIS")
        print("="*60)
        
        partial_data_interns = []
        
        # Check each Excel intern
        for idx, row in df.iterrows():
            excel_name = str(row[name_col]).strip()
            actual_restaurant = str(row[restaurant_col]).strip()
            
            if pd.isna(actual_restaurant) or actual_restaurant == 'nan' or actual_restaurant == '':
                continue
            
            # Find matching intern in database
            db_intern = None
            for intern in Intern.query.filter_by(is_seeking_internship=True).all():
                if excel_name in intern.user.full_name or intern.user.full_name in excel_name:
                    db_intern = intern
                    break
            
            if not db_intern:
                print(f"X {excel_name}: Not found in database")
                continue
            
            # Find actual restaurant in database
            actual_restaurant_db = Restaurant.query.filter_by(name=actual_restaurant).first()
            
            # Check if we can calculate actual commute
            actual_commute = None
            if actual_restaurant_db:
                try:
                    actual_commute = optimizer.get_optimal_commute(
                        db_intern.get_full_address(),
                        actual_restaurant_db.get_full_address(),
                        'driving'
                    )
                except Exception as e:
                    print(f"X {excel_name} -> {actual_restaurant}: Commute error - {e}")
            
            # Check algorithm assignment
            algorithm_assignment = None
            algorithm_commute = None
            
            # Try to find algorithm assignment from latest analysis
            try:
                # Load latest analysis file
                analysis_df = pd.read_csv('ultimate_complete_analysis_final.csv')
                # Look for this intern in the analysis
                intern_rows = analysis_df[analysis_df.iloc[:, 0].str.contains(excel_name, na=False)]
                if not intern_rows.empty:
                    algorithm_assignment = str(intern_rows.iloc[0].get('Algorithm Restaurant', '')).strip()
                    if algorithm_assignment and algorithm_assignment != 'nan':
                        algorithm_restaurant_db = Restaurant.query.filter_by(name=algorithm_assignment).first()
                        if algorithm_restaurant_db:
                            algorithm_commute = optimizer.get_optimal_commute(
                                db_intern.get_full_address(),
                                algorithm_restaurant_db.get_full_address(),
                                'driving'
                            )
            except Exception as e:
                print(f"X {excel_name}: Algorithm analysis error - {e}")
            
            # Determine data status
            has_actual = actual_commute is not None
            has_algorithm = algorithm_commute is not None
            
            if has_actual and has_algorithm:
                status = "COMPLETE"
            elif has_actual or has_algorithm:
                status = "PARTIAL"
                partial_data_interns.append({
                    'name': excel_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_restaurant': algorithm_assignment,
                    'actual_commute': actual_commute,
                    'algorithm_commute': algorithm_commute,
                    'has_actual': has_actual,
                    'has_algorithm': has_algorithm,
                    'actual_restaurant_found': actual_restaurant_db is not None,
                    'algorithm_restaurant_found': algorithm_assignment and Restaurant.query.filter_by(name=algorithm_assignment).first() is not None
                })
            else:
                status = "❌ NO DATA"
            
            print(f"{status} {excel_name}:")
            print(f"  Actual: {actual_restaurant} -> {actual_commute} min")
            print(f"  Algorithm: {algorithm_assignment} -> {algorithm_commute} min")
            print(f"  Actual restaurant in DB: {actual_restaurant_db is not None}")
            print(f"  Algorithm restaurant in DB: {algorithm_assignment and Restaurant.query.filter_by(name=algorithm_assignment).first() is not None}")
            print()
        
        print(f"\n" + "="*60)
        print("PARTIAL DATA BREAKDOWN")
        print("="*60)
        
        print(f"Total partial data interns: {len(partial_data_interns)}")
        
        # Categorize partial data issues
        missing_actual_restaurant = [p for p in partial_data_interns if not p['actual_restaurant_found']]
        missing_algorithm_restaurant = [p for p in partial_data_interns if not p['algorithm_restaurant_found']]
        missing_actual_commute = [p for p in partial_data_interns if not p['has_actual'] and p['actual_restaurant_found']]
        missing_algorithm_commute = [p for p in partial_data_interns if not p['has_algorithm'] and p['algorithm_restaurant_found']]
        
        print(f"Missing actual restaurant in DB: {len(missing_actual_restaurant)}")
        for p in missing_actual_restaurant:
            print(f"  - {p['name']}: {p['actual_restaurant']}")
        
        print(f"\nMissing algorithm restaurant in DB: {len(missing_algorithm_restaurant)}")
        for p in missing_algorithm_restaurant:
            print(f"  - {p['name']}: {p['algorithm_restaurant']}")
        
        print(f"\nMissing actual commute (restaurant exists): {len(missing_actual_commute)}")
        for p in missing_actual_commute:
            print(f"  - {p['name']}: {p['actual_restaurant']}")
        
        print(f"\nMissing algorithm commute (restaurant exists): {len(missing_algorithm_commute)}")
        for p in missing_algorithm_commute:
            print(f"  - {p['name']}: {p['algorithm_restaurant']}")
        
        return partial_data_interns
        
    except Exception as e:
        print(f"Error investigating partial data: {e}")
        return []

def main():
    """Main function"""
    partial_data = investigate_partial_data()
    
    print(f"\n" + "="*80)
    print("PARTIAL DATA INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
