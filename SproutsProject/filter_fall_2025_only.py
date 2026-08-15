#!/usr/bin/env python3
"""
Filter analysis to only include Fall 2025 interns
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def filter_fall_2025_only():
    """Filter analysis to only Fall 2025 interns"""
    print("="*80)
    print("FILTERING TO FALL 2025 INTERNS ONLY")
    print("Removing interns from other cohorts")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Load both sheets
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_active = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        df_intern_avail = pd.read_excel(excel_file, sheet_name='Intern Availability')
        
        print(f"Active Intern List: {len(df_active)} rows")
        print(f"Intern Availability: {len(df_intern_avail)} rows")
        
        # Filter to Fall 2025 interns
        print(f"\n1. FILTERING TO FALL 2025 INTERNS")
        print("-" * 40)
        
        # Check for Fall 2025 indicators in Intern Availability
        fall_2025_keywords = ['fall 2025', 'Fall 2025', 'September', 'October', 'November', 'December']
        
        # Look for month/season columns
        month_columns = [col for col in df_intern_avail.columns if any(keyword.lower() in col.lower() for keyword in ['month', 'season', 'september', 'october', 'november', 'december'])]
        print(f"Month/season columns in Intern Availability: {month_columns}")
        
        # Filter Fall 2025 interns
        fall_2025_interns = []
        
        if month_columns:
            # Use month/season column to filter
            month_col = month_columns[0]
            fall_2025_mask = df_intern_avail[month_col].astype(str).str.contains('fall', case=False, na=False)
            df_fall_2025 = df_intern_avail[fall_2025_mask]
            print(f"Found {len(df_fall_2025)} Fall 2025 interns using month filter")
        else:
            # If no month column, assume all are Fall 2025 for now
            df_fall_2025 = df_intern_avail
            print(f"No month column found, assuming all {len(df_fall_2025)} are Fall 2025")
        
        # Show sample Fall 2025 interns
        print(f"\nSample Fall 2025 interns:")
        for idx, row in df_fall_2025.head(5).iterrows():
            name = f"{row['First Name']} {row['Last Name']}"
            restaurant = row['Restaurants']
            print(f"  {name}: {restaurant}")
        
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
        
        print(f"\n2. CREATING FALL 2025 ONLY ANALYSIS")
        print("-" * 40)
        
        # Create analysis for Fall 2025 interns only
        analysis_data = []
        
        # Process assigned interns first
        for assignment in assignments:
            intern_name = assignment.get('intern_name', '')
            algorithm_restaurant = assignment.get('restaurant_name', '')
            algorithm_commute = assignment.get('commute_minutes', 0)
            
            # Check if this intern is in Fall 2025 data
            intern_in_fall_2025 = False
            actual_restaurant = 'None'
            actual_commute = 0
            
            for idx, row in df_fall_2025.iterrows():
                fall_name = f"{row['First Name']} {row['Last Name']}"
                if intern_name in fall_name or fall_name in intern_name:
                    intern_in_fall_2025 = True
                    restaurant = row['Restaurants']
                    if pd.notna(restaurant) and str(restaurant) != 'nan':
                        actual_restaurant = str(restaurant).strip()
                        
                        # Calculate actual commute
                        try:
                            optimizer = TransportationOptimizer()
                            intern = next((i for i in interns if intern_name in i.user.full_name), None)
                            if intern:
                                actual_rest_db = next((r for r in restaurants if actual_restaurant in r.name or r.name in actual_restaurant), None)
                                if actual_rest_db:
                                    actual_commute = optimizer.get_optimal_commute(
                                        intern.get_full_address(),
                                        actual_rest_db.get_full_address(),
                                        intern.transportation_method or 'driving'
                                    )
                        except:
                            pass
                    break
            
            if intern_in_fall_2025:
                # Calculate delta
                if actual_commute and algorithm_commute:
                    delta = actual_commute - algorithm_commute
                    delta_pct = (delta / actual_commute * 100) if actual_commute > 0 else 0
                else:
                    delta = 0
                    delta_pct = 0
                
                # Determine status
                if actual_restaurant != 'None' and algorithm_restaurant:
                    if delta > 0:
                        status = "Algorithm Better"
                    elif delta < 0:
                        status = "Actual Better"
                    else:
                        status = "Same"
                elif algorithm_restaurant:
                    status = "Algorithm Only"
                else:
                    status = "No Assignment"
                
                analysis_data.append({
                    'Intern Name': intern_name,
                    'Actual Restaurant': actual_restaurant,
                    'Algorithm Restaurant': algorithm_restaurant,
                    'Actual Commute': actual_commute,
                    'Algorithm Commute': algorithm_commute,
                    'Delta (min)': delta,
                    'Delta %': delta_pct,
                    'Status': status,
                    'Cohort': 'Fall 2025'
                })
        
        print(f"Processed {len(analysis_data)} assigned Fall 2025 interns")
        
        # Now find Fall 2025 interns with actual assignments but no algorithm assignments
        print(f"\n3. FINDING FALL 2025 ACTUAL VS ALGORITHM MISMATCHES")
        print("-" * 40)
        
        # Get all Fall 2025 interns with actual assignments
        fall_2025_actual_assignments = []
        
        for idx, row in df_fall_2025.iterrows():
            first_name = str(row['First Name']).strip()
            last_name = str(row['Last Name']).strip()
            intern_name = f"{first_name} {last_name}"
            restaurant = row['Restaurants']
            
            if pd.notna(restaurant) and str(restaurant) != 'nan':
                fall_2025_actual_assignments.append({
                    'name': intern_name,
                    'restaurant': str(restaurant).strip(),
                    'email': row.get('Email Address', '')
                })
        
        print(f"Found {len(fall_2025_actual_assignments)} Fall 2025 interns with actual assignments")
        
        # Check which of these don't have algorithm assignments
        fall_2025_mismatches = []
        for actual in fall_2025_actual_assignments:
            has_algorithm = any(actual['name'] in assigned_name for assigned_name in assigned_interns)
            if not has_algorithm:
                fall_2025_mismatches.append(actual)
        
        print(f"Found {len(fall_2025_mismatches)} Fall 2025 interns with actual but no algorithm assignments")
        
        # Add Fall 2025 mismatches to analysis
        for mismatch in fall_2025_mismatches:
            intern_name = mismatch['name']
            actual_restaurant = mismatch['restaurant']
            
            # Calculate actual commute
            actual_commute = 0
            try:
                optimizer = TransportationOptimizer()
                intern = next((i for i in interns if intern_name in i.user.full_name or i.user.full_name in intern_name), None)
                if intern:
                    actual_rest_db = next((r for r in restaurants if actual_restaurant in r.name or r.name in actual_restaurant), None)
                    if actual_rest_db:
                        actual_commute = optimizer.get_optimal_commute(
                            intern.get_full_address(),
                            actual_rest_db.get_full_address(),
                            intern.transportation_method or 'driving'
                        )
            except:
                pass
            
            analysis_data.append({
                'Intern Name': intern_name,
                'Actual Restaurant': actual_restaurant,
                'Algorithm Restaurant': 'None',
                'Actual Commute': actual_commute,
                'Algorithm Commute': 0,
                'Delta (min)': 0,
                'Delta %': 0,
                'Status': 'Actual Only',
                'Cohort': 'Fall 2025'
            })
        
        print(f"Added {len(fall_2025_mismatches)} Fall 2025 mismatch cases to analysis")
        
        print(f"\n4. SAVING FALL 2025 ONLY ANALYSIS")
        print("-" * 40)
        
        # Create DataFrame and save
        df_analysis = pd.DataFrame(analysis_data)
        df_analysis.to_csv('fall_2025_only_analysis.csv', index=False)
        print(f"Saved Fall 2025 only analysis to 'fall_2025_only_analysis.csv'")
        
        # Create summary
        print(f"\n5. FALL 2025 SUMMARY")
        print("-" * 40)
        
        total_fall_2025 = len(df_analysis)
        algorithm_assigned = len(df_analysis[df_analysis['Algorithm Restaurant'] != 'None'])
        actual_only = len(df_analysis[df_analysis['Status'] == 'Actual Only'])
        
        print(f"Fall 2025 interns in analysis: {total_fall_2025}")
        print(f"Algorithm assigned: {algorithm_assigned}")
        print(f"Actual assignments only: {actual_only}")
        print(f"Coverage rate: {algorithm_assigned / total_fall_2025 * 100:.1f}%")
        
        print(f"\nComparison:")
        print(f"Previous (all interns): 51 mismatches")
        print(f"Fall 2025 only: {actual_only} mismatches")
        print(f"Difference: {actual_only - 51}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Filtering analysis to Fall 2025 interns only...")
    
    success = filter_fall_2025_only()
    
    print(f"\n" + "="*80)
    print("FALL 2025 FILTERING COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: Analysis filtered to Fall 2025 interns only")
        print("Check 'fall_2025_only_analysis.csv' for results")

if __name__ == "__main__":
    main()
