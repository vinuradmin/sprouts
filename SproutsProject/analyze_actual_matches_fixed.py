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

def extract_actual_matches():
    """Extract actual matches from Contact Info sheet"""
    print("=== EXTRACTING ACTUAL MATCHES ===")
    
    try:
        # Load Contact Info sheet
        contact_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Contact Info')
        print(f"Contact Info sheet shape: {contact_df.shape}")
        print(f"Columns: {list(contact_df.columns)}")
        
        # Find relevant columns
        intern_col = None
        restaurant_col = None
        
        for col in contact_df.columns:
            col_lower = col.lower()
            if 'intern' in col_lower and 'ct' in col_lower:
                intern_col = col
            elif 'restaurant' in col_lower and 'host' in col_lower:
                restaurant_col = col
        
        print(f"\nDetected columns:")
        print(f"Intern column: {intern_col}")
        print(f"Restaurant column: {restaurant_col}")
        
        if intern_col and restaurant_col:
            # Extract actual matches
            actual_matches = []
            
            for idx, row in contact_df.iterrows():
                intern_name = str(row[intern_col]).strip() if pd.notna(row[intern_col]) else ''
                restaurant_name = str(row[restaurant_col]).strip() if pd.notna(row[restaurant_col]) else ''
                
                if intern_name and restaurant_name and intern_name != 'nan' and restaurant_name != 'nan':
                    actual_matches.append({
                        'intern_name': intern_name,
                        'restaurant_name': restaurant_name
                    })
            
            print(f"\nFound {len(actual_matches)} actual matches:")
            
            # Display matches
            for i, match in enumerate(actual_matches[:20]):  # Show first 20
                print(f"  {i+1}. {match['intern_name']} -> {match['restaurant_name']}")
            
            if len(actual_matches) > 20:
                print(f"  ... and {len(actual_matches) - 20} more")
            
            return actual_matches
        else:
            print("Could not identify intern and restaurant columns")
            return []
            
    except Exception as e:
        print(f"Error extracting matches: {e}")
        return []

def get_fall_interns():
    """Get interns from Fall 2022"""
    print("\n=== EXTRACTING FALL 2022 INTERNS ===")
    
    try:
        # Load Internship Duration sheet
        duration_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Internship Duration')
        print(f"Internship Duration sheet shape: {duration_df.shape}")
        
        # Find Fall 2022 column
        fall_col = None
        for col in duration_df.columns:
            if 'fall' in col.lower() and '22' in col:
                fall_col = col
                break
        
        print(f"Fall 2022 column: {fall_col}")
        
        if fall_col:
            fall_interns = []
            for idx, row in duration_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                intern_name = str(row['Name']).strip() if pd.notna(row['Name']) else ''
                fall_info = str(row[fall_col]).strip() if pd.notna(row[fall_col]) else ''
                
                if intern_name and intern_name != 'nan' and fall_info and fall_info != 'nan':
                    fall_interns.append({
                        'intern_name': intern_name,
                        'fall_info': fall_info
                    })
            
            print(f"\nFound {len(fall_interns)} Fall 2022 interns:")
            for intern in fall_interns[:10]:
                print(f"  - {intern['intern_name']}: {intern['fall_info']}")
            
            if len(fall_interns) > 10:
                print(f"  ... and {len(fall_interns) - 10} more")
            
            return fall_interns
        else:
            print("Could not find Fall 2022 column")
            return []
            
    except Exception as e:
        print(f"Error extracting Fall interns: {e}")
        return []

