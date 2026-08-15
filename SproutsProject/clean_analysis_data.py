#!/usr/bin/env python3
"""
Clean the analysis data to fix partial data issues
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def clean_analysis_data():
    """Clean the analysis data to fix parsing issues"""
    print("="*80)
    print("CLEANING ANALYSIS DATA")
    print("Fixing CSV parsing issues that cause partial data")
    print("="*80)
    
    try:
        # Load the analysis file properly
        analysis_file = 'ultimate_complete_analysis_final.csv'
        
        # Read the file manually to find the correct data section
        with open(analysis_file, 'r') as f:
            lines = f.readlines()
        
        # Find the line with "Intern Name,Actual Restaurant,Algorithm Restaurant"
        data_start = None
        for i, line in enumerate(lines):
            if 'Intern Name,Actual Restaurant,Algorithm Restaurant' in line:
                data_start = i
                break
        
        if data_start is None:
            print("Could not find data section")
            return
        
        print(f"Found data section at line {data_start}")
        
        # Read from the data section
        df = pd.read_csv(analysis_file, skiprows=data_start, header=0)
        
        print(f"Cleaned data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Remove problematic rows
        print(f"\nOriginal rows: {len(df)}")
        
        # Remove rows where Intern Name is literally "Intern Name"
        df = df[df['Intern Name'] != 'Intern Name']
        
        # Remove rows where Algorithm Restaurant is literally "Algorithm Restaurant"
        df = df[df['Algorithm Restaurant'] != 'Algorithm Restaurant']
        
        # Remove rows with NaN values in critical columns
        df = df.dropna(subset=['Intern Name', 'Actual Restaurant'])
        
        # Replace 'Unassigned' with None for algorithm restaurant
        df['Algorithm Restaurant'] = df['Algorithm Restaurant'].replace('Unassigned', None)
        df['Algorithm Restaurant'] = df['Algorithm Restaurant'].replace('nan', None)
        
        print(f"After cleaning: {len(df)} rows")
        
        # Show the cleaned data
        print(f"\nCleaned intern assignments:")
        for idx, row in df.iterrows():
            intern_name = str(row['Intern Name'])
            actual_rest = str(row['Actual Restaurant'])
            algorithm_rest = str(row['Algorithm Restaurant']) if pd.notna(row['Algorithm Restaurant']) else 'None'
            actual_commute = row['Actual Commute']
            algorithm_commute = row['Algorithm Commute']
            
            print(f"  {intern_name}:")
            print(f"    Actual: {actual_rest} -> {actual_commute} min")
            print(f"    Algorithm: {algorithm_rest} -> {algorithm_commute} min")
        
        # Save the cleaned data
        cleaned_file = 'cleaned_analysis_data.csv'
        df.to_csv(cleaned_file, index=False)
        print(f"\nCleaned data saved to: {cleaned_file}")
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def verify_cleaned_data():
    """Verify the cleaned data works with the investigation"""
    print("="*80)
    print("VERIFYING CLEANED DATA")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        optimizer = TransportationOptimizer()
        
        # Load cleaned data
        df = pd.read_csv('cleaned_analysis_data.csv')
        
        print(f"Cleaned data: {len(df)} interns")
        
        complete_data = 0
        partial_data = 0
        no_data = 0
        
        for idx, row in df.iterrows():
            intern_name = str(row['Intern Name'])
            actual_restaurant = str(row['Actual Restaurant'])
            algorithm_restaurant = str(row['Algorithm Restaurant']) if pd.notna(row['Algorithm Restaurant']) else None
            
            # Find intern in database
            db_intern = None
            for intern in Intern.query.filter_by(is_seeking_internship=True).all():
                if intern_name in intern.user.full_name or intern.user.full_name in intern_name:
                    db_intern = intern
                    break
            
            if not db_intern:
                continue
            
            # Check actual restaurant
            actual_commute = None
            actual_restaurant_db = Restaurant.query.filter_by(name=actual_restaurant).first()
            if actual_restaurant_db:
                try:
                    actual_commute = optimizer.get_optimal_commute(
                        db_intern.get_full_address(),
                        actual_restaurant_db.get_full_address(),
                        'driving'
                    )
                except:
                    pass
            
            # Check algorithm restaurant
            algorithm_commute = None
            if algorithm_restaurant:
                algorithm_restaurant_db = Restaurant.query.filter_by(name=algorithm_restaurant).first()
                if algorithm_restaurant_db:
                    try:
                        algorithm_commute = optimizer.get_optimal_commute(
                            db_intern.get_full_address(),
                            algorithm_restaurant_db.get_full_address(),
                            'driving'
                        )
                    except:
                        pass
            
            # Count data status
            has_actual = actual_commute is not None
            has_algorithm = algorithm_commute is not None
            
            if has_actual and has_algorithm:
                complete_data += 1
            elif has_actual or has_algorithm:
                partial_data += 1
            else:
                no_data += 1
        
        print(f"\nData status after cleaning:")
        print(f"  Complete data: {complete_data}")
        print(f"  Partial data: {partial_data}")
        print(f"  No data: {no_data}")
        print(f"  Coverage rate: {(complete_data + partial_data) / len(df) * 100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    df = clean_analysis_data()
    
    if df is not None:
        print(f"\n" + "="*80)
        verify_cleaned_data()

if __name__ == "__main__":
    main()
