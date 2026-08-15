#!/usr/bin/env python3
"""
Create correct Fall 2025 only analysis
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fall_2025_correct_analysis():
    """Create correct Fall 2025 only analysis"""
    print("="*80)
    print("FALL 2025 CORRECT ANALYSIS")
    print("Only the 10 actual Fall 2025 interns")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Load Intern Availability sheet
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_intern_avail = pd.read_excel(excel_file, sheet_name='Intern Availability')
        
        # Filter to Fall 2025 interns
        month_col = 'For what months are you available during the times selected above? (for example: June 1-August 25)'
        fall_keywords = ['september', 'october', 'november', 'december']
        
        fall_mask = df_intern_avail[month_col].astype(str).str.contains('|'.join(fall_keywords), case=False, na=False)
        df_fall_2025 = df_intern_avail[fall_mask]
        
        print(f"Found {len(df_fall_2025)} Fall 2025 interns")
        
        # Get current algorithm results
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        matching_service = HungarianMatchingService()
        result = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            max_commute_minutes=90,
            restaurant_capacity=2
        )
        
        assignments = result.get('assignments', [])
        assigned_interns = set()
        for assignment in assignments:
            assigned_interns.add(assignment.get('intern_name', ''))
        
        print(f"Current algorithm assignments: {len(assignments)} interns")
        
        print(f"\n1. FALL 2025 INTERNS DETAILS")
        print("-" * 40)
        
        for idx, row in df_fall_2025.iterrows():
            name = f"{row['First Name']} {row['Last Name']}"
            months = row[month_col]
            restaurant = row['Restaurants']
            email = row.get('Email Address', '')
            
            print(f"\n{name}:")
            print(f"  Months: {months}")
            print(f"  Email: {email}")
            if pd.notna(restaurant) and str(restaurant) != 'nan':
                print(f"  Restaurant: {restaurant}")
            else:
                print(f"  Restaurant: None")
        
        print(f"\n2. CREATING FALL 2025 ANALYSIS")
        print("-" * 40)
        
        analysis_data = []
        
        # Process each Fall 2025 intern
        for idx, row in df_fall_2025.iterrows():
            fall_name = f"{row['First Name']} {row['Last Name']}"
            months = row[month_col]
            actual_restaurant = row['Restaurants']
            email = row.get('Email Address', '')
            
            # Check if they have algorithm assignment
            has_algorithm = False
            algorithm_restaurant = None
            algorithm_commute = 0
            
            for assignment in assignments:
                if fall_name in assignment.get('intern_name', '') or assignment.get('intern_name', '') in fall_name:
                    has_algorithm = True
                    algorithm_restaurant = assignment.get('restaurant_name')
                    algorithm_commute = assignment.get('commute_minutes', 0)
                    break
            
            # Calculate actual commute if they have actual restaurant
            actual_commute = 0
            if pd.notna(actual_restaurant) and str(actual_restaurant) != 'nan':
                try:
                    optimizer = TransportationOptimizer()
                    intern = next((i for i in interns if fall_name in i.user.full_name or i.user.full_name in fall_name), None)
                    if intern:
                        # Parse restaurant name from complex string
                        actual_restaurant_clean = str(actual_restaurant).strip()
                        if '\n' in actual_restaurant_clean:
                            actual_restaurant_clean = actual_restaurant_clean.split('\n')[0].strip()
                        
                        actual_rest_db = next((r for r in restaurants if actual_restaurant_clean in r.name or r.name in actual_restaurant_clean), None)
                        if actual_rest_db:
                            actual_commute = optimizer.get_optimal_commute(
                                intern.get_full_address(),
                                actual_rest_db.get_full_address(),
                                intern.transportation_method or 'driving'
                            )
                except:
                    pass
            
            # Determine status
            if has_algorithm:
                if pd.notna(actual_restaurant) and str(actual_restaurant) != 'nan':
                    if actual_commute and algorithm_commute:
                        delta = actual_commute - algorithm_commute
                        delta_pct = (delta / actual_commute * 100) if actual_commute > 0 else 0
                        
                        if delta > 0:
                            status = "Algorithm Better"
                        elif delta < 0:
                            status = "Actual Better"
                        else:
                            status = "Same"
                    else:
                        status = "Algorithm Only"
                        delta = 0
                        delta_pct = 0
                else:
                    status = "Algorithm Only"
                    delta = 0
                    delta_pct = 0
            else:
                if pd.notna(actual_restaurant) and str(actual_restaurant) != 'nan':
                    status = "Actual Only"
                else:
                    status = "No Assignment"
                delta = 0
                delta_pct = 0
            
            # Clean restaurant names
            actual_rest_clean = 'None'
            if pd.notna(actual_restaurant) and str(actual_restaurant) != 'nan':
                actual_rest_clean = str(actual_restaurant).strip()
                if '\n' in actual_rest_clean:
                    actual_rest_clean = actual_rest_clean.split('\n')[0].strip()
            
            analysis_data.append({
                'Intern Name': fall_name,
                'Actual Restaurant': actual_rest_clean,
                'Algorithm Restaurant': algorithm_restaurant if has_algorithm else 'None',
                'Actual Commute': actual_commute,
                'Algorithm Commute': algorithm_commute if has_algorithm else 0,
                'Delta (min)': delta,
                'Delta %': delta_pct,
                'Status': status,
                'Months Available': months,
                'Email': email
            })
        
        print(f"Processed {len(analysis_data)} Fall 2025 interns")
        
        print(f"\n3. FALL 2025 RESULTS SUMMARY")
        print("-" * 40)
        
        # Create summary
        total_fall_2025 = len(analysis_data)
        algorithm_assigned = len([d for d in analysis_data if d['Algorithm Restaurant'] != 'None'])
        actual_only = len([d for d in analysis_data if d['Status'] == 'Actual Only'])
        both_assigned = len([d for d in analysis_data if d['Status'] in ['Same', 'Actual Better', 'Algorithm Better']])
        algorithm_only = len([d for d in analysis_data if d['Status'] == 'Algorithm Only'])
        no_assignment = len([d for d in analysis_data if d['Status'] == 'No Assignment'])
        
        print(f"Fall 2025 interns: {total_fall_2025}")
        print(f"Algorithm assigned: {algorithm_assigned}")
        print(f"Actual assignments only: {actual_only}")
        print(f"Both actual and algorithm: {both_assigned}")
        print(f"Algorithm only: {algorithm_only}")
        print(f"No assignment: {no_assignment}")
        print(f"Coverage rate: {algorithm_assigned / total_fall_2025 * 100:.1f}%")
        
        print(f"\nDetailed breakdown:")
        for data in analysis_data:
            print(f"  {data['Intern Name']}:")
            print(f"    Status: {data['Status']}")
            print(f"    Actual: {data['Actual Restaurant']}")
            print(f"    Algorithm: {data['Algorithm Restaurant']}")
            if data['Actual Commute'] > 0:
                print(f"    Actual commute: {data['Actual Commute']} min")
            if data['Algorithm Commute'] > 0:
                print(f"    Algorithm commute: {data['Algorithm Commute']} min")
        
        print(f"\n4. SAVING FALL 2025 ANALYSIS")
        print("-" * 40)
        
        # Create DataFrame and save
        df_analysis = pd.DataFrame(analysis_data)
        df_analysis.to_csv('fall_2025_final_analysis.csv', index=False)
        print(f"Saved Fall 2025 analysis to 'fall_2025_final_analysis.csv'")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Creating correct Fall 2025 analysis...")
    
    success = fall_2025_correct_analysis()
    
    print(f"\n" + "="*80)
    print("FALL 2025 CORRECT ANALYSIS COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: Fall 2025 analysis complete")
        print("Check 'fall_2025_final_analysis.csv' for results")

if __name__ == "__main__":
    main()
