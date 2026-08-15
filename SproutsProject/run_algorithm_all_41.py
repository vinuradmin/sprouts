#!/usr/bin/env python3
"""
Run Hungarian algorithm with all 41 interns and redo comparative analysis
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def run_algorithm_all_interns():
    """Run algorithm with all 41 interns"""
    print("="*80)
    print("RUNNING HUNGARIAN ALGORITHM WITH ALL 41 INTERNS")
    print("="*80)
    
    try:
        # Load actual data from Excel (Column 15 - Trial Onboarding)
        excel_path = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df = pd.read_excel(excel_path, sheet_name="Active Intern List")
        fall_2025_df = df.iloc[337:367].copy()
        
        # Get all interns (not just assigned ones)
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        print(f"Total interns in database: {len(interns)}")
        print(f"Total restaurants: {len(restaurants)}")
        
        # Run algorithm with all interns
        print(f"\nRunning Hungarian algorithm...")
        results = service.find_optimal_assignments(interns, restaurants)
        assignments = results.get('assignments', [])
        
        print(f"Algorithm generated {len(assignments)} assignments")
        
        # Extract actual assignments from Excel
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
        
        print(f"Actual assigned interns in Excel: {len(assigned_interns)}")
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Enhanced matching for all 41 interns
        matched_assignments = []
        unmatched_assignments = []
        
        print(f"\nMatching {len(assigned_interns)} actual assignments with {len(assignments)} algorithm assignments...")
        
        # Name mapping including the previously unmatched
        enhanced_mapping = {
            'JP': 'Samuel  Gonzalez ',
            'Enrique': 'Enrique Marroquin',
            'Giselle': 'Giselle Contreras ',
            'Ollie': 'Ollie  O\'Malley',
            'Dana': 'Catherine Oropeza Huerta',
            'Bosco Liu': 'Zhijian Liu',
            'Angel': 'Angel Ruiz',
            'Gylli': 'Gyllibhet  Palacio',
            'Jesus': 'Jesus Chavez',
            'Alex': 'Alexander Barrios Castañeda',
            'Andrea': 'Andrea Caballero ',
            'Noel': 'Aliyatt  Rodgers',
            'Alexis/bri': 'Zailea Daniels',
            'Nae': 'Eljanae Robinson',
            'maye': 'Yeimi Diaz ',
            'Shelsea': 'Shelsea Vasquez',
            'Kaylin': 'Kaylin Lewis',
            'Ivory Willows': 'Aaliyah Engram',
            'Roni': 'Roni Velasquez',
            'Melanie Sanchez': 'Melanie Sanchez Ortega',
            'Gio': 'Giovanni Giacomazzi',
            'Imani': 'Imani Jarvis'
        }
        
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            matched_assignment = None
            match_method = None
            
            # Try enhanced mapping
            if actual_name in enhanced_mapping:
                mapped_name = enhanced_mapping[actual_name]
                if mapped_name in algorithm_lookup:
                    matched_assignment = algorithm_lookup[mapped_name]
                    match_method = f'Enhanced mapping ({actual_name} -> {mapped_name})'
            
            # Try exact match
            elif actual_name in algorithm_lookup:
                matched_assignment = algorithm_lookup[actual_name]
                match_method = 'Exact match'
            
            # Try first name match
            else:
                actual_first = actual_name.strip().split()[0].lower()
                for algo_name in algorithm_lookup:
                    algo_first = algo_name.strip().split()[0].lower()
                    if actual_first == algo_first:
                        matched_assignment = algorithm_lookup[algo_name]
                        match_method = f'First name match ({actual_name} -> {algo_name})'
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
            else:
                unmatched_assignments.append(actual)
        
        print(f"Matched: {len(matched_assignments)}")
        print(f"Unmatched: {len(unmatched_assignments)}")
        print(f"Match Rate: {len(matched_assignments)/len(assigned_interns)*100:.1f}%")
        
        return matched_assignments, unmatched_assignments, assignments
        
    except Exception as e:
        print(f"Error running algorithm: {e}")
        return [], [], []

def create_comprehensive_analysis(matched_assignments, unmatched_assignments, all_assignments):
    """Create comprehensive analysis with all 41 interns"""
    print("="*80)
    print("CREATING COMPREHENSIVE ANALYSIS")
    print("With all 41 interns considered")
    print("="*80)
    
    try:
        # Calculate metrics
        perfect_matches = []
        different_assignments = []
        
        for match in matched_assignments:
            if match['actual_restaurant'] == match['algorithm_restaurant']:
                perfect_matches.append(match)
            else:
                different_assignments.append(match)
        
        # Create comprehensive comparison data
        comparison_data = [
            ['Complete 41-Intern Algorithm Comparison'],
            [''],
            ['KEY METRICS'],
            ['Total Assigned Interns (Excel)', len(matched_assignments) + len(unmatched_assignments)],
            ['Algorithm Assignments Generated', len(all_assignments)],
            ['Successfully Matched', len(matched_assignments)],
            ['Unmatched', len(unmatched_assignments)],
            ['Match Rate', f'{len(matched_assignments)/(len(matched_assignments) + len(unmatched_assignments))*100:.1f}%'],
            ['Perfect Matches', len(perfect_matches)],
            ['Different Assignments', len(different_assignments)],
            [''],
            ['PERFECT MATCHES (Current placements are optimal)'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)']
        ]
        
        # Add perfect matches
        for match in perfect_matches:
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
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)', 'Status']
        ])
        
        for match in matched_assignments:
            status = 'Perfect Match' if match['actual_restaurant'] == match['algorithm_restaurant'] else 'Different Assignment'
            comparison_data.append([
                match['actual_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                f"{match['algorithm_commute']:.1f}",
                status
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
        
        # Add algorithm-only assignments (interns assigned by algorithm but not in Excel)
        algorithm_names = [match['algorithm_name'] for match in matched_assignments]
        algorithm_only = [assign for assign in all_assignments if assign['intern_name'] not in algorithm_names]
        
        if algorithm_only:
            comparison_data.extend([
                [''],
                ['ALGORITHM-ONLY ASSIGNMENTS'],
                ['Algorithm Name', 'Algorithm Restaurant', 'Commute (min)', 'Status']
            ])
            
            for assign in algorithm_only[:10]:  # Show first 10
                comparison_data.append([
                    assign['intern_name'],
                    assign['restaurant_name'],
                    f"{assign['commute_minutes']:.1f}",
                    'Algorithm only'
                ])
        
        # Save comparison
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv('complete_41_intern_algorithm_comparison.csv', index=False, header=False)
        
        print(f"Complete 41-intern comparison saved to 'complete_41_intern_algorithm_comparison.csv'")
        
        # Print summary
        if matched_assignments:
            avg_commute = sum(m['algorithm_commute'] for m in matched_assignments if m['algorithm_commute']) / len([m for m in matched_assignments if m['algorithm_commute']])
            print(f"\nCOMPREHENSIVE SUMMARY:")
            print(f"Perfect Matches: {len(perfect_matches)}")
            print(f"Different Assignments: {len(different_assignments)}")
            print(f"Average Algorithm Commute: {avg_commute:.1f} minutes")
            print(f"Algorithm-Only Assignments: {len(algorithm_only)}")
        
        return comparison_df
        
    except Exception as e:
        print(f"Error creating analysis: {e}")
        return None

def main():
    """Main function"""
    matched, unmatched, all_assignments = run_algorithm_all_interns()
    
    if matched or unmatched:
        comparison_df = create_comprehensive_analysis(matched, unmatched, all_assignments)
        
        print(f"\n" + "="*80)
        print("COMPLETE 41-INTERN ANALYSIS COMPLETE")
        print("="*80)
        print(f"Algorithm run with all interns and comprehensive analysis created")
    else:
        print("Error running algorithm")

if __name__ == "__main__":
    main()
