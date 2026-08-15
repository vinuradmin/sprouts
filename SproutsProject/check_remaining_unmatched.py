#!/usr/bin/env python3
"""
Check the remaining 4 unmatched interns in Intern Availabilities sheet
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_remaining_unmatched():
    """Check remaining unmatched interns in Intern Availabilities"""
    print("="*80)
    print("CHECKING REMAINING 4 UNMATCHED INTERNS")
    print("In Intern Availabilities sheet")
    print("="*80)
    
    try:
        # Load Intern Availabilities sheet
        avail_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv')
        
        # The 4 unmatched interns
        unmatched_interns = ['Alex', 'Andrea', 'Shelsea', 'Roni']
        
        print(f"Checking these interns in Intern Availabilities:")
        for intern_name in unmatched_interns:
            print(f"\n{'='*60}")
            print(f"Checking: '{intern_name}'")
            print(f"{'='*60}")
            
            found_matches = []
            
            for idx, row in avail_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                # Get name columns
                first_name = str(row.iloc[1]).strip()  # First Name column
                last_name = str(row.iloc[2]).strip()   # Last Name column
                full_name = f"{first_name} {last_name}".strip()
                
                # Check for matches
                match_found = False
                match_type = None
                
                # Exact first name match
                if intern_name.lower() == first_name.lower():
                    match_found = True
                    match_type = "First name match"
                
                # Exact full name match
                elif intern_name.lower() == full_name.lower():
                    match_found = True
                    match_type = "Full name match"
                
                # Partial match (intern name contained in full name)
                elif intern_name.lower() in full_name.lower():
                    match_found = True
                    match_type = "Partial match"
                
                # Full name contained in intern name (less likely)
                elif full_name.lower() in intern_name.lower():
                    match_found = True
                    match_type = "Reverse partial match"
                
                if match_found:
                    found_matches.append({
                        'row': idx,
                        'first_name': first_name,
                        'last_name': last_name,
                        'full_name': full_name,
                        'match_type': match_type,
                        'is_last': idx == len(avail_df) - 1
                    })
            
            if found_matches:
                print(f"FOUND {len(found_matches)} MATCHES:")
                for i, match in enumerate(found_matches):
                    last_indicator = " (LAST OCCURRENCE)" if match['is_last'] else ""
                    print(f"  {i+1}. Row {match['row']}: {match['full_name']}{last_indicator}")
                    print(f"     Type: {match['match_type']}")
                
                # Pick the last occurrence as requested
                last_match = found_matches[-1]
                print(f"\nSELECTED (last occurrence): {last_match['full_name']} at row {last_match['row']}")
                
            else:
                print(f"NO MATCHES FOUND for '{intern_name}'")
        
        # Now try to match these with database names
        print(f"\n" + "="*80)
        print("TRYING TO MATCH WITH DATABASE NAMES")
        print("="*80)
        
        # Get database names
        from app import create_app
        from app.models import Intern
        
        app = create_app()
        app.app_context().push()
        
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        database_names = [intern.user.full_name for intern in interns]
        
        print(f"Database intern names:")
        for i, name in enumerate(database_names):
            print(f"{i+1:2d}. '{name}'")
        
        # Try to match the unmatched interns using availabilities data
        for intern_name in unmatched_interns:
            print(f"\n--- Matching '{intern_name}' ---")
            
            # Find in availabilities
            avail_matches = []
            for idx, row in avail_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                
                first_name = str(row.iloc[1]).strip()
                last_name = str(row.iloc[2]).strip()
                full_name = f"{first_name} {last_name}".strip()
                
                if intern_name.lower() == first_name.lower():
                    avail_matches.append({
                        'full_name': full_name,
                        'row': idx,
                        'is_last': idx == len(avail_df) - 1
                    })
            
            if avail_matches:
                # Use last occurrence
                last_match = avail_matches[-1]
                avail_full_name = last_match['full_name']
                
                print(f"Availabilities: '{intern_name}' -> '{avail_full_name}'")
                
                # Try to match with database
                db_matches = []
                for db_name in database_names:
                    db_lower = db_name.lower()
                    avail_lower = avail_full_name.lower()
                    
                    # Check for various match types
                    if (avail_lower in db_lower or db_lower in avail_lower or
                        avail_lower.replace(' ', '') in db_lower.replace(' ', '') or
                        db_lower.replace(' ', '') in avail_lower.replace(' ', '')):
                        db_matches.append(db_name)
                
                if db_matches:
                    print(f"Database matches: {db_matches}")
                    # Pick the best match (first one for now)
                    best_match = db_matches[0]
                    print(f"Best match: '{best_match}'")
                else:
                    print(f"No database matches found for '{avail_full_name}'")
            else:
                print(f"No availabilities matches found for '{intern_name}'")
        
        return unmatched_interns
        
    except Exception as e:
        print(f"Error checking remaining unmatched: {e}")
        return []

def main():
    """Main function"""
    unmatched = check_remaining_unmatched()
    
    print(f"\n" + "="*80)
    print("REMAINING UNMATCHED CHECK COMPLETE")
    print("="*80)
    print(f"Checked {len(unmatched)} interns in Intern Availabilities")

if __name__ == "__main__":
    main()
