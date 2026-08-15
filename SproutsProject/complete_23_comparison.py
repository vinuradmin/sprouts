#!/usr/bin/env python3
"""
Complete 23 intern comparison with Intern Availabilities cross-reference
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def complete_23_comparison():
    """Complete comparison for all 23 interns using Intern Availabilities"""
    print("="*80)
    print("COMPLETE 23 INTERN COMPARISON")
    print("With Intern Availabilities cross-reference")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Load Intern Availabilities sheet
        avail_df = pd.read_csv('C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv')
        
        # Get algorithm assignments
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
        
        # Extract actual assignments
        actual_assignments = []
        for idx, row in fall_2025_df.iterrows():
            name_col = row.iloc[1]  # Name column
            restaurant_col = row.iloc[14]  # Column 15 (index 14)
            
            if pd.notna(name_col) and str(name_col).strip() != 'nan':
                actual_name = str(name_col).strip()
                actual_restaurant = str(restaurant_col).strip() if pd.notna(restaurant_col) else 'Unassigned'
                
                if actual_restaurant == 'nan' or actual_restaurant == '':
                    actual_restaurant = 'Unassigned'
                
                actual_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'row_number': idx + 338
                })
        
        # Filter to only assigned interns
        assigned_interns = [a for a in actual_assignments if a['actual_restaurant'] != 'Unassigned']
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Create availabilities lookup
        avail_lookup = {}
        for idx, row in avail_df.iterrows():
            if idx == 0:  # Skip header
                continue
            
            first_name = str(row.iloc[1]).strip()
            last_name = str(row.iloc[2]).strip()
            full_name = f"{first_name} {last_name}".strip()
            
            # Store all occurrences, but we'll use the last one
            if first_name not in avail_lookup:
                avail_lookup[first_name] = []
            avail_lookup[first_name].append({
                'full_name': full_name,
                'row': idx,
                'is_last': idx == len(avail_df) - 1
            })
        
        # Complete matching process
        matched_assignments = []
        unmatched_assignments = []
        
        print(f"Complete matching process for {len(assigned_interns)} interns:")
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            matched_assignment = None
            match_method = None
            
            # Strategy 1: Exact match
            if actual_name in algorithm_lookup:
                matched_assignment = algorithm_lookup[actual_name]
                match_method = 'Exact match'
            
            # Strategy 2: First name match
            elif not matched_assignment:
                actual_first = actual_name.strip().split()[0].lower()
                
                # Special case mappings
                special_mappings = {
                    'Gylli': 'Gyllibhet  Palacio',
                    'Nae': 'Eljanae Robinson',
                    'maye': 'Yeimi Diaz ',
                    'Gio': 'Giovanni Giacomazzi',
                    'JP': 'Samuel  Gonzalez ',
                    'Dana': 'Catherine Oropeza Huerta',
                    'Bosco Liu': 'Zhijian Liu',
                    'Noel': 'Aliyatt  Rodgers',
                    'Alexis/bri': 'Zailea Daniels',
                    'Ivory Willows': 'Aaliyah Engram'
                }
                
                # Try special mapping first
                if actual_name in special_mappings:
                    mapped_name = special_mappings[actual_name]
                    if mapped_name in algorithm_lookup:
                        matched_assignment = algorithm_lookup[mapped_name]
                        match_method = f'Special mapping ({actual_name} -> {mapped_name})'
                
                # Try first name match
                if not matched_assignment:
                    for algo_name in algorithm_lookup:
                        algo_first = algo_name.strip().split()[0].lower()
                        if actual_first == algo_first:
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = f'First name match ({actual_name} -> {algo_name})'
                            break
            
            # Strategy 3: Intern Availabilities cross-reference
            if not matched_assignment and actual_name in avail_lookup:
                avail_matches = avail_lookup[actual_name]
                if avail_matches:
                    # Use last occurrence
                    last_match = avail_matches[-1]
                    avail_full_name = last_match['full_name']
                    
                    # Try to match with database
                    for algo_name in algorithm_lookup:
                        algo_lower = algo_name.lower()
                        avail_lower = avail_full_name.lower()
                        
                        if (avail_lower in algo_lower or algo_lower in avail_lower or
                            avail_lower.replace(' ', '') in algo_lower.replace(' ', '') or
                            algo_lower.replace(' ', '') in avail_lower.replace(' ', '')):
                            matched_assignment = algorithm_lookup[algo_name]
                            match_method = f'Availabilities cross-ref ({actual_name} -> {avail_full_name} -> {algo_name})'
                            break
            
            if matched_assignment:
                matched_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_name': matched_assignment['intern_name'],
                    'algorithm_restaurant': matched_assignment['restaurant_name'],
                    'algorithm_commute': matched_assignment['commute_minutes'],
                    'match_method': match_method
                })
                
                print(f"MATCH: {actual_name} -> {matched_assignment['intern_name']} -> {matched_assignment['restaurant_name']} ({matched_assignment['commute_minutes']} min)")
            else:
                unmatched_assignments.append(actual)
                print(f"NO MATCH: {actual_name} -> {actual_restaurant}")
        
        print(f"\nFINAL RESULTS:")
        print(f"Matched: {len(matched_assignments)}")
        print(f"Unmatched: {len(unmatched_assignments)}")
        print(f"Match Rate: {len(matched_assignments)/len(assigned_interns)*100:.1f}%")
        
        # Create final comparison data
        comparison_data = [
            ['Complete Fall 2025 vs Algorithm Comparison - All 23 Interns'],
            [''],
            ['KEY METRICS'],
            ['Total Assigned Interns', len(assigned_interns)],
            ['Successfully Matched', len(matched_assignments)],
            ['Unmatched', len(unmatched_assignments)],
            ['Match Rate', f'{len(matched_assignments)/len(assigned_interns)*100:.1f}%'],
            [''],
            ['PERFECT MATCHES (Current placements are optimal)'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)']
        ]
        
        # Add perfect matches
        perfect_matches = []
        different_matches = []
        
        for match in matched_assignments:
            if match['actual_restaurant'] == match['algorithm_restaurant']:
                perfect_matches.append(match)
                comparison_data.append([
                    match['actual_name'],
                    match['actual_restaurant'],
                    match['algorithm_restaurant'],
                    f"{match['algorithm_commute']:.1f}"
                ])
        
        # Add top optimal commutes
        comparison_data.extend([
            [''],
            ['TOP 10 OPTIMAL COMMUTES'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)', 'Status']
        ])
        
        # Sort by commute time
        matched_assignments.sort(key=lambda x: x['algorithm_commute'] if x['algorithm_commute'] else 999)
        
        for match in matched_assignments[:10]:
            status = 'Perfect Match' if match['actual_restaurant'] == match['algorithm_restaurant'] else 'Different Assignment'
            comparison_data.append([
                match['actual_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                f"{match['algorithm_commute']:.1f}",
                status
            ])
        
        # Add complete comparison
        comparison_data.extend([
            [''],
            ['COMPLETE COMPARISON'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)', 'Status', 'Match Method']
        ])
        
        for match in matched_assignments:
            status = 'Perfect Match' if match['actual_restaurant'] == match['algorithm_restaurant'] else 'Different Assignment'
            comparison_data.append([
                match['actual_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                f"{match['algorithm_commute']:.1f}",
                status,
                match['match_method']
            ])
        
        # Add unmatched interns
        if unmatched_assignments:
            comparison_data.extend([
                [''],
                ['UNMATCHED INTERNS'],
                ['Actual Name', 'Actual Restaurant', 'Status']
            ])
            
            for unmatched in unmatched_assignments:
                comparison_data.append([
                    unmatched['actual_name'],
                    unmatched['actual_restaurant'],
                    'No algorithm match'
                ])
        
        # Save comparison
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv('complete_23_interns_final_comparison.csv', index=False, header=False)
        
        print(f"Complete comparison saved to 'complete_23_interns_final_comparison.csv'")
        
        # Print summary
        print(f"\nCOMPLETE SUMMARY:")
        print(f"Perfect Matches: {len(perfect_matches)}")
        print(f"Different Assignments: {len(different_matches)}")
        
        if matched_assignments:
            avg_commute = sum(m['algorithm_commute'] for m in matched_assignments if m['algorithm_commute']) / len([m for m in matched_assignments if m['algorithm_commute']])
            print(f"Average Algorithm Commute: {avg_commute:.1f} minutes")
        
        return matched_assignments, unmatched_assignments
        
    except Exception as e:
        print(f"Error in complete comparison: {e}")
        return [], []

def main():
    """Main function"""
    matched, unmatched = complete_23_comparison()
    
    print(f"\n" + "="*80)
    print("COMPLETE 23 INTERN COMPARISON DONE")
    print("="*80)
    print(f"Final result: {len(matched)} matched, {len(unmatched)} unmatched")

if __name__ == "__main__":
    main()
