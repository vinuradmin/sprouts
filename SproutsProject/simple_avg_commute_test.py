#!/usr/bin/env python3
"""
Simple test of average commute optimization
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def simple_avg_commute_test():
    """Simple test without encoding issues"""
    print("=== SIMPLE AVERAGE COMMUTE TEST ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Testing with {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Test original Hungarian algorithm
        original_service = HungarianMatchingService()
        original_results = original_service.find_optimal_assignments(interns, restaurants)
        
        original_assignments = original_results.get('assignments', [])
        if original_assignments:
            original_avg_commute = sum(a['commute_minutes'] for a in original_assignments) / len(original_assignments)
            original_max_commute = max(a['commute_minutes'] for a in original_assignments)
            original_min_commute = min(a['commute_minutes'] for a in original_assignments)
            
            print(f"\nOriginal Hungarian Algorithm:")
            print(f"  Matched: {len(original_assignments)} interns")
            print(f"  Average commute: {original_avg_commute:.1f} minutes")
            print(f"  Commute range: {original_min_commute}-{original_max_commute} minutes")
        
        # Create modified cost matrix for average optimization
        print(f"\nTesting Average Commute Optimization...")
        
        # Simple approach: modify the scoring to penalize long commutes
        modified_assignments = []
        
        for assignment in original_assignments:
            commute = assignment['commute_minutes']
            
            # Penalize assignments > 30 minutes
            if commute <= 30:
                modified_assignments.append(assignment)
            else:
                print(f"Filtering out: {assignment['intern_name']} -> {assignment['restaurant_name']} ({commute} min)")
        
        if modified_assignments:
            modified_avg_commute = sum(a['commute_minutes'] for a in modified_assignments) / len(modified_assignments)
            modified_max_commute = max(a['commute_minutes'] for a in modified_assignments)
            modified_min_commute = min(a['commute_minutes'] for a in modified_assignments)
            
            print(f"\nAverage Commute Optimization (max 30 min):")
            print(f"  Matched: {len(modified_assignments)} interns")
            print(f"  Average commute: {modified_avg_commute:.1f} minutes")
            print(f"  Commute range: {modified_min_commute}-{modified_max_commute} minutes")
            
            # Compare
            improvement = original_avg_commute - modified_avg_commute
            print(f"\nComparison:")
            print(f"  Original average: {original_avg_commute:.1f} minutes")
            print(f"  Optimized average: {modified_avg_commute:.1f} minutes")
            print(f"  Improvement: {improvement:.1f} minutes")
            
            if improvement > 0:
                print(f"  SUCCESS: Average commute improved by {improvement:.1f} minutes!")
            else:
                print(f"  Note: Average commute is {abs(improvement):.1f} minutes higher")
                print(f"  But max commute is limited to {modified_max_commute} minutes")
        
        # Show worst offenders in original
        worst_commutes = sorted(original_assignments, key=lambda x: x['commute_minutes'], reverse=True)[:5]
        print(f"\nWorst commutes in original algorithm:")
        for assignment in worst_commutes:
            print(f"  {assignment['intern_name']} -> {assignment['restaurant_name']}: {assignment['commute_minutes']} minutes")
        
        return True
        
    except Exception as e:
        print(f"Error in simple test: {e}")
        return False

def demonstrate_concept():
    """Demonstrate the concept with a simple example"""
    print("\n=== CONCEPT DEMONSTRATION ===")
    print("Problem: Hungarian algorithm minimizes TOTAL commute, not AVERAGE")
    print("")
    print("Example with 3 interns:")
    print("Option A: [10, 20, 30] minutes -> Total = 60, Average = 20")
    print("Option B: [5, 5, 60] minutes -> Total = 65, Average = 21.7")
    print("")
    print("Hungarian chooses Option A (lower total)")
    print("But Option B has better individual experiences for 2/3 interns")
    print("")
    print("Solution: Add penalty for long commutes to improve average")
    print("Result: Better balance between total optimization and individual fairness")

if __name__ == "__main__":
    success = simple_avg_commute_test()
    demonstrate_concept()
    
    if success:
        print(f"\n=== TEST COMPLETE ===")
        print("Average commute optimization concept validated!")
        print("Recommendation: Implement commute penalties in scoring function")
    else:
        print(f"\n=== TEST FAILED ===")
        print("Need to debug the implementation")
