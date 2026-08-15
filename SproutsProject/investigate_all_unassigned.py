#!/usr/bin/env python3
"""
Investigate ALL interns with actual assignments but no algorithm assignments
What's really blocking them?
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_all_unassigned():
    """Investigate all unassigned interns with actual assignments"""
    print("="*80)
    print("INVESTIGATING ALL UNASSIGNED INTERNS")
    print("What's blocking interns with actual assignments from getting algorithm assignments?")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get data
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        optimizer = TransportationOptimizer()
        
        # Load Excel data
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_excel = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        
        # Get current algorithm results
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
        
        # Find all interns with actual assignments but no algorithm assignments
        print(f"\n1. FINDING ALL ACTUAL VS ALGORITHM MISMATCHES")
        print("-" * 40)
        
        actual_vs_algorithm_mismatches = []
        
        for idx, row in df_excel.iterrows():
            excel_name = str(row['Name']).strip()
            actual_restaurant = str(row['Restaurant']).strip()
            
            # Skip if no actual restaurant
            if pd.isna(row['Restaurant']) or actual_restaurant == 'nan' or actual_restaurant == '':
                continue
            
            # Check if intern is in database
            intern_in_db = False
            db_intern = None
            for intern in interns:
                if excel_name in intern.user.full_name or intern.user.full_name in excel_name:
                    intern_in_db = True
                    db_intern = intern
                    break
            
            if not intern_in_db:
                continue
            
            # Check if they have algorithm assignment
            has_algorithm_assignment = any(excel_name in assigned_name for assigned_name in assigned_interns)
            
            if intern_in_db and not has_algorithm_assignment:
                actual_vs_algorithm_mismatches.append({
                    'excel_name': excel_name,
                    'actual_restaurant': actual_restaurant,
                    'db_intern': db_intern
                })
        
        print(f"Found {len(actual_vs_algorithm_mismatches)} interns with actual assignments but no algorithm assignments")
        
        print(f"\n2. DETAILED ANALYSIS OF EACH CASE")
        print("-" * 40)
        
        # Categorize the issues
        categories = {
            'availability_issues': [],
            'commute_issues': [],
            'age_issues': [],
            'schedule_overlap_issues': [],
            'unknown_issues': []
        }
        
        for case in actual_vs_algorithm_mismatches:
            intern = case['db_intern']
            actual_restaurant = case['actual_restaurant']
            
            print(f"\n{case['excel_name']}:")
            print(f"  Actual: {actual_restaurant}")
            print(f"  Email: {intern.user.email}")
            print(f"  Location: {intern.get_full_address()}")
            print(f"  Age: {intern.age}")
            print(f"  Transportation: {intern.transportation_method}")
            
            # Check availability
            has_availability = False
            availability_status = "NO AVAILABILITY DATA"
            if intern.availability:
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                has_any = False
                for day in days:
                    am = getattr(intern.availability, f'{day}_am')
                    pm = getattr(intern.availability, f'{day}_pm')
                    if am or pm:
                        has_any = True
                        break
                
                if has_any:
                    has_availability = True
                    availability_status = "HAS AVAILABILITY"
                else:
                    availability_status = "ALL FALSE"
            
            print(f"  Availability: {availability_status}")
            
            # Check commute to actual restaurant
            actual_restaurant_db = None
            for restaurant in restaurants:
                if actual_restaurant in restaurant.name or restaurant.name in actual_restaurant:
                    actual_restaurant_db = restaurant
                    break
            
            commute_issue = False
            if actual_restaurant_db:
                try:
                    commute_time = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        actual_restaurant_db.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    print(f"  Commute to actual: {commute_time} min")
                    
                    if commute_time is None:
                        commute_issue = True
                        print(f"    ERROR: Cannot calculate commute")
                    elif commute_time > 90:
                        commute_issue = True
                        print(f"    ISSUE: Commute exceeds 90 min limit")
                except Exception as e:
                    commute_issue = True
                    print(f"    ERROR: {e}")
            else:
                commute_issue = True
                print(f"  Restaurant not found in database")
            
            # Check age requirements
            age_issue = False
            if actual_restaurant_db and actual_restaurant_db.requires_over_18:
                if not intern.age or intern.age < 18:
                    age_issue = True
                    print(f"  Age issue: Restaurant requires 18+, intern is {intern.age}")
            
            # Check if they have ANY possible assignments
            possible_assignments = 0
            if has_availability and not commute_issue and not age_issue:
                for restaurant in restaurants:
                    if restaurant.requires_over_18 and (not intern.age or intern.age < 18):
                        continue
                    
                    try:
                        commute = optimizer.get_optimal_commute(
                            intern.get_full_address(),
                            restaurant.get_full_address(),
                            intern.transportation_method or 'driving'
                        )
                        
                        if commute and commute <= 90:
                            possible_assignments += 1
                    except:
                        pass
                
                print(f"  Possible restaurants within 90 min: {possible_assignments}")
                
                if possible_assignments == 0:
                    print(f"    ISSUE: No restaurants within commute limit")
                elif possible_assignments < 3:
                    print(f"    WARNING: Limited options ({possible_assignments} restaurants)")
            
            # Categorize the issue
            if not has_availability:
                categories['availability_issues'].append(case)
                print(f"  PRIMARY ISSUE: AVAILABILITY")
            elif commute_issue:
                categories['commute_issues'].append(case)
                print(f"  PRIMARY ISSUE: COMMUTE")
            elif age_issue:
                categories['age_issues'].append(case)
                print(f"  PRIMARY ISSUE: AGE RESTRICTION")
            elif possible_assignments > 0:
                categories['schedule_overlap_issues'].append(case)
                print(f"  PRIMARY ISSUE: SCHEDULE OVERLAP (has options but no 12+ hour overlap)")
            else:
                categories['unknown_issues'].append(case)
                print(f"  PRIMARY ISSUE: UNKNOWN")
        
        print(f"\n3. SUMMARY BY CATEGORY")
        print("-" * 40)
        
        for category, cases in categories.items():
            print(f"\n{category.upper().replace('_', ' ')}: {len(cases)} cases")
            for case in cases:
                print(f"  - {case['excel_name']} -> {case['actual_restaurant']}")
        
        return categories
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    """Main function"""
    categories = investigate_all_unassigned()
    
    print(f"\n" + "="*80)
    print("ALL UNASSIGNED INVESTIGATION COMPLETE")
    print("="*80)
    
    total_issues = sum(len(cases) for cases in categories.values())
    print(f"Total cases investigated: {total_issues}")
    
    if categories:
        print(f"\nIssue breakdown:")
        for category, cases in categories.items():
            percentage = len(cases) / total_issues * 100 if total_issues > 0 else 0
            print(f"  {category.replace('_', ' ').title()}: {len(cases)} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
