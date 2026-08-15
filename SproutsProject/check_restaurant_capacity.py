#!/usr/bin/env python3
"""
Check if restaurant capacity limit is being enforced
"""

from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def check_restaurant_capacity():
    """Check restaurant capacity enforcement"""
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print("=== CHECKING RESTAURANT CAPACITY ENFORCEMENT ===")
    print(f"Current restaurant_capacity: {service.restaurant_capacity}")
    
    # Run algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    assignments = matches.get('assignments', [])
    
    print(f"\nTotal matches: {len(assignments)}")
    
    # Count interns per restaurant
    restaurant_counts = {}
    for assignment in assignments:
        restaurant_name = assignment.get('restaurant_name', 'Unknown')
        intern_name = assignment.get('intern_name', 'Unknown')
        
        if restaurant_name not in restaurant_counts:
            restaurant_counts[restaurant_name] = []
        restaurant_counts[restaurant_name].append(intern_name)
    
    print(f"\nInterns per restaurant:")
    for restaurant, intern_list in restaurant_counts.items():
        count = len(intern_list)
        status = "OK" if count <= service.restaurant_capacity else "OVER LIMIT"
        print(f"  {restaurant}: {count} interns ({status})")
        for intern in intern_list:
            print(f"    - {intern}")
    
    # Check if any restaurants exceed capacity
    over_capacity = {r: interns for r, interns in restaurant_counts.items() if len(interns) > service.restaurant_capacity}
    
    if over_capacity:
        print(f"\nRESTAURANTS OVER CAPACITY:")
        for restaurant, interns in over_capacity.items():
            print(f"  {restaurant}: {len(interns)} interns (limit: {service.restaurant_capacity})")
    else:
        print(f"\nAll restaurants within capacity limit ({service.restaurant_capacity} interns max)")
    
    # Check total capacity utilization
    total_capacity = len(restaurants) * service.restaurant_capacity
    utilized_capacity = len(assignments)
    utilization = (utilized_capacity / total_capacity * 100) if total_capacity > 0 else 0
    
    print(f"\nCapacity Analysis:")
    print(f"  Total restaurants: {len(restaurants)}")
    print(f"  Capacity per restaurant: {service.restaurant_capacity}")
    print(f"  Total capacity: {total_capacity}")
    print(f"  Utilized capacity: {utilized_capacity}")
    print(f"  Utilization rate: {utilization:.1f}%")

if __name__ == "__main__":
    check_restaurant_capacity()
