"""
Diagnose the actual structure of the Chef Availabilities sheet
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import read_sheet_data

def diagnose_sheets():
    """Check the actual structure of both sheets"""
    
    print("=" * 80)
    print("DIAGNOSING GOOGLE SHEETS STRUCTURE")
    print("=" * 80)
    print()
    
    # Check Intern sheet
    print("1. INTERN AVAILABILITIES SHEET:")
    intern_data = read_sheet_data('Intern Availabilities')
    print(f"   Total rows: {len(intern_data)}")
    print(f"   First row (headers): {len(intern_data[0])} columns")
    print(f"   First 10 headers:")
    for i, header in enumerate(intern_data[0][:10]):
        print(f"     {i}: '{header}'")
    print()
    
    # Check Chef sheet
    print("2. CHEF AVAILABILITIES SHEET:")
    chef_data = read_sheet_data('Chef Availabilities')
    print(f"   Total rows: {len(chef_data)}")
    if chef_data:
        print(f"   First row: {len(chef_data[0])} columns")
        print(f"   First row content: {chef_data[0]}")
        print()
        
        if len(chef_data) > 1:
            print(f"   Second row: {len(chef_data[1])} columns")
            print(f"   Second row content: {chef_data[1][:10]}")
            print()
        
        if len(chef_data) > 2:
            print(f"   Third row: {len(chef_data[2])} columns")
            print(f"   Third row content: {chef_data[2][:10]}")
            print()
        
        # Look for actual header row
        print("   Searching for header row (looking for 'Restaurant Name'):")
        for i, row in enumerate(chef_data[:10]):
            for cell in row:
                if 'Restaurant Name' in str(cell):
                    print(f"     Found 'Restaurant Name' in row {i}")
                    print(f"     Row {i} content: {row}")
                    break
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    diagnose_sheets()