def compare_with_optimal(actual_matches, fall_interns):
    """Compare actual matches with optimal algorithm for Fall interns"""
    print("\n=== COMPARING WITH OPTIMAL ALGORITHM ===")
    
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
    
    # Focus on Fall interns
    fall_intern_names = [intern['intern_name'] for intern in fall_interns]
    
    # Filter actual matches for Fall interns
    fall_actual_matches = []
    for match in actual_matches:
        for fall_name in fall_intern_names:
            if fall_name.lower() in match['intern_name'].lower() or match['intern_name'].lower() in fall_name.lower():
                fall_actual_matches.append(match)
                break
    
    print(f"\nFall 2022 actual matches: {len(fall_actual_matches)}")
    for match in fall_actual_matches:
        print(f"  {match['intern_name']} -> {match['restaurant_name']}")
    
    # Filter optimal assignments for Fall interns
    fall_optimal_assignments = []
    for assignment in optimal_assignments:
        for fall_name in fall_intern_names:
            if fall_name.lower() in assignment['intern_name'].lower() or assignment['intern_name'].lower() in fall_name.lower():
                fall_optimal_assignments.append(assignment)
                break
    
    print(f"\nFall 2022 optimal assignments: {len(fall_optimal_assignments)}")
    for assignment in fall_optimal_assignments:
        print(f"  {assignment['intern_name']} -> {assignment['restaurant_name']} ({assignment['commute_minutes']} min, {assignment['total_overlap_hours']} hrs)")
    
    # Compare
    print("\n=== COMPARISON ANALYSIS ===")
    
    better_matches = []
    same_matches = []
    different_matches = []
    
    # Create lookup for optimal assignments
    optimal_lookup = {assignment['intern_name']: assignment for assignment in fall_optimal_assignments}
    
    for actual_match in fall_actual_matches:
        intern_name = actual_match['intern_name']
        actual_restaurant = actual_match['restaurant_name']
        
        # Find corresponding optimal assignment
        optimal_assignment = None
        for opt_name, opt_assignment in optimal_lookup.items():
            if intern_name.lower() in opt_name.lower() or opt_name.lower() in intern_name.lower():
                optimal_assignment = opt_assignment
                break
        
        if optimal_assignment:
            optimal_restaurant = optimal_assignment['restaurant_name']
            optimal_commute = optimal_assignment['commute_minutes']
            optimal_hours = optimal_assignment['total_overlap_hours']
            
            if actual_restaurant == optimal_restaurant:
                same_matches.append({
                    'intern': intern_name,
                    'restaurant': actual_restaurant,
                    'commute': optimal_commute,
                    'hours': optimal_hours,
                    'status': 'SAME'
                })
            else:
                different_matches.append({
                    'intern': intern_name,
                    'actual_restaurant': actual_restaurant,
                    'optimal_restaurant': optimal_restaurant,
                    'optimal_commute': optimal_commute,
                    'optimal_hours': optimal_hours,
                    'status': 'DIFFERENT'
                })
        else:
            print(f"  No optimal assignment found for {intern_name}")
    
    # Print results
    print(f"\nSAME MATCHES ({len(same_matches)}):")
    for match in same_matches:
        print(f"  {match['intern']} -> {match['restaurant']} ({match['commute']} min, {match['hours']} hrs)")
    
    print(f"\nDIFFERENT MATCHES ({len(different_matches)}):")
    for match in different_matches:
        print(f"  {match['intern']}:")
        print(f"    Actual:  {match['actual_restaurant']}")
        print(f"    Optimal: {match['optimal_restaurant']} ({match['optimal_commute']} min, {match['optimal_hours']} hrs)")
    
    # Summary
    total_fall_matches = len(fall_actual_matches)
    print(f"\n=== FALL 2022 SUMMARY ===")
    print(f"Total Fall matches: {total_fall_matches}")
    print(f"Same matches: {len(same_matches)} ({len(same_matches)/total_fall_matches*100:.1f}%)")
    print(f"Different matches: {len(different_matches)} ({len(different_matches)/total_fall_matches*100:.1f}%)")
    
    return {
        'same': same_matches,
        'different': different_matches,
        'summary': {
            'total_fall': total_fall_matches,
            'same_pct': len(same_matches)/total_fall_matches*100,
            'different_pct': len(different_matches)/total_fall_matches*100
        }
    }

def analyze_specific_interns(actual_matches, fall_interns):
    """Analyze specific interns we've been discussing"""
    print("\n=== SPECIFIC INTERN ANALYSIS ===")
    
    target_interns = ["Ollie", "Shelsea", "Angel"]
    
    for target_intern in target_interns:
        print(f"\n--- {target_intern} ---")
        
        # Find in Fall interns
        fall_match = None
        for intern in fall_interns:
            if target_intern.lower() in intern['intern_name'].lower():
                fall_match = intern
                print(f"Fall 2022: {intern['intern_name']} - {intern['fall_info']}")
                break
        
        # Find actual match
        actual_match = None
        for match in actual_matches:
            if target_intern.lower() in match['intern_name'].lower():
                actual_match = match
                print(f"Actual match: {match['intern_name']} -> {match['restaurant_name']}")
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
            
            if actual_match and actual_match['restaurant_name'] == optimal_match['restaurant_name']:
                print("  Status: SAME MATCH")
            else:
                print("  Status: DIFFERENT MATCH")
                if actual_match:
                    print(f"  Analysis: Optimal suggests {optimal_match['restaurant_name']} instead of {actual_match['restaurant_name']}")
        else:
            print(f"No optimal match found for {target_intern}")

if __name__ == "__main__":
    # Extract actual matches
    actual_matches = extract_actual_matches()
    
    # Get Fall interns
    fall_interns = get_fall_interns()
    
    if actual_matches and fall_interns:
        # Compare with optimal
        comparison_results = compare_with_optimal(actual_matches, fall_interns)
        
        # Analyze specific interns
        analyze_specific_interns(actual_matches, fall_interns)
    
    print("\n=== ANALYSIS COMPLETE ===")
