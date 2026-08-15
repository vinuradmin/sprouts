#!/usr/bin/env python3
"""
Update analysis using Intern Availability sheet restaurant data
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def update_analysis_with_intern_sheet():
    """Update analysis using Intern Availability sheet restaurant data"""
    print("="*80)
    print("UPDATING ANALYSIS WITH INTERN AVAILABILITY SHEET")
    print("Using Restaurants column from Intern Availability instead of Active Intern List")
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
        
        print(f"\n1. CHECKING RESTAURANT DATA IN INTERN AVAILABILITY SHEET")
        print("-" * 40)
        
        # Check how many have actual restaurant data in Intern Availability
        non_nan_restaurants = df_intern_avail[df_intern_avail['Restaurants'].notna()]
        print(f"Interns with restaurant data in Intern Availability: {len(non_nan_restaurants)}")
        
        print(f"\nSample restaurant data from Intern Availability:")
        for idx, row in non_nan_restaurants.head(5).iterrows():
            name = f"{row['First Name']} {row['Last Name']}"
            restaurant = row['Restaurants']
            print(f"  {name}: {restaurant}")
        
        print(f"\n2. CREATING UPDATED ANALYSIS")
        print("-" * 40)
        
        # Create comprehensive analysis using Intern Availability for actual assignments
        analysis_data = []
        
        # Process assigned interns first
        for assignment in assignments:
            intern_name = assignment.get('intern_name', '')
            algorithm_restaurant = assignment.get('restaurant_name', '')
            algorithm_commute = assignment.get('commute_minutes', 0)
            
            # Find actual assignment from Intern Availability sheet
            actual_restaurant = 'None'
            actual_commute = 0
            
            # Try to find in Intern Availability sheet first
            intern_match = df_intern_avail[df_intern_avail['First Name'].str.contains(intern_name.split()[0], na=False, case=False)]
            if not intern_match.empty:
                avail_restaurant = intern_match.iloc[0]['Restaurants']
                if pd.notna(avail_restaurant) and str(avail_restaurant) != 'nan':
                    actual_restaurant = str(avail_restaurant).strip()
                    
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
            else:
                # Fallback to Active Intern List
                active_match = df_active[df_active['Name'].str.contains(intern_name.split()[0], na=False, case=False)]
                if not active_match.empty:
                    active_restaurant = str(active_match.iloc[0]['Restaurant']).strip()
                    if active_restaurant and active_restaurant != 'nan':
                        actual_restaurant = active_restaurant
                        
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
                'Data Source': 'Intern Availability' if actual_restaurant != 'None' else 'None'
            })
        
        print(f"Processed {len(analysis_data)} assigned interns")
        
        # Now find interns with actual assignments but no algorithm assignments
        print(f"\n3. FINDING ACTUAL VS ALGORITHM MISMATCHES")
        print("-" * 40)
        
        # Get all interns with actual assignments from Intern Availability
        actual_assignments = []
        
        for idx, row in df_intern_avail.iterrows():
            first_name = str(row['First Name']).strip()
            last_name = str(row['Last Name']).strip()
            intern_name = f"{first_name} {last_name}"
            restaurant = row['Restaurants']
            
            if pd.notna(restaurant) and str(restaurant) != 'nan':
                actual_assignments.append({
                    'name': intern_name,
                    'restaurant': str(restaurant).strip(),
                    'email': row.get('Email Address', '')
                })
        
        print(f"Found {len(actual_assignments)} interns with actual assignments in Intern Availability")
        
        # Check which of these don't have algorithm assignments
        mismatches = []
        for actual in actual_assignments:
            has_algorithm = any(actual['name'] in assigned_name for assigned_name in assigned_interns)
            if not has_algorithm:
                mismatches.append(actual)
        
        print(f"Found {len(mismatches)} interns with actual but no algorithm assignments")
        
        # Add mismatches to analysis
        for mismatch in mismatches:
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
                'Data Source': 'Intern Availability'
            })
        
        print(f"Added {len(mismatches)} mismatch cases to analysis")
        
        print(f"\n4. SAVING UPDATED ANALYSIS")
        print("-" * 40)
        
        # Create DataFrame and save
        df_analysis = pd.DataFrame(analysis_data)
        df_analysis.to_csv('updated_analysis_using_intern_sheet.csv', index=False)
        print(f"Saved updated analysis to 'updated_analysis_using_intern_sheet.csv'")
        
        # Create summary
        print(f"\n5. SUMMARY")
        print("-" * 40)
        
        total_interns = len(df_analysis)
        algorithm_assigned = len(df_analysis[df_analysis['Algorithm Restaurant'] != 'None'])
        actual_only = len(df_analysis[df_analysis['Status'] == 'Actual Only'])
        intern_source_data = len(df_analysis[df_analysis['Data Source'] == 'Intern Availability'])
        
        print(f"Total interns in analysis: {total_interns}")
        print(f"Algorithm assigned: {algorithm_assigned}")
        print(f"Actual assignments only: {actual_only}")
        print(f"Data from Intern Availability sheet: {intern_source_data}")
        print(f"Coverage rate: {algorithm_assigned / total_interns * 100:.1f}%")
        
        print(f"\nComparison with previous analysis:")
        print(f"Previous mismatches: 6")
        print(f"New mismatches: {actual_only}")
        print(f"Change: {actual_only - 6}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Updating analysis using Intern Availability sheet restaurant data...")
    
    success = update_analysis_with_intern_sheet()
    
    print(f"\n" + "="*80)
    print("UPDATED ANALYSIS COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: Analysis updated using Intern Availability sheet")
        print("Check 'updated_analysis_using_intern_sheet.csv' for results")

if __name__ == "__main__":
    main()
