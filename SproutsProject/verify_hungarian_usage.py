#!/usr/bin/env python3
<arg_value>Verify if Hungarian algorithm is using transportation optimization
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verify_hungarian_usage():
    """Verify if Hungarian algorithm is using transportation optimization"""
    print("=== VERIFYING HUNGARIAN USAGE ===")
    
    try:
        # Read the Hungarian matching service
        with open('app/services/hungarian_matching.py', 'r') as f:
            content = f.read()
        
        print("Checking imports...")
        if 'from app.services.transportation_optimizer import TransportationOptimizer' in content:
            print("✅ TransportationOptimizer is imported")
        else:
            print("❌ TransportationOptimizer is NOT imported")
        
        print("\nChecking usage in _find_valid_pairs...")
        
        # Find the section with transportation optimization
        lines = content.split('\n')
        
        in_transport_section = False
        transport_lines = []
        
        for i, line in enumerate(lines):
            if 'TransportationOptimizer()' in line:
                in_transport_section = True
                transport_lines.append(f"Line {i+1}: {line.strip()}")
            elif in_transport_section:
                transport_lines.append(f"Line {i+1}: {line.strip()}")
            elif transport_lines and ('try:' in line or 'except' in line):
                transport_lines.append(f"Line {i+1}: {line.strip()}")
        
        print(f"Transportation optimization section ({len(transport_lines)} lines):")
        for line in transport_lines[:10]:  # Show first 10 lines
            print(f"  {line}")
        
        if len(transport_lines) > 10:
            print(f"  ... and {len(transport_lines) - 10} more lines")
        
        # Check if the old commute calculation is still there
        print(f"\nChecking for old commute calculation...")
        old_commute_lines = []
        
        for i, line in enumerate(lines):
            if 'commute = self.commute_cache.get_commute(' in line:
                old_commute_lines.append(f"Line {i+1}: {line.strip()}")
        
        if old_commute_lines:
            print(f"Found {len(old_commute_lines)} lines with old commute calculation:")
            for line in old_commute_lines[:5]:
                print(f"  {line}")
            if len(old_commute_lines) > 5:
                print(f"  ... and {len(old_commute_lines) - 5} more lines")
        else:
            print("No old commute calculation found")
        
        # Check for new commute calculation
        new_commute_lines = []
        
        for i, line in enumerate(lines):
            if 'optimal_commute = optimizer.get_optimal_commute' in line:
                new_commute_lines.append(f"Line {i+1}: {line.strip()}")
        
        if new_commute_lines:
            print(f"\nFound {len(new_commute_lines)} lines with new commute calculation:")
            for line in new_commute_lines:
                print(f"  {line}")
        else:
            print("\nNo new commute calculation found")
        
        print(f"\n=== ANALYSIS ===")
        
        if len(transport_lines) > 0 and len(new_commute_lines) > 0:
            print("✅ Transportation optimization is implemented")
            print("✅ Hungarian algorithm should use optimal commute")
        elif len(transport_lines) > 0 and len(new_commute_lines) == 0:
            print("⚠️  Transportation optimization imported but not used")
            print("   Hungarian algorithm still uses old commute calculation")
        else:
            print("❌ Transportation optimization not implemented")
        
        # Check if the old commute calculation is still being used
        if len(old_commute_lines) > 0:
            print("⚠️  Old commute calculation still present")
            print("   This explains why average commute unchanged")
        
        print(f"\n=== RECOMMENDATION ===")
        
        if len(old_commute_lines) > 0:
            print("ISSUE: Old commute calculation is still being used")
            print("FIX: Remove old commute calculation code")
            print("      Ensure only new optimal commute calculation is used")
        
        if len(transport_lines) > 0 and len(new_commute_lines) == 0:
            print("ISSUE: Transportation optimization not being used")
            print("FIX: Check integration in _find_valid_pairs method")
        
        if len(transport_lines) == 0 and len(new_commute_lines) == 0:
            print("ISSUE: Transportation optimization not implemented")
            print("FIX: Implement transportation optimization")
        
    except Exception as e:
        print(f"Error verifying Hungarian usage: {e}")

def test_actual_usage():
    """Test actual usage"""
    print("\n=== TESTING ACTUAL USAGE ===")
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Testing with {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Test a specific case
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            print(f"\nTesting Angel Ruiz case:")
            print(f"Transportation: {angel_ruiz.transportation_method}")
            
            # Test the optimizer directly
            from app.services.transportation_optimizer import TransportationOptimizer
            optimizer = TransportationOptimizer()
            
            restaurants = Restaurant.query.all()
            for restaurant in restaurants:
                if 'alaMar' in restaurant.name:
                    print(f"Restaurant: {restaurant.name}")
                    print(f"Address: {restaurant.get_full_address()}")
                    
                    # Test the optimizer
                    optimal_commute = optimizer.get_optimal_commute(
                        angel_ruiz.get_full_address(),
                        restaurant.get_full_address(),
                        angel_ruiz.transportation_method
                    )
                    
                    print(f"Direct optimal commute: {optimal_commute} minutes")
                    
                    # Test what Hungarian algorithm gives
                    match = service._evaluate_match(angel_ruiz, restaurant, 60, 12)
                    if match:
                        print(f"Hungarian commute: {match['commute_minutes']} minutes")
                    
                    break
        
        # Run the full algorithm
        print(f"\nRunning full Hungarian algorithm...")
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Found {len(assignments)} assignments")
        
        if assignments:
            # Check Angel Ruiz assignment
            angel_assignment = None
            for assignment in assignments:
                if 'Angel' in assignment['intern_name']:
                    angel_assignment = assignment
                    break
            
            if angel_assignment:
                print(f"\nAngel Ruiz assignment from Hungarian algorithm:")
                print(f"  Restaurant: {angel_assignment['restaurant_name']}")
                print(f"  Commute: {angel_assignment['commute_minutes']} minutes")
                print(f"  Expected: ~20 minutes (optimal)")
                print(f"  Status: {'IMPROVED' if angel_assignment['commute_minutes'] < 30 else 'NO CHANGE'}")
            
            # Calculate statistics
            commutes = [a['commute_minutes'] for a in assignments]
            avg_commute = sum(commutes) / len(commutes)
            
            print(f"\nCurrent average commute: {avg_commute:.1f} minutes")
            print(f"Expected average: ~25 minutes")
            print(f"Status: {'IMPROVED' if avg_commute < 30 else 'NO CHANGE'}")
        
        print(f"\n=== CONCLUSION ===")
        
        if angel_assignment and angel_assignment['commute_minutes'] < 30:
            print("✅ Angel Ruiz got improved commute!")
            print(f"  Angel Ruiz: {angel_assignment['commute_minutes']} minutes")
        else:
            print("❌ Angel Ruiz did not get improved commute")
        
        if avg_commute < 30:
            print("✅ Average commute improved!")
            print(f"  Current: {avg_commute:.1f} minutes")
        else:
            print("❌ Average commute unchanged")
        
    except Exception as e:
        print(f"Error testing actual usage: {e}")

if __name__ == "__main__":
    verify_hungarian_usage()
    test_actual_usage()
    
    print(f"\n=== VERIFICATION COMPLETE ===")
    print("This will show if the Hungarian algorithm is actually using the transportation optimization.")
