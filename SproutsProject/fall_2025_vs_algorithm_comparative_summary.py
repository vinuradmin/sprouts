#!/usr/bin/env python3
"""
Create comparative analysis and summary in the same format as fall_2025_final_summary.csv
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_comparative_summary():
    """Create comparative summary in the same format as existing file"""
    print("="*80)
    print("FALL 2025 vs ALGORITHM COMPARATIVE ANALYSIS")
    print("Same format as fall_2025_final_summary.csv")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
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
        
        # Extract actual assignments from Column 15 (Trial Onboarding)
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
                    'actual_restaurant': actual_restaurant
                })
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Create comparative data with name matching
        comparative_data = []
        perfect_matches = []
        different_matches = []
        
        for actual in actual_assignments:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            # Find matching algorithm assignment
            matching_assignment = None
            match_type = 'None'
            
            # Try exact match first
            for assign in assignments:
                if assign['intern_name'].strip() == actual_name.strip():
                    matching_assignment = assign
                    match_type = 'Exact'
                    break
            
            # If no exact match, try partial match
            if not matching_assignment:
                for assign in assignments:
                    algo_name = assign['intern_name'].strip().lower()
                    actual_lower = actual_name.strip().lower()
                    
                    if (actual_lower in algo_name or algo_name in actual_lower or
                        actual_lower.replace(' ', '') in algo_name.replace(' ', '') or
                        algo_name.replace(' ', '') in actual_lower.replace(' ', '')):
                        matching_assignment = assign
                        match_type = 'Partial'
                        break
            
            if matching_assignment and actual_restaurant != 'Unassigned':
                algorithm_restaurant = matching_assignment['restaurant_name']
                algorithm_commute = matching_assignment['commute_minutes']
                
                # Determine match status
                if actual_restaurant == algorithm_restaurant:
                    status = 'Perfect Match'
                    perfect_matches.append({
                        'intern_name': actual_name,
                        'restaurant': actual_restaurant,
                        'commute': algorithm_commute
                    })
                else:
                    status = 'Different Match'
                    different_matches.append({
                        'intern_name': actual_name,
                        'actual_restaurant': actual_restaurant,
                        'algorithm_restaurant': algorithm_restaurant,
                        'algorithm_commute': algorithm_commute
                    })
                
                comparative_data.append({
                    'intern_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_restaurant': algorithm_restaurant,
                    'algorithm_commute': algorithm_commute,
                    'status': status,
                    'match_type': match_type
                })
        
        # Calculate metrics
        total_interns = len([d for d in comparative_data if d['actual_restaurant'] != 'Unassigned'])
        perfect_match_count = len(perfect_matches)
        different_match_count = len(different_matches)
        
        if comparative_data:
            avg_algorithm_commute = sum(d['algorithm_commute'] for d in comparative_data if d['algorithm_commute']) / len([d for d in comparative_data if d['algorithm_commute']])
        else:
            avg_algorithm_commute = 0
        
        # Create summary data
        summary_data = [
            ['Fall 2025 vs Algorithm Comparative Analysis'],
            [''],
            ['KEY METRICS'],
            ['Total Interns Analyzed', total_interns],
            ['Perfect Matches', perfect_match_count],
            ['Different Matches', different_match_count],
            ['Actual Commutes Available', 'N/A'],
            ['Optimal Commutes Available', total_interns],
            [''],
            ['COMMUTE COMPARISON'],
            ['Average Actual Commute (minutes)', 'N/A'],
            ['Average Optimal Commute (minutes)', f'{avg_algorithm_commute:.1f}'],
            ['Note', 'Using algorithm-calculated commute times'],
            [''],
            ['PERFECT MATCHES (Current placements are optimal)'],
            ['Intern Name', 'Restaurant', 'Commute (minutes)']
        ]
        
        # Add perfect matches
        for match in perfect_matches:
            summary_data.append([match['intern_name'], match['restaurant'], f"{match['commute']:.1f}"])
        
        # Add top optimal commutes
        summary_data.extend([
            [''],
            ['TOP 10 OPTIMAL COMMUTES'],
            ['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Optimal Commute (minutes)']
        ])
        
        # Sort all matches by commute time
        all_matches = comparative_data.copy()
        all_matches.sort(key=lambda x: x['algorithm_commute'] if x['algorithm_commute'] else 999)
        
        for match in all_matches[:10]:
            if match['algorithm_commute']:
                summary_data.append([
                    match['intern_name'],
                    match['actual_restaurant'],
                    match['algorithm_restaurant'],
                    f"{match['algorithm_commute']:.1f}"
                ])
        
        # Add complete comparison
        summary_data.extend([
            [''],
            ['COMPLETE COMPARISON'],
            ['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Status']
        ])
        
        for match in comparative_data:
            status = match['status']
            if status == 'Different Match':
                status = 'Improvement Opportunity'
            
            summary_data.append([
                match['intern_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                status
            ])
        
        # Create DataFrame and save
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('fall_2025_vs_algorithm_comparative_summary.csv', index=False, header=False)
        
        print(f"Comparative summary saved to 'fall_2025_vs_algorithm_comparative_summary.csv'")
        
        # Print summary
        print(f"\nFALL 2025 vs ALGORITHM COMPARATIVE ANALYSIS")
        print(f"=" * 60)
        print(f"\nKEY METRICS")
        print(f"Total Interns Analyzed: {total_interns}")
        print(f"Perfect Matches: {perfect_match_count}")
        print(f"Different Matches: {different_match_count}")
        print(f"Average Optimal Commute: {avg_algorithm_commute:.1f} minutes")
        
        if perfect_matches:
            print(f"\nPERFECT MATCHES (Current placements are optimal)")
            for match in perfect_matches:
                print(f"{match['intern_name']}, {match['restaurant']}, {match['commute']:.1f}")
        
        print(f"\nTOP 5 OPTIMAL COMMUTES")
        for match in all_matches[:5]:
            print(f"{match['intern_name']}, {match['actual_restaurant']}, {match['algorithm_restaurant']}, {match['algorithm_commute']:.1f}")
        
        return summary_df, {
            'total_interns': total_interns,
            'perfect_matches': perfect_match_count,
            'different_matches': different_match_count,
            'avg_commute': avg_algorithm_commute
        }
        
    except Exception as e:
        print(f"Error creating comparative summary: {e}")
        return None, None

def main():
    """Main function"""
    summary_df, metrics = create_comparative_summary()
    
    if summary_df is not None:
        print(f"\nFILES CREATED:")
        print(f"1. fall_2025_vs_algorithm_comparative_summary.csv - Comparative analysis")
        print(f"   (Same format as fall_2025_final_summary.csv)")
        
        print(f"\nCOMPARATIVE ANALYSIS COMPLETE!")
    else:
        print(f"Error creating comparative summary")

if __name__ == "__main__":
    main()
