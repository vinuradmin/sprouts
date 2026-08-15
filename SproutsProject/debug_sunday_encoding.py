#!/usr/bin/env python3
"""
Debug Sunday encoding issues and find the exact bug location
"""

import csv
import re

def debug_sunday_encoding():
    """Debug Sunday encoding issues and find the bug"""
    print("=== DEBUGGING SUNDAY ENCODING AND BUG LOCATION ===")
    
    # First, let's read the CSV with proper encoding handling
    print("\n1. READING OLLIE'S SUNDAY WITH ENCODING FIX:")
    
    try:
        with open('../intern_to_restaurant.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                intern_name = row.get('Intern Name', '').strip()
                
                # Find Ollie (line 13 with special character)
                if i == 13:
                    print(f"Line {i}: {repr(intern_name)}")
                    
                    # Check Sunday specifically with encoding-safe printing
                    sunday_matches = row.get('Sunday', '').strip()
                    print(f"Sunday raw: {repr(sunday_matches)}")
                    
                    if sunday_matches:
                        print(f"Sunday length: {len(sunday_matches)}")
                        print(f"Sunday bytes: {sunday_matches.encode('latin-1', errors='replace')}")
                        
                        # Parse each restaurant option safely
                        lines = sunday_matches.split('\n')
                        print(f"Number of lines: {len(lines)}")
                        
                        for j, line in enumerate(lines):
                            line = line.strip()
                            if line:
                                print(f"Line {j+1}: {repr(line)}")
                                
                                # Parse restaurant option
                                match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                                if match:
                                    restaurant = match.group(1).strip()
                                    commute = match.group(2).strip()
                                    start = int(match.group(3))
                                    end = int(match.group(4))
                                    hours = end - start
                                    
                                    print(f"  -> Restaurant: {repr(restaurant)}")
                                    print(f"  -> Commute: {repr(commute)}")
                                    print(f"  -> Time: [{start}-{end}] ({hours} hrs)")
                                    
                                    # Check if this is Snail Bar
                                    if 'Snail Bar' in restaurant:
                                        print(f"    ^^^ SNAIL BAR FOUND!")
                                        print(f"    Sunday overlap: {hours} hours")
                                        print(f"    Time range: {start}-{end}")
                                else:
                                    print(f"  -> Failed to parse: {repr(line)}")
                    else:
                        print("No Sunday matches found")
                    
                    print()
                    break
                    
    except Exception as e:
        print(f"Error reading results CSV: {e}")
    
    # Now let's examine the original algorithm code to find the bug
    print("\n2. EXAMINING ORIGINAL ALGORITHM CODE:")
    
    # Look for the original algorithm files
    import os
    current_dir = os.getcwd()
    
    # Find Python files that might contain the original algorithm
    python_files = []
    for file in os.listdir(current_dir):
        if file.endswith('.py') and any(keyword in file.lower() for keyword in ['match', 'algorithm', 'original', 'overlap']):
            python_files.append(file)
    
    print(f"Found relevant files: {python_files}")
    
    # Look for the main algorithm file
    algorithm_files = []
    for file in os.listdir(current_dir):
        if file.endswith('.py'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(keyword in content for keyword in ['overlap', 'hours', 'minimum', '12', '4']):
                        algorithm_files.append(file)
            except:
                pass
    
    print(f"Files with overlap logic: {algorithm_files}")
    
    # Search for the specific bug in overlap calculation
    print("\n3. SEARCHING FOR OVERLAP CALCULATION BUG:")
    
    bug_patterns = [
        r'duration.*\+.*duration',  # Adding durations
        r'overlap.*\+.*overlap',    # Adding overlaps
        r'\.duration\(\)',          # Duration calculations
        r'get_overlap',             # Overlap function calls
        r'12.*hours',               # 12-hour requirement
        r'4.*hours',                # 4-hour requirement
    ]
    
    for file in algorithm_files[:3]:  # Check first 3 files
        print(f"\nChecking {file}:")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines):
                    for pattern in bug_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            print(f"  Line {i+1}: {line.strip()}")
                            break
        except Exception as e:
            print(f"  Error reading {file}: {e}")

if __name__ == "__main__":
    debug_sunday_encoding()
