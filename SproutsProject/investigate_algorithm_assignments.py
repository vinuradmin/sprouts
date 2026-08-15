#!/usr/bin/env python3
"""
Investigate why some interns don't have algorithm assignments
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def investigate_algorithm_assignments():
    """Investigate why algorithm didn't assign all interns"""
    print("="*80)
    print("INVESTIGATING ALGORITHM ASSIGNMENTS")
    print("Why some interns don't have algorithm assignments")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get all interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        print(f"Total interns seeking internship: {len(interns)}")
        print(f"Total active restaurants: {len(restaurants)}")
        
        # Check business rules
        print(f"\n" + "="*60)
        print("BUSINESS RULES ANALYSIS")
        print("="*60)
        
        # Maximum 2 interns per restaurant
        max_per_restaurant = 2
        total_available_slots = len(restaurants) * max_per_restaurant
        
        print(f"Maximum interns per restaurant: {max_per_restaurant}")
        print(f"Total available slots: {total_available_slots}")
        print(f"Total interns: {len(interns)}")
        
        if len(interns) > total_available_slots:
            print(f"WARNING: More interns ({len(interns)}) than available slots ({total_available_slots})")
            print(f"   {len(interns) - total_available_slots} interns will be unassigned")
        else:
            print(f"OK: Enough slots for all interns")
        
        # Run the algorithm to see what it actually assigns
        print(f"\n" + "="*60)
        print("RUNNING HUNGARIAN ALGORITHM")
        print("="*60)
        
        matching_service = HungarianMatchingService()
        
        # Create cost matrix
        cost_matrix = []
        intern_names = []
        restaurant_names = []
        
        for intern in interns:
            row = []
            intern_names.append(intern.user.full_name)
            
            for restaurant in restaurants:
                # Use a simple cost for now (you could use commute times)
                cost = 1  # Default cost
                row.append(cost)
            
            cost_matrix.append(row)
        
        restaurant_names = [r.name for r in restaurants]
        
        print(f"Cost matrix shape: {len(cost_matrix)} x {len(cost_matrix[0])}")
        
        # Run Hungarian algorithm using the service method
        try:
            # Use the actual matching service method
            result = matching_service.find_optimal_assignments(interns, restaurants)
            assignments = result.get('assignments', [])
            
            print(f"Algorithm generated {len(assignments)} assignments")
            print(f"Matched interns: {result.get('matched_interns', 0)}")
            print(f"Unmatched interns: {len(result.get('unmatched_interns', []))}")
            
            # Analyze assignments
            assigned_interns = set()
            restaurant_assignments = {}
            
            print(f"\nAssignment details:")
            for i, assignment in enumerate(assignments):
                print(f"  Assignment {i}: {type(assignment)} - {assignment}")
                
                # Handle different assignment formats
                if isinstance(assignment, dict):
                    if 'intern' in assignment and 'restaurant' in assignment:
                        intern_name = assignment['intern'].user.full_name
                        restaurant_name = assignment['restaurant'].name
                    elif 'intern_id' in assignment and 'restaurant_id' in assignment:
                        # Find intern and restaurant by ID
                        intern = next((i for i in interns if i.id == assignment['intern_id']), None)
                        restaurant = next((r for r in restaurants if r.id == assignment['restaurant_id']), None)
                        if intern and restaurant:
                            intern_name = intern.user.full_name
                            restaurant_name = restaurant.name
                        else:
                            continue
                    else:
                        print(f"    Unknown assignment format: {assignment.keys()}")
                        continue
                elif isinstance(assignment, (list, tuple)) and len(assignment) >= 2:
                    # Handle tuple/list format (intern, restaurant, ...)
                    intern_obj = assignment[0]
                    restaurant_obj = assignment[1]
                    
                    if hasattr(intern_obj, 'user') and hasattr(restaurant_obj, 'name'):
                        intern_name = intern_obj.user.full_name
                        restaurant_name = restaurant_obj.name
                    else:
                        print(f"    Invalid objects in assignment")
                        continue
                else:
                    print(f"    Unknown assignment type: {type(assignment)}")
                    continue
                
                assigned_interns.add(intern_name)
                
                if restaurant_name not in restaurant_assignments:
                    restaurant_assignments[restaurant_name] = []
                restaurant_assignments[restaurant_name].append(intern_name)
            
            # Check restaurant capacity
            print(f"\nRestaurant assignments:")
            for restaurant, assigned_interns_list in restaurant_assignments.items():
                count = len(assigned_interns_list)
                status = "OK" if count <= max_per_restaurant else "OVERCAPACITY"
                print(f"  {status} {restaurant}: {count} interns")
                if count > 0:
                    for intern_name in assigned_interns_list:
                        print(f"    - {intern_name}")
            
            # Get unmatched interns from result
            unmatched_interns = [u['name'] for u in result.get('unmatched_interns', [])]
            
            print(f"\nUnassigned interns ({len(unmatched_interns)}):")
            for intern_name in sorted(unmatched_interns):
                print(f"  - {intern_name}")
            
            return {
                'total_interns': len(interns),
                'total_restaurants': len(restaurants),
                'total_slots': total_available_slots,
                'assigned_count': len(assignments),
                'unassigned_count': len(unmatched_interns),
                'unassigned_interns': unmatched_interns,
                'restaurant_assignments': restaurant_assignments,
                'algorithm_result': result
            }
            
        except Exception as e:
            print(f"Error running Hungarian algorithm: {e}")
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def check_specific_unassigned_interns(unassigned_interns):
    """Check specific details about unassigned interns"""
    print("="*80)
    print("CHECKING UNASSIGNED INTERNS DETAILS")
    print("="*80)
    
    try:
        from app import create_app
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        for intern_name in unassigned_interns:
            print(f"\n{intern_name}:")
            
            # Find intern in database
            intern = None
            for i in Intern.query.filter_by(is_seeking_internship=True).all():
                if intern_name in i.user.full_name or i.user.full_name in intern_name:
                    intern = i
                    break
            
            if intern:
                print(f"  Full name: {intern.user.full_name}")
                print(f"  Email: {intern.user.email}")
                print(f"  Location: {intern.get_full_address()}")
                print(f"  Transportation: {intern.transportation_method}")
                print(f"  Age: {intern.age}")
                
                # Check if they have actual assignment from Excel
                try:
                    import pandas as pd
                    df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List', header=2)
                    
                    intern_row = df[df['Name'].str.contains(intern_name, na=False, case=False)]
                    if not intern_row.empty:
                        actual_restaurant = str(intern_row.iloc[0]['Restaurant']).strip()
                        print(f"  Actual assignment: {actual_restaurant}")
                    else:
                        print(f"  Actual assignment: Not found in Excel")
                except:
                    print(f"  Actual assignment: Error checking Excel")
            else:
                print(f"  Not found in database")
    
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    results = investigate_algorithm_assignments()
    
    if results and results['unassigned_interns']:
        print(f"\n" + "="*80)
        check_specific_unassigned_interns(results['unassigned_interns'])
    
    print(f"\n" + "="*80)
    print("ALGORITHM ASSIGNMENTS INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
