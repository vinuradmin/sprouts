#!/usr/bin/env python3
"""
Check if algorithm respects business rules: max 2 interns per restaurant and age restrictions
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_business_rules():
    """Check business rules compliance"""
    print("="*80)
    print("CHECKING BUSINESS RULES COMPLIANCE")
    print("Max 2 interns per restaurant + Age restrictions")
    print("="*80)
    
    try:
        # Get algorithm assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Total algorithm assignments: {len(assignments)}")
        print(f"Total interns: {len(interns)}")
        print(f"Total restaurants: {len(restaurants)}")
        
        # Check restaurant capacity (max 2 interns per restaurant)
        print(f"\n" + "="*60)
        print("RESTAURANT CAPACITY CHECK (Max 2 Interns)")
        print("="*60)
        
        restaurant_counts = {}
        violations = []
        
        for assign in assignments:
            restaurant_name = assign['restaurant_name']
            intern_name = assign['intern_name']
            
            if restaurant_name not in restaurant_counts:
                restaurant_counts[restaurant_name] = []
            restaurant_counts[restaurant_name].append(intern_name)
        
        print(f"Restaurant assignments:")
        for restaurant, intern_list in sorted(restaurant_counts.items()):
            count = len(intern_list)
            status = "OK" if count <= 2 else "VIOLATION"
            
            print(f"  {restaurant}: {count} interns {status}")
            for intern in intern_list:
                print(f"    - {intern}")
            
            if count > 2:
                violations.append({
                    'type': 'capacity',
                    'restaurant': restaurant,
                    'count': count,
                    'interns': intern_list
                })
        
        print(f"\nCapacity violations: {len(violations)}")
        for violation in violations:
            print(f"  ✗ {violation['restaurant']}: {violation['count']} interns (max 2 allowed)")
        
        # Check age restrictions
        print(f"\n" + "="*60)
        print("AGE RESTRICTIONS CHECK")
        print("="*60)
        
        age_violations = []
        intern_lookup = {intern.user.full_name: intern for intern in interns}
        restaurant_lookup = {restaurant.name: restaurant for restaurant in restaurants}
        
        print(f"Age restriction checks:")
        for assign in assignments:
            intern_name = assign['intern_name']
            restaurant_name = assign['restaurant_name']
            
            intern = intern_lookup.get(intern_name)
            restaurant = restaurant_lookup.get(restaurant_name)
            
            if intern and restaurant:
                intern_age = intern.age
                restaurant_requirement = restaurant.requires_over_18
                
                # Check if intern is underage and restaurant requires 18+
                if restaurant_requirement and intern_age and intern_age < 18:
                    age_violations.append({
                        'intern': intern_name,
                        'restaurant': restaurant_name,
                        'intern_age': intern_age,
                        'requirement': '18+',
                        'violation': True
                    })
                    print(f"  VIOLATION {intern_name} (age {intern_age}) -> {restaurant_name} (requires 18+)")
                elif restaurant_requirement:
                    print(f"  OK {intern_name} (age {intern_age}) -> {restaurant_name} (requires 18+)")
                else:
                    print(f"  OK {intern_name} (age {intern_age}) -> {restaurant_name} (no age restriction)")
            else:
                print(f"  ? {intern_name} -> {restaurant_name} (data missing)")
        
        print(f"\nAge restriction violations: {len(age_violations)}")
        for violation in age_violations:
            print(f"  VIOLATION {violation['intern']} (age {violation['intern_age']}) assigned to {violation['restaurant']} (requires {violation['requirement']})")
        
        # Check actual assignments for comparison
        print(f"\n" + "="*60)
        print("ACTUAL ASSIGNMENTS COMPARISON")
        print("="*60)
        
        # Load actual assignments from Excel
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        actual_restaurant_counts = {}
        
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                if actual_restaurant != 'nan' and actual_restaurant != '' and actual_restaurant != 'Unassigned':
                    if actual_restaurant not in actual_restaurant_counts:
                        actual_restaurant_counts[actual_restaurant] = []
                    actual_restaurant_counts[actual_restaurant].append(actual_name)
        
        print(f"Actual restaurant assignments:")
        actual_violations = []
        
        for restaurant, intern_list in sorted(actual_restaurant_counts.items()):
            count = len(intern_list)
            status = "OK" if count <= 2 else "VIOLATION"
            
            print(f"  {restaurant}: {count} interns {status}")
            for intern in intern_list:
                print(f"    - {intern}")
            
            if count > 2:
                actual_violations.append({
                    'restaurant': restaurant,
                    'count': count,
                    'interns': intern_list
                })
        
        print(f"\nActual assignment capacity violations: {len(actual_violations)}")
        for violation in actual_violations:
            print(f"  ✗ {violation['restaurant']}: {violation['count']} interns (max 2 allowed)")
        
        # Summary
        print(f"\n" + "="*60)
        print("BUSINESS RULES COMPLIANCE SUMMARY")
        print("="*60)
        
        print(f"Algorithm Assignments:")
        print(f"  Total assignments: {len(assignments)}")
        print(f"  Capacity violations: {len(violations)}")
        print(f"  Age restriction violations: {len(age_violations)}")
        print(f"  Compliance rate: {((len(assignments) - len(violations) - len(age_violations)) / len(assignments) * 100):.1f}%")
        
        print(f"\nActual Assignments:")
        print(f"  Total assignments: {sum(len(interns) for interns in actual_restaurant_counts.values())}")
        print(f"  Capacity violations: {len(actual_violations)}")
        
        return {
            'algorithm_assignments': len(assignments),
            'capacity_violations': len(violations),
            'age_violations': len(age_violations),
            'actual_capacity_violations': len(actual_violations)
        }
        
    except Exception as e:
        print(f"Error checking business rules: {e}")
        return {}

def main():
    """Main function"""
    results = check_business_rules()
    
    print(f"\n" + "="*80)
    print("BUSINESS RULES CHECK COMPLETE")
    print("="*80)
    
    if results:
        print(f"Algorithm compliance: {results.get('algorithm_assignments', 0)} assignments")
        print(f"Capacity violations: {results.get('capacity_violations', 0)}")
        print(f"Age violations: {results.get('age_violations', 0)}")
        print(f"Actual violations: {results.get('actual_capacity_violations', 0)}")

if __name__ == "__main__":
    main()
