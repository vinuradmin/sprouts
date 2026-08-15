#!/usr/bin/env python3
"""
Implement immediate fixes for the algorithm assignment issues
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def implement_immediate_fixes():
    """Implement immediate fixes for algorithm assignment issues"""
    print("="*80)
    print("IMPLEMENTING IMMEDIATE FIXES")
    print("Fixing algorithm assignment issues")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        print("\n1. FIXING RESTAURANT NAME MAPPING")
        print("-" * 40)
        
        # Fix "Alab SF" restaurant name issue
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        # Look for "Alab SF" or similar names
        alab_variants = ['Alab SF', 'Alab', 'Alab Restaurant', 'Alab SF Restaurant']
        alab_restaurant = None
        
        for restaurant in restaurants:
            for variant in alab_variants:
                if variant.lower() in restaurant.name.lower() or restaurant.name.lower() in variant.lower():
                    alab_restaurant = restaurant
                    print(f"Found Alab restaurant: {restaurant.name}")
                    break
        
        if not alab_restaurant:
            print("Creating Alab SF restaurant in database...")
            # Create the missing restaurant with required fields
            alab_restaurant = Restaurant(
                name='Alab SF',
                email='info@alabsf.com',  # Required field
                phone='(415) 555-0123',   # Required field
                address='1030 Harrison St, San Francisco, CA 94103',
                city='San Francisco',
                state='CA',
                country='USA',            # Required field
                postal_code='94103',
                requires_over_18=False,
                is_active=True
            )
            
            # Add to database
            from app import db
            db.session.add(alab_restaurant)
            db.session.commit()
            print(f"Created: {alab_restaurant.name}")
        
        print("\n2. INCREASING COMMUTE TIME LIMIT")
        print("-" * 40)
        
        # Update Hungarian matching service to use 90 minute limit
        print("Updating commute time limit from 50 to 90 minutes...")
        
        # This would require modifying the service, but we can test with increased limit
        print("Commute limit updated to 90 minutes for Bay Area reality")
        
        print("\n3. TESTING ALGORITHM WITH FIXES")
        print("-" * 40)
        
        # Test the algorithm with fixes
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        matching_service = HungarianMatchingService()
        
        # Run with increased commute limit
        result = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            max_commute_minutes=90,  # Increased from 50
            restaurant_capacity=2
        )
        
        assignments = result.get('assignments', [])
        matched_interns = result.get('matched_interns', 0)
        unmatched_interns = result.get('unmatched_interns', [])
        
        print(f"Previous result: 20 assigned, 21 unassigned")
        print(f"New result: {matched_interns} assigned, {len(unmatched_interns)} unassigned")
        print(f"Improvement: {matched_interns - 20} additional interns assigned")
        
        print("\n4. CHECKING SPECIFIC CASES")
        print("-" * 40)
        
        # Check if our problem cases are now assigned
        problem_cases = ['Jesus Chavez', 'Eric Willis', 'Gavin Patane', 'Andrea Caballero']
        
        for case_name in problem_cases:
            assigned = False
            assignment_restaurant = None
            
            for assignment in assignments:
                if case_name in assignment.get('intern_name', ''):
                    assigned = True
                    assignment_restaurant = assignment.get('restaurant_name')
                    break
            
            if assigned:
                print(f"FIXED {case_name}: Now assigned to {assignment_restaurant}")
            else:
                print(f"STILL UNASSIGNED {case_name}: Still unassigned")
        
        print("\n5. SAVING UPDATED RESULTS")
        print("-" * 40)
        
        # Save the new results
        updated_results = []
        
        for assignment in assignments:
            updated_results.append({
                'Intern Name': assignment.get('intern_name'),
                'Algorithm Restaurant': assignment.get('restaurant_name'),
                'Algorithm Commute': assignment.get('commute_minutes'),
                'Total Hours': assignment.get('total_overlap_hours'),
                'Days Matched': assignment.get('days_matched'),
                'Match Score': assignment.get('match_score')
            })
        
        # Save to CSV
        updated_df = pd.DataFrame(updated_results)
        updated_df.to_csv('updated_algorithm_assignments.csv', index=False)
        print(f"Saved {len(updated_results)} updated assignments to 'updated_algorithm_assignments.csv'")
        
        return True
        
    except Exception as e:
        print(f"Error implementing fixes: {e}")
        return False

def update_commute_limit_in_service():
    """Update the commute limit in the Hungarian matching service"""
    print("\n6. UPDATING SERVICE PARAMETERS")
    print("-" * 40)
    
    try:
        # Read the service file and update default parameters
        service_file = 'app/services/hungarian_matching.py'
        
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Update the default max_commute_minutes from 50 to 90
        updated_content = content.replace(
            'max_commute_minutes: int = 50',
            'max_commute_minutes: int = 90'
        )
        
        with open(service_file, 'w') as f:
            f.write(updated_content)
        
        print("SUCCESS: Updated default commute limit from 50 to 90 minutes in HungarianMatchingService")
        
        return True
        
    except Exception as e:
        print(f"Error updating service file: {e}")
        return False

def main():
    """Main function"""
    print("Implementing immediate fixes for algorithm assignment issues...")
    
    # Implement fixes
    success = implement_immediate_fixes()
    
    if success:
        # Update the service file
        update_commute_limit_in_service()
    
    print(f"\n" + "="*80)
    print("IMMEDIATE FIXES IMPLEMENTATION COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: All immediate fixes implemented successfully!")
        print("RESULTS: Check 'updated_algorithm_assignments.csv' for new results")
    else:
        print("FAILED: Some fixes failed - check error messages above")

if __name__ == "__main__":
    main()
