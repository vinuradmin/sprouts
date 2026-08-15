#!/usr/bin/env python3
"""
Find Ollie exactly as it appears in the CSV
"""
import csv

def find_ollie_exact():
    """Find Ollie exactly as it appears in the CSV"""
    print("=== FINDING OLLIE EXACTLY ===")
    
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                print(f"\nTrying encoding: {encoding}")
                
                with open('../intern_to_restaurant.csv', 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    
                    for i, row in enumerate(reader, 1):
                        intern_name = row.get('Intern Name', '')
                        
                        # Print the raw bytes to see what's there
                        if intern_name:
                            name_bytes = intern_name.encode('latin-1', errors='replace')
                            print(f"Line {i}: {repr(intern_name)} -> {repr(name_bytes)}")
                            
                            # Check for Ollie variations
                            if 'Ollie' in intern_name or 'ollie' in intern_name.lower():
                                print(f"  ^^^ FOUND OLLIE!")
                                
                                # Check for Snail Bar
                                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                                for day in days:
                                    day_matches = row.get(day, '').strip()
                                    if 'Snail Bar' in day_matches:
                                        print(f"    SNAIL BAR: {day} - {day_matches}")
                                print()
                                break
                        
                        # Check for empty lines that might be Ollie
                        if not intern_name.strip():
                            # Check if this line has Snail Bar
                            has_snail_bar = False
                            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            for day in days:
                                day_matches = row.get(day, '').strip()
                                if 'Snail Bar' in day_matches:
                                    has_snail_bar = True
                                    print(f"Line {i}: Empty name with Snail Bar in {day}")
                                    print(f"  {day}: {day_matches}")
                                    break
                            
                            if has_snail_bar:
                                print("  ^^^ This could be Ollie with empty name!")
                                print()
                        
                        # Stop after first 50 lines to avoid too much output
                        if i >= 50:
                            break
                            
                break
                
            except Exception as e:
                print(f"Encoding {encoding} failed: {e}")
                continue
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_ollie_exact()
