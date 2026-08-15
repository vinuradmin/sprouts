#!/usr/bin/env python3
<arg_value>Check if Hungarian algorithm is using transportation optimization
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_hungarian_integration():
    """Check if Hungarian algorithm is using transportation optimization"""
    print("=== CHECKING HUNGARIAN INTEGRATION ===")
    
    try:
        # Read the Hungarian matching service
        with open('app/services/hungarian_matching.py', 'r') as f:
            content = f.read()
        
        print("Checking if TransportationOptimizer is imported...")
        if 'from app.services.transportation_optimizer import TransportationOptimizer' in content:
            print("✅ TransportationOptimizer is imported")
        else:
            print("❌ TransportationOptimizer is NOT imported")
        
        print("\nChecking if TransportationOptimizer is used in _find_valid_pairs...")
        if 'TransportationOptimizer()' in content:
            print("✅ TransportationOptimizer is being used")
        else:
            print("❌ TransportationOptimizer is NOT being used")
        
        print("\nChecking commute calculation section...")
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'get_optimal_commute' in line:
                print(f"✅ Found get_optimal_commute at line {i+1}: {line.strip()}")
            elif 'commute_minutes = optimal_commute' in line:
                print(f"✅ Found commute_minutes = optimal_commute at line {i+1}: {line.strip()}")
            elif 'commute.minutes' in line and 'optimal_commute' not in line:
                print(f"⚠️  Found old commute calculation at line {i+1}: {line.strip()}")
        
        print("\n=== CURRENT IMPLEMENTATION STATUS ===")
        
        # Show the relevant section
        print("Current commute calculation section:")
        print("Lines 215-235 should contain the new implementation")
        
        for i in range(214, 236):
            if i < len(lines):
                print(f"Line {i+1}: {lines[i]}")
        
    except Exception as e:
        print(f"Error checking Hungarian integration: {e}")

def check_transportation_optimizer_usage():
    """Check if transportation optimizer is being used correctly"""
    print("\n=== CHECKING TRANSPORTATION OPTIMIZER USAGE ===")
    
    try:
        # Test if the Hungarian algorithm actually uses the optimizer
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Testing with {len(interns)} interns and {len(restaurants)} restaurants")
        
        # Run the algorithm
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Found {len(assignments)} assignments")
        
        if assignments:
            # Check if Angel Ruiz got the expected improvement
            angel_assignment = None
            for assignment in assignments:
                if 'Angel' in assignment['intern_name']:
                    angel_assignment = assignment
                    break
            
            if angel_assignment:
                print(f"\nAngel Ruiz assignment:")
                print(f"  Restaurant: {angel_assignment['restaurant_name']}")
                print(f"  Commute: {angel_assignment['commute_minutes']} minutes")
                print(f"  Expected: ~17 minutes (from previous test)")
                print(f"  Status: {'IMPROVED' if angel_assignment['commute_minutes'] < 30 else 'NO CHANGE'}")
            
            # Calculate statistics
            commutes = [a['commute_minutes'] for a in assignments]
            avg_commute = sum(commutes) / len(commutes)
            
            print(f"\nCurrent average commute: {avg_commute:.1f} minutes")
            print(f"Expected average: ~25 minutes")
            print(f"Status: {'IMPROVED' if avg_commute < 30 else 'NO CHANGE'}")
        
        # Test the transportation optimizer directly
        print(f"\n=== TESTING TRANSPORTATION OPTIMIZER DIRECTLY ===")
        
        from app.services.transportation_optimizer import TransportationOptimizer
        
        optimizer = TransportationOptimizer()
        
        # Test with Angel Ruiz
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        angel_ruiz = None
        for intern in interns:
            if 'Angel' in intern.user.full_name:
                angel_ruiz = intern
                break
        
        if angel_ruiz:
            restaurants = Restaurant.query.all()
            for restaurant in restaurants:
                if 'alaMar' in restaurant.name:
                    print(f"\nDirect test with Angel Ruiz -> {restaurant.name}")
                    
                    optimal_commute = optimizer.get_optimal_commute(
                        angel_ruiz.get_full_address(),
                        restaurant.get_full_address(),
                        angel_ruiz.transportation_method
                    )
                    
                    print(f"Direct optimal commute: {optimal_commute} minutes")
                    print(f"Expected: ~20 minutes")
                    print(f"Status: {'WORKING' if optimal_commute and optimal_commute > 0 else 'NOT WORKING'}")
                    break
        
    except Exception as e:
        print(f"Error checking transportation optimizer usage: {e}")

def show_integration_status():
    """Show integration status"""
    print("\n=== INTEGRATION STATUS ===")
    
    print("CURRENT STATUS:")
    print("TransportationOptimizer class created")
    print("HungarianMatchingService updated")
    print("Integration test passing")
    print("Commute times still showing 0 minutes")
    print("Average commute unchanged (33.9 minutes)")
    
    print("\nISSUES IDENTIFIED:")
    print("1. TransportationOptimizer returns None (0 minutes filtered out)")
    print("2. Hungarian algorithm may not be using the optimizer")
    print("3. Cache key/address mismatch issues")
    print("4. Google Maps API may have issues")
    
    print("\nNEXT STEPS:")
    print("1. Verify Hungarian algorithm is using TransportationOptimizer")
    print("2. Debug why commute times are 0 minutes")
    print("3. Fix address formatting issues")
    print("4. Test with known working addresses")
    
    print("\nEXPECTED OUTCOME:")
    print("Once fixed:")
    print("- Average commute should drop significantly")
    print("- Angel Ruiz: 50 -> ~20 minutes")
    print("- Many interns should get better commutes")
    print("- System will use optimal transportation")

if __name__ == "__main__":
    check_hungarian_integration()
    check_transportation_optimizer_usage()
    show_integration_status()
    
    print(f"\n=== INTEGRATION CHECK COMPLETE ===")
    print("Need to verify Hungarian algorithm is actually using the optimizer")
