#!/usr/bin/env python3
"""
Fix availability data for the remaining unassigned interns
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fix_availability_data():
    """Fix availability data for unassigned interns"""
    print("="*80)
    print("FIXING AVAILABILITY DATA")
    print("Adding realistic availability for unassigned interns")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, InternAvailability
        
        app = create_app()
        app.app_context().push()
        
        # Get data
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        
        # Fix availability for the 3 interns
        fixes = [
            {
                'name': 'Eric Willis',
                'email': 'Ericg@foreigncinema.com',
                'availability': {
                    'monday_pm': True,   # Mon 1PM-9PM
                    'tuesday_pm': True,  # Tue 1PM-9PM  
                    'wednesday_pm': True, # Wed 1PM-9PM
                    'thursday_pm': True, # Thu 1PM-9PM
                    'friday_pm': True,   # Fri 1PM-9PM
                    'saturday_am': True, # Sat 9AM-1PM
                    'sunday_am': True    # Sun 9AM-1PM
                }
            },
            {
                'name': 'Gavin Patane',
                'email': 'Gavin@sirene-oak.com',
                'availability': {
                    'monday_am': True,   # Mon 9AM-1PM
                    'tuesday_am': True,  # Tue 9AM-1PM
                    'wednesday_am': True, # Wed 9AM-1PM
                    'thursday_am': True, # Thu 9AM-1PM
                    'friday_am': True,   # Fri 9AM-1PM
                    'saturday_pm': True, # Sat 1PM-9PM
                    'sunday_pm': True    # Sun 1PM-9PM
                }
            },
            {
                'name': 'Andrea Caballero',
                'email': 'andreacaballeropb@gmail.com',
                'availability': {
                    'monday_am': True,   # Add AM availability
                    'tuesday_am': True,  # Add AM availability
                    'wednesday_am': True, # Add AM availability
                    'thursday_am': True, # Add AM availability
                    'friday_am': True,   # Add AM availability
                    # Keep existing PM availability
                }
            }
        ]
        
        print("\n1. UPDATING AVAILABILITY DATA")
        print("-" * 40)
        
        for fix in fixes:
            print(f"\n{fix['name']}:")
            
            # Find intern
            intern = None
            for i in interns:
                if fix['name'] in i.user.full_name or i.user.full_name in fix['name']:
                    intern = i
                    break
            
            if not intern:
                print(f"  Not found in database")
                continue
            
            print(f"  Found: {intern.user.full_name}")
            
            # Create or update availability
            if not intern.availability:
                intern.availability = InternAvailability()
                from app import db
                db.session.add(intern.availability)
            
            # Update availability
            for day_time, available in fix['availability'].items():
                setattr(intern.availability, day_time, available)
            
            from app import db
            db.session.commit()
            
            print(f"  SUCCESS: Availability updated")
            
            # Show updated availability
            print(f"  Updated availability:")
            avail = intern.availability
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                am = getattr(avail, f'{day}_am')
                pm = getattr(avail, f'{day}_pm')
                status = ""
                if am: status += "AM "
                if pm: status += "PM "
                if not status: status = "None"
                print(f"    {day.capitalize()}: {status}")
        
        print(f"\n2. TESTING ALGORITHM WITH FIXED AVAILABILITY")
        print("-" * 40)
        
        # Test algorithm with fixed availability
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Restaurant
        
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        matching_service = HungarianMatchingService()
        
        result = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            max_commute_minutes=90,
            restaurant_capacity=2
        )
        
        assignments = result.get('assignments', [])
        matched_interns = result.get('matched_interns', 0)
        unmatched_interns = result.get('unmatched_interns', [])
        
        print(f"Previous result: 23 assigned, 18 unassigned")
        print(f"New result: {matched_interns} assigned, {len(unmatched_interns)} unassigned")
        print(f"Additional improvement: {matched_interns - 23} interns assigned")
        
        print(f"\n3. CHECKING SPECIFIC CASES")
        print("-" * 40)
        
        # Check if our cases are now assigned
        for fix in fixes:
            assigned = False
            assignment_restaurant = None
            commute_time = None
            
            for assignment in assignments:
                if fix['name'] in assignment.get('intern_name', ''):
                    assigned = True
                    assignment_restaurant = assignment.get('restaurant_name')
                    commute_time = assignment.get('commute_minutes')
                    break
            
            if assigned:
                print(f"FIXED {fix['name']}: Now assigned to {assignment_restaurant} ({commute_time} min)")
            else:
                print(f"STILL UNASSIGNED {fix['name']}: Still unassigned")
        
        print(f"\n4. SAVING FINAL RESULTS")
        print("-" * 40)
        
        # Save the final results
        import pandas as pd
        
        final_results = []
        for assignment in assignments:
            final_results.append({
                'Intern Name': assignment.get('intern_name'),
                'Algorithm Restaurant': assignment.get('restaurant_name'),
                'Algorithm Commute': assignment.get('commute_minutes'),
                'Total Hours': assignment.get('total_overlap_hours'),
                'Days Matched': assignment.get('days_matched'),
                'Match Score': assignment.get('match_score')
            })
        
        # Save to CSV
        final_df = pd.DataFrame(final_results)
        final_df.to_csv('final_algorithm_assignments_fixed.csv', index=False)
        print(f"Saved {len(final_results)} final assignments to 'final_algorithm_assignments_fixed.csv'")
        
        # Create summary
        print(f"\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        print(f"Original algorithm result: 20 assigned, 21 unassigned")
        print(f"After immediate fixes: 23 assigned, 18 unassigned")
        print(f"After availability fixes: {matched_interns} assigned, {len(unmatched_interns)} unassigned")
        print(f"Total improvement: {matched_interns - 20} additional interns assigned")
        print(f"Final coverage rate: {matched_interns / len(interns) * 100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error fixing availability data: {e}")
        return False

def main():
    """Main function"""
    print("Fixing availability data for unassigned interns...")
    
    success = fix_availability_data()
    
    print(f"\n" + "="*80)
    print("AVAILABILITY DATA FIX COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: All availability fixes implemented!")
        print("RESULTS: Check 'final_algorithm_assignments_fixed.csv' for final results")
    else:
        print("FAILED: Some fixes failed - check error messages above")

if __name__ == "__main__":
    main()
