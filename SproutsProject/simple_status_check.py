#!/usr/bin/env python3
"""
Simple status check
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_status():
    """Check current status"""
    print("=== CURRENT STATUS CHECK ===")
    
    try:
        # Read the Hungarian matching service
        with open('app/services/hungarian_matching.py', 'r') as f:
            content = f.read()
        
        print("TransportationOptimizer import:")
        if 'from app.services.transportation_optimizer import TransportationOptimizer' in content:
            print("  FOUND - TransportationOptimizer is imported")
        else:
            print("  NOT FOUND - TransportationOptimizer not imported")
        
        print("\nTransportationOptimizer usage:")
        if 'TransportationOptimizer()' in content:
            print("  FOUND - TransportationOptimizer is being used")
        else:
            print("  NOT FOUND - TransportationOptimizer not being used")
        
        print("\nOld commute calculation:")
        if 'commute = self.commute_cache.get_commute(' in content:
            print("  FOUND - Old commute calculation still present")
        else:
            print("  NOT FOUND - Old commute calculation removed")
        
        print("\nNew commute calculation:")
        if 'optimal_commute = optimizer.get_optimal_commute' in content:
            print("  FOUND - New commute calculation present")
        else:
            print("  NOT FOUND - New commute calculation not found")
        
        print("\n=== ANALYSIS ===")
        
        has_import = 'from app.services.transportation_optimizer import TransportationOptimizer' in content
        has_usage = 'TransportationOptimizer()' in content
        has_old = 'commute = self.commute_cache.get_commute(' in content
        has_new = 'optimal_commute = optimizer.get_optimal_commute' in content
        
        if has_import and has_usage and has_new and not has_old:
            print("STATUS: CORRECTLY IMPLEMENTED")
            print("Transportation optimization should be working")
        elif has_import and has_usage and has_old:
            print("STATUS: PARTIALLY IMPLEMENTED")
            print("Both old and new commute calculations present")
            print("This could cause issues")
        elif has_import and not has_usage:
            print("STATUS: IMPORTED BUT NOT USED")
            print("TransportationOptimizer imported but not used")
        else:
            print("STATUS: NOT IMPLEMENTED")
            print("Transportation optimization not implemented")
        
        # Test actual usage
        print("\n=== TESTING ACTUAL USAGE ===")
        
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Found {len(assignments)} assignments")
        
        if assignments:
            commutes = [a['commute_minutes'] for a in assignments]
            avg_commute = sum(commutes) / len(commutes)
            
            print(f"Average commute: {avg_commute:.1f} minutes")
            
            # Find Angel Ruiz
            angel_assignment = None
            for assignment in assignments:
                if 'Angel' in assignment['intern_name']:
                    angel_assignment = assignment
                    break
            
            if angel_assignment:
                print(f"Angel Ruiz commute: {angel_assignment['commute_minutes']} minutes")
                
                if angel_assignment['commute_minutes'] < 30:
                    print("Angel Ruiz: IMPROVED")
                else:
                    print("Angel Ruiz: NO CHANGE")
        
        print("\n=== CONCLUSION ===")
        
        if avg_commute < 30:
            print("RESULT: TRANSPORTATION OPTIMIZATION WORKING")
            print(f"Average commute improved to {avg_commute:.1f} minutes")
        else:
            print("RESULT: TRANSPORTATION OPTIMIZATION NOT WORKING")
            print(f"Average commute still {avg_commute:.1f} minutes")
            print("Need to debug further")
        
    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    check_status()
    print("\n=== STATUS CHECK COMPLETE ===")
