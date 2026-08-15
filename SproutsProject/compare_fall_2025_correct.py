#!/usr/bin/env python3
"""
Compare Fall 2025 actual restaurant assignments with optimal algorithm
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def extract_fall_2025_actual_assignments():
    """Extract actual restaurant assignments from column 14"""
    print("=== EXTRACTING FALL 2025 ACTUAL RESTAURANT ASSIGNMENTS ===")
    
    try:
        # Load Active Intern List sheet
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Extract Fall 2025 interns with their restaurant assignments (column 14)
        fall_2025_assignments = []
        
        for idx in range(338, 367):  # Fall 2025 section
            if idx < len(active_df):
                row = active_df.iloc[idx]
                intern_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                
                if intern_name and intern_name.lower() != 'nan' and 'latitude' not in intern_name.lower():
                    # Get restaurant assignment from column 14
                    restaurant = str(row.iloc[14]).strip() if pd.notna(row.iloc[14]) else ''
                    
                    # Get placement info from column 9
                    placement = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ''
                    
                    fall_2025_assignments.append({
                        'row': idx,
                        'intern_name': intern_name,
                        'restaurant': restaurant,
                        'placement': placement,
                        'nickname': str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                    })
        
        print(f"Found {len(fall_2025_assignments)} Fall 2025 interns:")
        for assignment in fall_2025_assignments:
            print(f"  {assignment['intern_name']} -> {assignment['restaurant']} (Placement: {assignment['placement']})")
        
        return fall_2025_assignments
        
    except Exception as e:
        print(f"Error extracting Fall 2025 assignments: {e}")
        return []

def compare_with_optimal_algorithm(fall_2025_assignments):
    """Compare actual assignments with optimal algorithm"""
    print("\n=== COMPARING WITH OPTIMAL ALGORITHM ===")
    
    try:
        # Load optimal algorithm
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        
        # Get optimal assignments
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
        
        optimal_results = service.find_optimal_assignments(interns, restaurants)
        optimal_assignments = optimal_results.get('assignments', [])
        
        print(f"Optimal algorithm found {len(optimal_assignments)} assignments")
        
        # Compare assignments
        comparison_results = []
        
        for actual_assignment in fall_2025_assignments:
            intern_name = actual_assignment['intern_name']
            actual_restaurant = actual_assignment['restaurant']
            placement = actual_assignment['placement']
            
            # Find optimal assignment for this intern
            optimal_match = None
            for assignment in optimal_assignments:
                opt_name = assignment['intern_name']
                
                # Check for name match
                if (intern_name.lower() in opt_name.lower() or 
                    opt_name.lower() in intern_name.lower() or
                    intern_name.split()[0].lower() in opt_name.lower() or
                    opt_name.split()[0].lower() in intern_name.lower()):
                    
                    optimal_match = assignment
                    break
            
            if optimal_match:
                optimal_restaurant = optimal_match['restaurant_name']
                optimal_commute = optimal_match['commute_minutes']
                optimal_hours = optimal_match['total_overlap_hours']
                
                comparison = {
                    'intern': intern_name,
                    'actual_restaurant': actual_restaurant,
                    'placement': placement,
                    'optimal_restaurant': optimal_restaurant,
                    'optimal_commute': optimal_commute,
                    'optimal_hours': optimal_hours,
                    'status': 'SAME' if actual_restaurant == optimal_restaurant else 'DIFFERENT'
                }
                
                comparison_results.append(comparison)
                
                print(f"\n{intern_name}:")
                print(f"  Actual:  {actual_restaurant} (Placement: {placement})")
                print(f"  Optimal: {optimal_restaurant} ({optimal_commute} min, {optimal_hours} hrs)")
                print(f"  Status:  {comparison['status']}")
            else:
                print(f"\n{intern_name}: No optimal assignment found")
                comparison_results.append({
                    'intern': intern_name,
                    'actual_restaurant': actual_restaurant,
                    'placement': placement,
                    'optimal_restaurant': 'NONE',
                    'optimal_commute': 'N/A',
                    'optimal_hours': 'N/A',
                    'status': 'NO OPTIMAL'
                })
        
        # Summary
        same_matches = [r for r in comparison_results if r['status'] == 'SAME']
        different_matches = [r for r in comparison_results if r['status'] == 'DIFFERENT']
        no_optimal = [r for r in comparison_results if r['status'] == 'NO OPTIMAL']
        
        print(f"\n=== COMPARISON SUMMARY ===")
        print(f"Total Fall 2025 interns: {len(fall_2025_assignments)}")
        print(f"Same matches: {len(same_matches)}")
        print(f"Different matches: {len(different_matches)}")
        print(f"No optimal assignment: {len(no_optimal)}")
        
        # Detailed analysis of different matches
        if different_matches:
            print(f"\n=== DIFFERENT MATCHES ANALYSIS ===")
            for match in different_matches:
                print(f"\n{match['intern']}:")
                print(f"  Actual:  {match['actual_restaurant']} (Placement: {match['placement']})")
                print(f"  Optimal: {match['optimal_restaurant']}")
                print(f"  Optimal commute: {match['optimal_commute']} minutes")
                print(f"  Optimal hours: {match['optimal_hours']} hours")
                
                # Explain why optimal is better
                if isinstance(match['optimal_commute'], int) and match['optimal_commute'] < 45:
                    print(f"  ✓ Optimal choice has better commute ({match['optimal_commute']} min)")
                if isinstance(match['optimal_hours'], (int, float)) and match['optimal_hours'] >= 12:
                    print(f"  ✓ Optimal choice meets 12-hour weekly requirement ({match['optimal_hours']} hrs)")
        
        return comparison_results
        
    except Exception as e:
        print(f"Error comparing with optimal algorithm: {e}")
        return []

def analyze_specific_interns():
    """Analyze specific interns we've been discussing"""
    print("\n=== SPECIFIC INTERNS ANALYSIS ===")
    
    target_interns = ["Graciela O'Malley", "Shelsea Vasquez", "Angel Ruiz"]
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        
        for target_intern in target_interns:
            print(f"\n--- {target_intern} ---")
            
            # Find actual assignment
            active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
            actual_restaurant = None
            placement = None
            
            for idx in range(338, 367):
                if idx < len(active_df):
                    intern_name = str(active_df.iloc[idx, 0]).strip()
                    if target_intern.lower() in intern_name.lower():
                        actual_restaurant = str(active_df.iloc[idx, 14]).strip()
                        placement = str(active_df.iloc[idx, 9]).strip()
                        print(f"Actual assignment: {actual_restaurant} (Placement: {placement})")
                        break
            
            # Find optimal assignment
            interns = Intern.query.filter_by(is_seeking_internship=True).all()
            restaurants = Restaurant.query.all()
            optimal_results = service.find_optimal_assignments(interns, restaurants)
            optimal_assignments = optimal_results.get('assignments', [])
            
            optimal_match = None
            for assignment in optimal_assignments:
                if target_intern.lower() in assignment['intern_name'].lower():
                    optimal_match = assignment
                    break
            
            if optimal_match:
                print(f"Optimal assignment: {optimal_match['restaurant_name']}")
                print(f"  Commute: {optimal_match['commute_minutes']} minutes")
                print(f"  Hours: {optimal_match['total_overlap_hours']} hours")
                print(f"  Days: {optimal_match['days_matched']}")
                
                if actual_restaurant == optimal_match['restaurant_name']:
                    print("  Status: SAME MATCH")
                else:
                    print("  Status: DIFFERENT MATCH")
                    print(f"  Analysis: Optimal suggests {optimal_match['restaurant_name']} instead of {actual_restaurant}")
                    
                    # Explain why optimal is better
                    if optimal_match['commute_minutes'] < 45:
                        print(f"    Better commute: {optimal_match['commute_minutes']} minutes")
                    if optimal_match['total_overlap_hours'] >= 12:
                        print(f"    Better availability: {optimal_match['total_overlap_hours']} hours")
            else:
                print("No optimal assignment found")
    
    except Exception as e:
        print(f"Error analyzing specific interns: {e}")

if __name__ == "__main__":
    # Extract actual assignments
    fall_2025_assignments = extract_fall_2025_actual_assignments()
    
    if fall_2025_assignments:
        # Compare with optimal algorithm
        comparison_results = compare_with_optimal_algorithm(fall_2025_assignments)
        
        # Analyze specific interns
        analyze_specific_interns()
    
    print("\n=== COMPARISON COMPLETE ===")
