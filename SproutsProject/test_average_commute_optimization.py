#!/usr/bin/env python3
"""
Test average commute optimization vs original Hungarian algorithm
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_average_commute_optimization():
    """Test average commute optimization"""
    print("=== TESTING AVERAGE COMMUTE OPTIMIZATION ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.average_commute_matching import AverageCommuteMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Testing with {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Test original Hungarian algorithm
        print(f"\n--- ORIGINAL HUNGARIAN ALGORITHM ---")
        original_service = HungarianMatchingService()
        original_results = original_service.find_optimal_assignments(interns, restaurants)
        
        original_assignments = original_results.get('assignments', [])
        if original_assignments:
            original_avg_commute = sum(a['commute_minutes'] for a in original_assignments) / len(original_assignments)
            original_max_commute = max(a['commute_minutes'] for a in original_assignments)
            original_min_commute = min(a['commute_minutes'] for a in original_assignments)
            
            print(f"Original algorithm:")
            print(f"  Matched: {len(original_assignments)} interns")
            print(f"  Average commute: {original_avg_commute:.1f} minutes")
            print(f"  Commute range: {original_min_commute}-{original_max_commute} minutes")
        
        # Test average commute optimization
        print(f"\n--- AVERAGE COMMUTE OPTIMIZATION ---")
        avg_service = AverageCommuteMatchingService()
        
        # Test with different max commute constraints
        max_commute_options = [30, 35, 40, 45]
        
        for max_commute in max_commute_options:
            print(f"\nMax commute constraint: {max_commute} minutes")
            
            avg_results = avg_service.find_optimal_assignments_avg_commute(interns, restaurants, max_commute)
            
            avg_assignments = avg_results.get('assignments', [])
            if avg_assignments:
                avg_commute = avg_results.get('average_commute', 0)
                max_commute_result = avg_results.get('max_commute', 0)
                min_commute = avg_results.get('min_commute', 0)
                
                print(f"  Matched: {len(avg_assignments)} interns")
                print(f"  Average commute: {avg_commute:.1f} minutes")
                print(f"  Commute range: {min_commute}-{max_commute_result} minutes")
                
                # Compare with original
                if original_assignments:
                    improvement = original_avg_commute - avg_commute
                    print(f"  Improvement vs original: {improvement:.1f} minutes")
                    
                    if improvement > 0:
                        print(f"  ✓ BETTER average commute by {improvement:.1f} minutes")
                    else:
                        print(f"  ✗ Worse average commute by {abs(improvement):.1f} minutes")
        
        # Show best result
        print(f"\n=== RECOMMENDATION ===")
        
        # Test all options and find best
        best_result = None
        best_avg_commute = float('inf')
        
        for max_commute in max_commute_options:
            avg_results = avg_service.find_optimal_assignments_avg_commute(interns, restaurants, max_commute)
            avg_commute = avg_results.get('average_commute', float('inf'))
            
            if avg_commute < best_avg_commute and len(avg_results.get('assignments', [])) > 0:
                best_avg_commute = avg_commute
                best_result = avg_results
        
        if best_result:
            print(f"Best configuration:")
            print(f"  Max commute: {best_result.get('max_commute_constraint')} minutes")
            print(f"  Average commute: {best_result.get('average_commute', 0):.1f} minutes")
            print(f"  Matched interns: {len(best_result.get('assignments', []))}")
            
            if original_assignments:
                improvement = original_avg_commute - best_result.get('average_commute', 0)
                print(f"  Improvement over original: {improvement:.1f} minutes")
        
        # Show detailed comparison for best result
        if best_result:
            print(f"\n=== DETAILED COMPARISON ===")
            print(f"Original algorithm average: {original_avg_commute:.1f} minutes")
            print(f"Best average optimization: {best_result.get('average_commute', 0):.1f} minutes")
            
            improvement = original_avg_commute - best_result.get('average_commute', 0)
            if improvement > 0:
                print(f"✅ Average commute optimization IMPROVES average by {improvement:.1f} minutes")
            else:
                print(f"❌ Average commute optimization is WORSE by {abs(improvement):.1f} minutes")
        
        return best_result
        
    except Exception as e:
        print(f"Error testing average commute optimization: {e}")
        return None

def show_comparison_details():
    """Show detailed comparison between algorithms"""
    print("\n=== DETAILED ALGORITHM COMPARISON ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.average_commute_matching import AverageCommuteMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        # Get results from both algorithms
        original_service = HungarianMatchingService()
        original_results = original_service.find_optimal_assignments(interns, restaurants)
        
        avg_service = AverageCommuteMatchingService()
        avg_results = avg_service.find_optimal_assignments_avg_commute(interns, restaurants, 35)
        
        original_assignments = original_results.get('assignments', [])
        avg_assignments = avg_results.get('assignments', [])
        
        # Create comparison
        print(f"{'Intern':<25} {'Original':<20} {'Avg Opt':<20} {'Difference':<10}")
        print("-" * 75)
        
        # Create lookup for average assignments
        avg_lookup = {a['intern_name']: a for a in avg_assignments}
        
        for orig_assignment in original_assignments[:10]:  # Show first 10
            intern_name = orig_assignment['intern_name']
            orig_commute = orig_assignment['commute_minutes']
            orig_restaurant = orig_assignment['restaurant_name']
            
            if intern_name in avg_lookup:
                avg_assignment = avg_lookup[intern_name]
                avg_commute = avg_assignment['commute_minutes']
                avg_restaurant = avg_assignment['restaurant_name']
                difference = orig_commute - avg_commute
                
                print(f"{intern_name:<25} {orig_commute:<20} {avg_commute:<20} {difference:+.1f}")
            else:
                print(f"{intern_name:<25} {orig_commute:<20} {'No match':<20} {'N/A':<10}")
        
    except Exception as e:
        print(f"Error showing comparison details: {e}")

if __name__ == "__main__":
    best_result = test_average_commute_optimization()
    show_comparison_details()
    
    print(f"\n=== AVERAGE COMMUTE OPTIMIZATION TEST COMPLETE ===")
    
    if best_result:
        print(f"\n✅ Average commute optimization successfully implemented!")
        print(f"Recommendation: Use max_commute={best_result.get('max_commute_constraint')} for best results")
    else:
        print(f"\n❌ Average commute optimization needs refinement")
