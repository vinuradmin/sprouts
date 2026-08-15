#!/usr/bin/env python3
"""
Debug why Ollie's Snail Bar match was missed in verification
"""

import csv

def debug_ollie_matching():
    """Debug the matching logic for Ollie"""
    print("=== DEBUGGING OLLIE MATCHING ISSUE ===")
    
    # Load original results
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            original_results = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Hungarian algorithm match
    hungarian_match = ("Ollie  OMalley", "Snail Bar")
    
    print(f"Hungarian match: {hungarian_match[0]} -> {hungarian_match[1]}")
    print()
    
    # Test the current matching logic
    print("=== CURRENT MATCHING LOGIC ===")
    
    for i, row in enumerate(original_results):
        original_intern = row.get('Intern Name', '').strip()
        
        # Skip problematic character printing
        if '\x92' in original_intern:
            print(f"Line {i+1}: Contains special character (Ollie with apostrophe)")
            print(f"  Hungarian name in original: {hungarian_match[0] in original_intern}")
            print(f"  Original in Hungarian: {original_intern in hungarian_match[0]}")
            
            # Check for Snail Bar
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            restaurant_found = False
            
            for day in days:
                day_matches = row.get(day, '').strip()
                if 'Snail Bar' in day_matches:
                    restaurant_found = True
                    print(f"    SNAIL BAR FOUND: {day}")
                    print(f"    {day_matches}")
            
            if not restaurant_found:
                print(f"    No Snail Bar found")
            
            print()
            break
        else:
            print(f"Checking: '{original_intern}'")
            print(f"  Contains 'Ollie': {'Ollie' in original_intern}")
            print(f"  Contains 'OMalley': {'OMalley' in original_intern}")
            print(f"  Contains 'Ollie' (case-insensitive): {'ollie' in original_intern.lower()}")
            print(f"  Hungarian name in original: {hungarian_match[0] in original_intern}")
            print(f"  Original in Hungarian: {original_intern in hungarian_match[0]}")
            print()
    
    # Test different matching approaches
    print("=== TESTING DIFFERENT MATCHING APPROACHES ===")
    
    ollie_variations = [
        "Ollie  OMalley",
        "Ollie O'Malley", 
        "Ollie  O'Malley",
        "Ollie O\x92Malley"
    ]
    
    for variation in ollie_variations:
        print(f"Testing: '{variation}'")
        print(f"  Contains 'Ollie': {'Ollie' in variation}")
        print(f"  Contains 'Ollie' (case-insensitive): {'ollie' in variation.lower()}")
        print(f"  Hungarian match contains: {hungarian_match[0] in variation}")
        print(f"  Variation contains Hungarian: {variation in hungarian_match[0]}")
        print()

if __name__ == "__main__":
    debug_ollie_matching()
