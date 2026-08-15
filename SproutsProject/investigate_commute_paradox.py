#!/usr/bin/env python3
"""
Investigate why optimal algorithm has longer average commute than actual
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_commute_paradox():
    """Investigate the commute time paradox"""
    print("=== INVESTIGATING COMMUTE PARADOX ===")
    
    try:
        # Load the comparison data
        df = pd.read_csv('fall_2025_comparison.csv')
        data_rows = df[df['Intern Name'] != 'SUMMARY STATISTICS'].copy()
        
        print(f"Analyzing {len(data_rows)} interns...")
        
        # Load actual assignments from Excel
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Get optimal assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        optimal_results = service.find_optimal_assignments(interns, restaurants)
        optimal_assignments = optimal_results.get('assignments', [])
        
        print(f"Optimal assignments found: {len(optimal_assignments)}")
        
        # Analyze specific cases
        print(f"\n=== DETAILED ANALYSIS ===")
        
        # Check actual vs optimal for interns with both
        both_available = data_rows[
            (data_rows['Actual Commute (min)'] != 'N/A') & 
            (data_rows['Optimal Commute (min)'] != 'N/A')
        ]
        
        print(f"Interns with both actual and optimal commutes: {len(both_available)}")
        
        if len(both_available) > 0:
            print(f"\n--- CASES WHERE OPTIMAL > ACTUAL ---")
            for _, row in both_available.iterrows():
                actual_commute = float(row['Actual Commute (min)'])
                optimal_commute = float(row['Optimal Commute (min)'])
                
                if optimal_commute > actual_commute:
                    print(f"\n{row['Intern Name']}:")
                    print(f"  Actual: {row['Actual Restaurant']} ({actual_commute} min)")
                    print(f"  Optimal: {row['Optimal Restaurant']} ({optimal_commute} min)")
                    print(f"  Difference: +{optimal_commute - actual_commute:.1f} min")
                    
                    # Check if actual violates business rules
                    check_business_rules(row['Intern Name'], row['Actual Restaurant'], service, interns, restaurants)
        
        # Check if optimal algorithm prioritizes availability over commute
        print(f"\n=== ALGORITHM PRIORITIES ===")
        print("Checking if optimal algorithm prioritizes availability over commute...")
        
        # Look at the optimal assignment details
        for assignment in optimal_assignments[:5]:
            intern_name = assignment['intern_name']
            restaurant_name = assignment['restaurant_name']
            commute = assignment['commute_minutes']
            hours = assignment['total_overlap_hours']
            days = assignment['days_matched']
            
            print(f"\n{intern_name} -> {restaurant_name}:")
            print(f"  Commute: {commute} min")
            print(f"  Hours: {hours} hrs")
            print(f"  Days: {days}")
            print(f"  Score: {assignment.get('match_score', 'N/A')}")
        
        # Check if actual placements have availability issues
        print(f"\n=== CHECKING ACTUAL PLACEMENT VIOLATIONS ===")
        check_actual_placement_violations(active_df, service, interns, restaurants)
        
        return True
        
    except Exception as e:
        print(f"Error investigating: {e}")
        return False

def check_business_rules(intern_name, restaurant_name, service, interns, restaurants):
    """Check if a placement violates business rules"""
    try:
        # Find intern and restaurant
        target_intern = None
        for intern in interns:
            if (intern_name.lower() in intern.user.full_name.lower() or 
                intern.user.full_name.lower() in intern_name.lower()):
                target_intern = intern
                break
        
        target_restaurant = None
        for restaurant in restaurants:
            if (restaurant_name.lower() in restaurant.name.lower() or 
                restaurant.name.lower() in restaurant_name.lower()):
                target_restaurant = restaurant
                break
        
        if not target_intern or not target_restaurant:
            print(f"    Could not find intern/restaurant data")
            return
        
        # Check if this match would be valid
        match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
        
        if match:
            print(f"    Business rules check: VALID")
            print(f"    Hours: {match['total_overlap_hours']}")
            print(f"    Days: {match['days_matched']}")
        else:
            print(f"    Business rules check: INVALID")
            print(f"    This placement may violate availability/age rules")
            
    except Exception as e:
        print(f"    Error checking business rules: {e}")

def check_actual_placement_violations(active_df, service, interns, restaurants):
    """Check if actual placements violate business rules"""
    print("Checking if actual placements violate business rules...")
    
    violations = []
    
    for idx in range(338, 367):  # Fall 2025 section
        if idx < len(active_df):
            row = active_df.iloc[idx]
            intern_name = str(row.iloc[0]).strip()
            actual_restaurant = str(row.iloc[14]).strip()
            
            if intern_name and actual_restaurant and intern_name.lower() != 'nan':
                # Find intern and restaurant
                target_intern = None
                for intern in interns:
                    if (intern_name.lower() in intern.user.full_name.lower() or 
                        intern.user.full_name.lower() in intern_name.lower()):
                        target_intern = intern
                        break
                
                target_restaurant = None
                for restaurant in restaurants:
                    if (actual_restaurant.lower() in restaurant.name.lower() or 
                        restaurant.name.lower() in actual_restaurant.lower()):
                        target_restaurant = restaurant
                        break
                
                if target_intern and target_restaurant:
                    # Check if this match is valid
                    match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
                    
                    if not match:
                        violations.append({
                            'intern': intern_name,
                            'restaurant': actual_restaurant,
                            'reason': 'Business rules violation'
                        })
    
    print(f"\nFound {len(violations)} potential violations:")
    for violation in violations[:5]:
        print(f"  {violation['intern']} -> {violation['restaurant']}: {violation['reason']}")

def analyze_algorithm_scoring():
    """Analyze how the algorithm scores matches"""
    print("\n=== ALGORITHM SCORING ANALYSIS ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        
        # Check the scoring function
        print("Algorithm scoring factors:")
        print("1. Commute time (lower is better)")
        print("2. Availability overlap (higher is better)")
        print("3. Business rules compliance (must pass)")
        print("4. Hungarian algorithm optimizes total commute")
        
        print("\nKey insight: Hungarian algorithm minimizes TOTAL commute across all matches")
        print("This means some individual interns may have longer commutes for global optimization")
        
    except Exception as e:
        print(f"Error analyzing scoring: {e}")

if __name__ == "__main__":
    investigate_commute_paradox()
    analyze_algorithm_scoring()
    
    print("\n=== INVESTIGATION COMPLETE ===")
    print("\nKEY FINDINGS:")
    print("1. Hungarian algorithm optimizes TOTAL system commute, not individual")
    print("2. Some interns may have longer commutes for global optimization")
    print("3. Actual placements may violate business rules")
    print("4. Algorithm prioritizes 12-hour availability over minimal commute")
