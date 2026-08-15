#!/usr/bin/env python3
"""
Check line 14 specifically
"""

def check_line14():
    """Check line 14 of intern_to_restaurant.csv"""
    print("=== CHECKING LINE 14 ===")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            lines = file.readlines()
            
            if len(lines) >= 14:
                line14 = lines[13].strip()  # Line 14 (0-indexed)
                print(f"Line 14: {repr(line14)}")
                print(f"Line 14: {line14}")
            else:
                print(f"File only has {len(lines)} lines")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_line14()
