#!/usr/bin/env python3
"""
Analyze actual matches from Excel file and compare with optimal algorithm
"""

import pandas as pd
import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def analyze_actual_matches():
    """Analyze actual matches from Excel file"""
    print("=== ANALYZING ACTUAL MATCHES FROM EXCEL ===")
    
    # Load the Excel file
    try:
        df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx')
        print(f"Loaded Excel file with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Display first few rows to understand structure
        print("\nFirst few rows:")
        print(df.head())
        
        # Look for intern and restaurant columns
        intern_col = None
        restaurant_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'intern' in col_lower and 'name' in col_lower:
                intern_col = col
            elif 'restaurant' in col_lower and 'name' in col_lower:
                restaurant_col = col
            elif 'restaurant' in col_lower and not restaurant_col:
                restaurant_col = col
        
        print(f"\nDetected columns:")
        print(f"Intern column: {intern_col}")
        print(f"Restaurant column: {restaurant_col}")
        
        if intern_col and restaurant_col:
            # Get actual matches
            actual_matches = df[[intern_col, restaurant_col]].dropna()
            print(f"\nFound {len(actual_matches)} actual matches")
            
            # Display actual matches
            print("\nActual matches:")
            for idx, row in actual_matches.iterrows():
                intern_name = row[intern_col]
                restaurant_name = row[restaurant_col]
                print(f"  {intern_name} -> {restaurant_name}")
            
            return actual_matches, intern_col, restaurant_col
        else:
            print("Could not identify intern and restaurant columns")
            return None, None, None
            
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None, None, None

def compare_with_optimal(actual_matches, intern_col, restaurant_col):
    """Compare actual matches with optimal algorithm"""
    print("\n=== COMPARING WITH OPTIMAL ALGORITHM ===")
    
    if actual_matches is None:
        print("No actual matches to compare")
        return
    
    # Load our optimal algorithm
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
    
    # Create comparison
    print("\n=== COMPARISON ANALYSIS ===")
    
    # Convert actual matches to dict for easier lookup
    actual_dict = {}
    for idx, row in actual_matches.iterrows():
        intern_name = str(row[intern_col]).strip()
        restaurant_name = str(row[restaurant_col]).strip()
        actual_dict[intern_name] = restaurant_name
    
    # Compare each optimal assignment
    better_matches = []
    same_matches = []
    worse_matches = []
    
    for assignment in optimal_assignments:
        optimal_intern = assignment['intern_name']
        optimal_restaurant = assignment['restaurant_name']
        optimal_commute = assignment['commute_minutes']
        optimal_hours = assignment['total_overlap_hours']
        
        # Find actual match for this intern
        actual_restaurant = actual_dict.get(optimal_intern)
        
        if actual_restaurant:
            if actual_restaurant == optimal_restaurant:
                same_matches.append({
                    'intern': optimal_intern,
                    'restaurant': optimal_restaurant,
                    'commute': optimal_commute,
                    'hours': optimal_hours,
                    'status': 'SAME'
                })
            else:
                # Find the actual match details to compare
                actual_assignment_details = None
                for assignment in optimal_assignments:
                    if assignment['intern_name'] == optimal_intern and assignment['restaurant_name'] == actual_restaurant:
                        actual_assignment_details = assignment
                        break
                
                if actual_assignment_details:
                    actual_commute = actual_assignment_details['commute_minutes']
                    actual_hours = actual_assignment_details['total_overlap_hours']
                    
                    # Determine which is better
                    if optimal_commute < actual_commute and optimal_hours >= actual_hours:
                        better_matches.append({
                            'intern': optimal_intern,
                            'optimal_restaurant': optimal_restaurant,
                            'actual_restaurant': actual_restaurant,
                            'optimal_commute': optimal_commute,
                            'actual_commute': actual_commute,
                            'optimal_hours': optimal_hours,
                            'actual_hours': actual_hours,
                            'status': 'BETTER'
                        })
                    elif optimal_commute > actual_commute and optimal_hours <= actual_hours:
                        worse_matches.append({
                            'intern': optimal_intern,
                            'optimal_restaurant': optimal_restaurant,
                            'actual_restaurant': actual_restaurant,
                            'optimal_commute': optimal_commute,
                            'actual_commute': actual_commute,
                            'optimal_hours': optimal_hours,
                            'actual_hours': actual_hours,
                            'status': 'WORSE'
                        })
                    else:
                        same_matches.append({
                            'intern': optimal_intern,
                            'optimal_restaurant': optimal_restaurant,
                            'actual_restaurant': actual_restaurant,
                            'optimal_commute': optimal_commute,
                            'actual_commute': actual_commute,
                            'optimal_hours': optimal_hours,
                            'actual_hours': actual_hours,
                            'status': 'COMPARABLE'
                        })
        else:
            # Intern not in actual matches
            better_matches.append({
                'intern': optimal_intern,
                'optimal_restaurant': optimal_restaurant,
                'actual_restaurant': 'NONE',
                'optimal_commute': optimal_commute,
                'actual_commute': 'N/A',
                'optimal_hours': optimal_hours,
                'actual_hours': 'N/A',
                'status': 'NEW MATCH'
            })
    
    # Print results
    print(f"\nSAME MATCHES ({len(same_matches)}):")
    for match in same_matches[:5]:  # Show first 5
        print(f"  {match['intern']} -> {match['restaurant']} ({match['commute']} min, {match['hours']} hrs)")
    
    print(f"\nBETTER MATCHES ({len(better_matches)}):")
    for match in better_matches[:5]:  # Show first 5
        print(f"  {match['intern']}:")
        print(f"    Optimal: {match['optimal_restaurant']} ({match['optimal_commute']} min, {match['optimal_hours']} hrs)")
        print(f"    Actual:  {match['actual_restaurant']} ({match['actual_commute']} min, {match['actual_hours']} hrs)")
        print(f"    Improvement: {match['actual_commute'] - match['optimal_commute']} min less commute")
    
    print(f"\nWORSE MATCHES ({len(worse_matches)}):")
    for match in worse_matches[:5]:  # Show first 5
        print(f"  {match['intern']}:")
        print(f"    Optimal: {match['optimal_restaurant']} ({match['optimal_commute']} min, {match['optimal_hours']} hrs)")
        print(f"    Actual:  {match['actual_restaurant']} ({match['actual_commute']} min, {match['actual_hours']} hrs)")
        print(f"    Difference: {match['optimal_commute'] - match['actual_commute']} min more commute")
    
    # Summary statistics
    total_optimal = len(optimal_assignments)
    total_actual = len(actual_matches)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total optimal assignments: {total_optimal}")
    print(f"Total actual matches: {total_actual}")
    print(f"Same matches: {len(same_matches)} ({len(same_matches)/total_optimal*100:.1f}%)")
    print(f"Better matches: {len(better_matches)} ({len(better_matches)/total_optimal*100:.1f}%)")
    print(f"Worse matches: {len(worse_matches)} ({len(worse_matches)/total_optimal*100:.1f}%)")
    
    if better_matches:
        avg_commute_improvement = sum(m['actual_commute'] - m['optimal_commute'] for m in better_matches if isinstance(m['actual_commute'], int)) / len(better_matches)
        print(f"Average commute improvement: {avg_commute_improvement:.1f} minutes")
    
    return {
        'same': same_matches,
        'better': better_matches,
        'worse': worse_matches,
        'summary': {
            'total_optimal': total_optimal,
            'total_actual': total_actual,
            'same_pct': len(same_matches)/total_optimal*100,
            'better_pct': len(better_matches)/total_optimal*100,
            'worse_pct': len(worse_matches)/total_optimal*100
        }
    }

def analyze_specific_interns(actual_matches, intern_col, restaurant_col):
    """Analyze specific interns we've been discussing"""
    print("\n=== SPECIFIC INTERN ANALYSIS ===")
    
    target_interns = ["Ollie O'Malley", "Shelsea Vasquez", "Angel Ruiz"]
    
    for target_intern in target_interns:
        print(f"\n--- {target_intern} ---")
        
        # Find actual match
        actual_match = None
        for idx, row in actual_matches.iterrows():
            intern_name = str(row[intern_col]).strip()
            if target_intern.lower() in intern_name.lower() or intern_name.lower() in target_intern.lower():
                actual_match = str(row[restaurant_col]).strip()
                print(f"Actual match: {intern_name} -> {actual_match}")
                break
        
        if not actual_match:
            print(f"No actual match found for {target_intern}")
            continue
        
        # Get optimal match
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
        
        optimal_match = None
        for assignment in optimal_assignments:
            if target_intern.lower() in assignment['intern_name'].lower():
                optimal_match = assignment
                break
        
        if optimal_match:
            print(f"Optimal match: {optimal_match['intern_name']} -> {optimal_match['restaurant_name']}")
            print(f"  Commute: {optimal_match['commute_minutes']} minutes")
            print(f"  Hours: {optimal_match['total_overlap_hours']} hours")
            print(f"  Days: {optimal_match['days_matched']}")
            
            if actual_match == optimal_match['restaurant_name']:
                print("  Status: SAME MATCH")
            else:
                print("  Status: DIFFERENT MATCH")
                print(f"  Analysis: Optimal algorithm suggests {optimal_match['restaurant_name']} instead of {actual_match}")
        else:
            print(f"No optimal match found for {target_intern}")

if __name__ == "__main__":
    # Analyze actual matches
    actual_matches, intern_col, restaurant_col = analyze_actual_matches()
    
    if actual_matches is not None:
        # Compare with optimal
        comparison_results = compare_with_optimal(actual_matches, intern_col, restaurant_col)
        
        # Analyze specific interns
        analyze_specific_interns(actual_matches, intern_col, restaurant_col)
    
    print("\n=== ANALYSIS COMPLETE ===")
