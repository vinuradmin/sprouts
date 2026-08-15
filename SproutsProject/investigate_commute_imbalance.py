#!/usr/bin/env python3
"""
Investigate why optimal algorithm has much worse average commute
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_commute_imbalance():
    """Investigate the commute imbalance issue"""
    print("=== INVESTIGATING COMMUTE IMBALANCE ===")
    
    try:
        # Load the comparison data
        df = pd.read_csv('fall_2025_comparison.csv')
        data_rows = df[df['Intern Name'] != 'SUMMARY STATISTICS'].copy()
        
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
        
        print(f"Optimal assignments: {len(optimal_assignments)}")
        
        # Analyze commute distribution
        optimal_commutes = []
        for assignment in optimal_assignments:
            optimal_commutes.append(assignment['commute_minutes'])
        
        optimal_commutes.sort()
        
        print(f"\n=== OPTIMAL COMMUTE DISTRIBUTION ===")
        print(f"Min commute: {min(optimal_commutes)} minutes")
        print(f"Max commute: {max(optimal_commutes)} minutes")
        print(f"Average: {sum(optimal_commutes)/len(optimal_commutes):.1f} minutes")
        print(f"Median: {optimal_commutes[len(optimal_commutes)//2]} minutes")
        
        # Show worst offenders
        worst_commutes = sorted(optimal_assignments, key=lambda x: x['commute_minutes'], reverse=True)[:5]
        print(f"\n=== WORST OPTIMAL COMMUTES ===")
        for assignment in worst_commutes:
            print(f"{assignment['intern_name']} -> {assignment['restaurant_name']}: {assignment['commute_minutes']} minutes")
        
        # Show best commutes
        best_commutes = sorted(optimal_assignments, key=lambda x: x['commute_minutes'])[:5]
        print(f"\n=== BEST OPTIMAL COMMUTES ===")
        for assignment in best_commutes:
            print(f"{assignment['intern_name']} -> {assignment['restaurant_name']}: {assignment['commute_minutes']} minutes")
        
        # Check if we can improve by adjusting weights
        print(f"\n=== WEIGHT ADJUSTMENT ANALYSIS ===")
        print("Current scoring: Commute + Availability + Business Rules")
        print("Potential improvement: Increase commute weight in scoring")
        
        # Check actual vs optimal for specific cases
        print(f"\n=== ACTUAL VS OPTIMAL COMPARISON ===")
        
        for idx in range(338, 367):  # Fall 2025 section
            active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
            if idx < len(active_df):
                row = active_df.iloc[idx]
                intern_name = str(row.iloc[0]).strip()
                actual_restaurant = str(row.iloc[14]).strip()
                
                if intern_name and actual_restaurant and intern_name.lower() != 'nan':
                    # Find optimal assignment
                    optimal_match = None
                    for assignment in optimal_assignments:
                        if (intern_name.lower() in assignment['intern_name'].lower() or 
                            assignment['intern_name'].lower() in intern_name.lower()):
                            optimal_match = assignment
                            break
                    
                    if optimal_match:
                        optimal_restaurant = optimal_match['restaurant_name']
                        optimal_commute = optimal_match['commute_minutes']
                        
                        # Check if actual is better commute
                        actual_commute = get_actual_commute(intern_name, actual_restaurant, service, interns, restaurants)
                        
                        if actual_commute and actual_commute < optimal_commute:
                            improvement = optimal_commute - actual_commute
                            print(f"{intern_name}:")
                            print(f"  Actual: {actual_restaurant} ({actual_commute} min)")
                            print(f"  Optimal: {optimal_restaurant} ({optimal_commute} min)")
                            print(f"  Difference: +{improvement} min (actual better)")
                            
                            # Check if actual is valid
                            check_actual_validity(intern_name, actual_restaurant, service, interns, restaurants)
        
        return optimal_commutes
        
    except Exception as e:
        print(f"Error investigating commute imbalance: {e}")
        return []

def get_actual_commute(intern_name, restaurant_name, service, interns, restaurants):
    """Get commute time for actual placement"""
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
        
        if target_intern and target_restaurant:
            # Calculate commute
            commute_info = service.commute_cache.get_commute(
                target_intern.get_full_address(),
                target_restaurant.get_full_address()
            )
            
            if commute_info:
                return commute_info.value // 60000  # Convert to minutes
        
        return None
        
    except Exception as e:
        return None

def check_actual_validity(intern_name, restaurant_name, service, interns, restaurants):
    """Check if actual placement is valid"""
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
        
        if target_intern and target_restaurant:
            match = service._evaluate_match(target_intern, target_restaurant, 50, 12)
            if match:
                print(f"    Status: VALID ({match['total_overlap_hours']} hrs, {match['days_matched']} days)")
            else:
                print(f"    Status: INVALID (violates business rules)")
        
    except Exception as e:
        print(f"    Status: Unknown (error checking)")

def suggest_improvements():
    """Suggest improvements to the algorithm"""
    print(f"\n=== SUGGESTED IMPROVEMENTS ===")
    print("1. Increase commute weight in scoring function")
    print("2. Add maximum commute constraint (e.g., 45 minutes max)")
    print("3. Implement hybrid approach: optimize for commute + availability")
    print("4. Use lexicographic optimization: minimize max commute first, then total")
    print("5. Add commute penalty for assignments > 30 minutes")
    
    print(f"\n=== CURRENT ALGORITHM PRIORITIES ===")
    print("1. Business rules compliance (must pass)")
    print("2. Availability overlap (12+ hours, 2+ days)")
    print("3. Total commute minimization (Hungarian algorithm)")
    print("4. Individual commute may suffer for system optimum")

if __name__ == "__main__":
    optimal_commutes = investigate_commute_imbalance()
    suggest_improvements()
    
    print(f"\n=== COMMUTE IMBALANCE ANALYSIS ===")
    print("The optimal algorithm prioritizes system-wide optimization over")
    print("individual commute times. This creates a 'commute imbalance' where")
    print("some interns have much longer commutes for the benefit of others.")
    print("\nRECOMMENDATION: Adjust scoring to balance individual and system needs.")
