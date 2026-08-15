#!/usr/bin/env python3
"""
Investigate interns with actual assignments but no algorithm assignments
Focus on the specific cases and why Jesus appears duplicated
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_actual_vs_algorithm():
    """Investigate actual vs algorithm assignment mismatches"""
    print("="*80)
    print("INVESTIGATING ACTUAL VS ALGORITHM ASSIGNMENTS")
    print("Focus on interns with actual assignments but no algorithm assignments")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Load Excel data
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        
        print(f"Excel interns: {len(df)}")
        
        # Load cleaned analysis data
        try:
            analysis_df = pd.read_csv('cleaned_analysis_data.csv')
            print(f"Cleaned analysis interns: {len(analysis_df)}")
        except:
            print("No cleaned analysis data found")
            analysis_df = None
        
        # Get algorithm assignments
        matching_service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        result = matching_service.find_optimal_assignments(interns, restaurants)
        algorithm_assignments = result.get('assignments', [])
        
        print(f"Algorithm assignments: {len(algorithm_assignments)}")
        
        # Create lookup dictionaries
        algorithm_assigned_interns = set()
        for assignment in algorithm_assignments:
            intern_name = assignment.get('intern_name', '')
            if intern_name:
                algorithm_assigned_interns.add(intern_name.strip())
        
        print(f"Algorithm assigned interns: {len(algorithm_assigned_interns)}")
        
        # Find interns with actual assignments but no algorithm assignments
        actual_vs_algorithm_mismatch = []
        
        for idx, row in df.iterrows():
            excel_name = str(row['Name']).strip()
            actual_restaurant = str(row['Restaurant']).strip()
            
            if pd.isna(row['Restaurant']) or actual_restaurant == 'nan':
                continue
            
            # Check if intern is in database and has algorithm assignment
            intern_in_db = False
            has_algorithm_assignment = False
            
            for intern in interns:
                if excel_name in intern.user.full_name or intern.user.full_name in excel_name:
                    intern_in_db = True
                    if intern.user.full_name in algorithm_assigned_interns:
                        has_algorithm_assignment = True
                    break
            
            if intern_in_db and not has_algorithm_assignment:
                actual_vs_algorithm_mismatch.append({
                    'excel_name': excel_name,
                    'actual_restaurant': actual_restaurant,
                    'in_database': intern_in_db,
                    'algorithm_assignment': has_algorithm_assignment
                })
        
        print(f"\n" + "="*60)
        print("INTERNS WITH ACTUAL ASSIGNMENTS BUT NO ALGORITHM ASSIGNMENTS")
        print("="*60)
        
        print(f"Found {len(actual_vs_algorithm_mismatch)} cases:")
        
        for case in actual_vs_algorithm_mismatch:
            print(f"\n{case['excel_name']}:")
            print(f"  Actual assignment: {case['actual_restaurant']}")
            print(f"  In database: {case['in_database']}")
            print(f"  Algorithm assignment: {case['algorithm_assignment']}")
        
        # Investigate Jesus duplication specifically
        print(f"\n" + "="*60)
        print("INVESTIGATING JESUS DUPLICATION")
        print("="*60)
        
        jesus_cases = [case for case in actual_vs_algorithm_mismatch if 'Jesus' in case['excel_name']]
        
        print(f"Jesus cases found: {len(jesus_cases)}")
        for case in jesus_cases:
            print(f"\n{case['excel_name']}:")
            print(f"  Actual assignment: {case['actual_restaurant']}")
            
            # Find the corresponding database intern
            for intern in interns:
                if case['excel_name'] in intern.user.full_name or intern.user.full_name in case['excel_name']:
                    print(f"  Database intern: {intern.user.full_name}")
                    print(f"  Email: {intern.user.email}")
                    print(f"  Location: {intern.get_full_address()}")
                    print(f"  Age: {intern.age}")
                    print(f"  Transportation: {intern.transportation_method}")
                    
                    # Check algorithm assignment details
                    if intern.user.full_name in algorithm_assigned_interns:
                        print(f"  Algorithm assigned: YES")
                        # Find the specific assignment
                        for assignment in algorithm_assignments:
                            if assignment.get('intern_name') == intern.user.full_name:
                                print(f"    Algorithm restaurant: {assignment.get('restaurant_name')}")
                                print(f"    Commute time: {assignment.get('commute_minutes')} min")
                                break
                    else:
                        print(f"  Algorithm assigned: NO")
                    
                    # Check why no algorithm assignment
                    print(f"  Investigating why no algorithm assignment...")
                    investigate_why_no_assignment(intern, restaurants, case['actual_restaurant'])
        
        return actual_vs_algorithm_mismatch
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def investigate_why_no_assignment(intern, restaurants, actual_restaurant):
    """Investigate why a specific intern has no algorithm assignment"""
    try:
        from app.services.transportation_optimizer import TransportationOptimizer
        
        optimizer = TransportationOptimizer()
        
        print(f"    Checking {intern.user.full_name} -> {actual_restaurant}:")
        
        # Find the actual restaurant in database
        actual_restaurant_db = None
        for restaurant in restaurants:
            if actual_restaurant in restaurant.name or restaurant.name in actual_restaurant:
                actual_restaurant_db = restaurant
                break
        
        if not actual_restaurant_db:
            print(f"      Restaurant '{actual_restaurant}' not found in database")
            return
        
        print(f"      Found restaurant: {actual_restaurant_db.name}")
        
        # Check commute time
        try:
            commute_time = optimizer.get_optimal_commute(
                intern.get_full_address(),
                actual_restaurant_db.get_full_address(),
                intern.transportation_method or 'driving'
            )
            print(f"      Commute time: {commute_time} min")
            
            if commute_time is None:
                print(f"      ERROR: Could not calculate commute time")
            elif commute_time > 50:
                print(f"      ISSUE: Commute time exceeds 50 minute limit")
            else:
                print(f"      OK: Commute time within limits")
        except Exception as e:
            print(f"      ERROR calculating commute: {e}")
        
        # Check age requirement
        if actual_restaurant_db.requires_over_18:
            if intern.age and intern.age >= 18:
                print(f"      OK: Age requirement met ({intern.age} >= 18)")
            else:
                print(f"      ISSUE: Age requirement not met ({intern.age} < 18)")
        else:
            print(f"      OK: No age restriction")
        
        # Check schedule compatibility (basic check)
        if not intern.availability:
            print(f"      ISSUE: No availability data in database")
        else:
            print(f"      OK: Has availability data")
        
    except Exception as e:
        print(f"      Error in investigation: {e}")

def main():
    """Main function"""
    mismatches = investigate_actual_vs_algorithm()
    
    print(f"\n" + "="*80)
    print("ACTUAL VS ALGORITHM ASSIGNMENTS INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
