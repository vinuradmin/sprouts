#!/usr/bin/env python3
"""
Find the row with Ollie O'Malley
"""

def find_ollie_row():
    """Find the row with Ollie O'Malley"""
    print("=== FINDING OLLIE O'MALLEY ROW ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            lines = file.readlines()
            
            for i, line in enumerate(lines, 1):
                if 'Ollie' in line or 'OMalley' in line:
                    print(f"Line {i}: {repr(line)}")
                    print(f"Line {i}: {line}")
                    print()
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_ollie_row()
