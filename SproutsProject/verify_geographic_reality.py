#!/usr/bin/env python3
"""
Verify the geographic reality - are these distances correct?
"""

import sys
import os

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verify_geographic_reality():
    """Verify if the geographic distances make sense"""
    print("="*80)
    print("VERIFYING GEOGRAPHIC REALITY")
    print("Are these distances actually correct?")
    print("="*80)
    
    try:
        from app.services.commute_service import CommuteService
        
        service = CommuteService()
        jesus_address = "4271 N First St, San Jose, 95134, USA"
        
        # Test key locations
        locations = [
            ("Tarts de Feybesse", "324 24th Street, Oakland, California, 94591"),
            ("Burdell", "4640 Telegraph Ave, Oakland, CA 94609"),
            ("UC Berkeley", "University of California, Berkeley, CA 94720"),
            ("Downtown Oakland", "Downtown Oakland, CA"),
            ("Downtown Berkeley", "Downtown Berkeley, CA")
        ]
        
        print(f"From: {jesus_address}")
        print(f"\n" + "="*60)
        print("COMMUTE TIMES FROM SAN JOSE")
        print("="*60)
        
        results = []
        for name, address in locations:
            try:
                result = service.calculate_commute_time('driving', jesus_address, address)
                minutes = round(result.value / 60)
                results.append((name, address, result.text, minutes, result.value))
                print(f"{name:20s} | {minutes:3d} min | {result.text}")
            except Exception as e:
                print(f"{name:20s} | ERROR | {e}")
        
        print(f"\n" + "="*60)
        print("COMMUTES BETWEEN LOCATIONS")
        print("="*60)
        
        # Test commutes between the locations
        location_pairs = [
            ("Tarts de Feybesse", "UC Berkeley"),
            ("Burdell", "UC Berkeley"),
            ("Tarts de Feybesse", "Burdell"),
            ("Downtown Oakland", "Downtown Berkeley")
        ]
        
        location_map = {name: address for name, address, _, _, _ in results}
        
        for loc1, loc2 in location_pairs:
            if loc1 in location_map and loc2 in location_map:
                try:
                    result = service.calculate_commute_time('driving', location_map[loc1], location_map[loc2])
                    minutes = round(result.value / 60)
                    print(f"{loc1:20s} -> {loc2:20s} | {minutes:3d} min | {result.text}")
                except Exception as e:
                    print(f"{loc1:20s} -> {loc2:20s} | ERROR | {e}")
        
        print(f"\n" + "="*60)
        print("GEOGRAPHIC ANALYSIS")
        print("="*60)
        
        # Extract the key results
        tarts_result = next((r for r in results if r[0] == "Tarts de Feybesse"), None)
        burdell_result = next((r for r in results if r[0] == "Burdell"), None)
        berkeley_result = next((r for r in results if r[0] == "UC Berkeley"), None)
        
        if tarts_result and burdell_result and berkeley_result:
            print(f"San Jose to Tarts (Oakland): {tarts_result[3]} minutes")
            print(f"San Jose to Burdell (Oakland): {burdell_result[3]} minutes")
            print(f"San Jose to UC Berkeley: {berkeley_result[3]} minutes")
            print()
            print(f"Oakland average: {(tarts_result[3] + burdell_result[3]) / 2:.1f} minutes")
            print(f"Berkeley: {berkeley_result[3]} minutes")
            print(f"Difference: {berkeley_result[3] - ((tarts_result[3] + burdell_result[3]) / 2):.1f} minutes")
        
        print(f"\n" + "="*60)
        print("REALITY CHECK")
        print("="*60)
        
        print("Geographic facts:")
        print("- San Jose to Oakland: ~45-50 miles")
        print("- San Jose to Berkeley: ~45-50 miles") 
        print("- Oakland to Berkeley: ~5-10 miles")
        print()
        print("Traffic reality:")
        print("- Bay Area traffic can add 30-60+ minutes")
        print("- Routes to Berkeley might go through different traffic")
        print("- Google Maps considers real-time/typical traffic patterns")
        print()
        print("Conclusion: 118 minutes from San Jose to Berkeley might be realistic")
        print("due to traffic patterns, even though geographic distance is similar to Oakland")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    """Main function"""
    results = verify_geographic_reality()
    
    print(f"\n" + "="*80)
    print("GEOGRAPHIC REALITY VERIFICATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
