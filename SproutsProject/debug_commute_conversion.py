#!/usr/bin/env python3
"""
Debug commute conversion - why 46 mins becomes 45 mins
"""

def debug_commute_conversion():
    """Debug the commute time conversion"""
    print("="*80)
    print("DEBUGGING COMMUTE CONVERSION")
    print("Why 46 mins becomes 45 mins")
    print("="*80)
    
    # Test the conversion
    cached_value = 2752  # seconds from cache
    converted_minutes = cached_value // 60  # integer division
    
    print(f"Cached value: {cached_value} seconds")
    print(f"Converted with // 60: {converted_minutes} minutes")
    print(f"Actual minutes: {cached_value / 60:.2f} minutes")
    print(f"Rounded minutes: {round(cached_value / 60)} minutes")
    
    # Test different conversion methods
    print(f"\nTesting different conversion methods:")
    print(f"Integer division (//): {cached_value // 60}")
    print(f"Float division (/): {cached_value / 60:.2f}")
    print(f"Round: {round(cached_value / 60)}")
    print(f"Math floor: {int(cached_value / 60)}")
    print(f"Math ceil: {int(-cached_value // 60 * -1)}")
    
    # Check other cached values
    print(f"\nChecking other cached commute values:")
    test_values = [
        (1531, "26 mins"),
        (2769, "46 mins"), 
        (1091, "18 mins"),
        (2706, "45 mins"),
        (2420, "40 mins")
    ]
    
    for value, expected in test_values:
        converted = value // 60
        actual = value / 60
        print(f"  {value} seconds -> {converted} minutes (//60), actual: {actual:.1f}, expected: {expected}")

if __name__ == "__main__":
    debug_commute_conversion()
