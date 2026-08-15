#!/usr/bin/env python3
"""
Simple comparison for all 23 assigned interns
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_23_comparison():
    """Create comparison for all 23 assigned interns"""
    print("="*80)
    print("CREATING COMPARISON FOR ALL 23 ASSIGNED INTERNS")
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
        print(f"Actual assigned interns: {len(assigned_interns)}")
        
        # Manual name mapping based on analysis
        name_mapping = {
            'Enrique': 'Enrique Marroquin',
            'Giselle': 'Giselle Contreras', 
            'Ollie': 'Ollie  O\'Malley',
            'Angel': 'Angel Ruiz',
            'Gylli': 'Gyllibhet  Palacio',
            'Shelsea': 'Shelsea Vasquez',
            'Kaylin': 'Kaylin Lewis',
            'Roni': 'Roni Velasquez',
            'Melanie Sanchez': 'Melanie Sanchez Ortega',
            'Gio': 'Giovanni Giacomazzi',
            'Imani': 'Imani Jarvis',
            'Jesus': 'Jesus Chavez',  # First Jesus
            'Alex': 'Alexander Barrios Castaneda',
            'Andrea': 'Andrea Caballero',
            'Nae': 'Eljanae Robinson',
            'maye': 'Yeimi Diaz'
        }
        
        # Create algorithm lookup
        algorithm_lookup = {assign['intern_name']: assign for assign in assignments}
        
        # Match assignments
        matched_assignments = []
        unmatched_assignments = []
        
        print(f"\nMatching process:")
        for actual in assigned_interns:
            actual_name = actual['actual_name']
            actual_restaurant = actual['actual_restaurant']
            
            mapped_name = name_mapping.get(actual_name)
            
            if mapped_name and mapped_name in algorithm_lookup:
                algorithm_assignment = algorithm_lookup[mapped_name]
                
                matched_assignments.append({
                    'actual_name': actual_name,
                    'actual_restaurant': actual_restaurant,
                    'algorithm_name': algorithm_assignment['intern_name'],
                    'algorithm_restaurant': algorithm_assignment['restaurant_name'],
                    'algorithm_commute': algorithm_assignment['commute_minutes']
                })
                
                print(f"MATCH: {actual_name} -> {algorithm_assignment['intern_name']} -> {algorithm_assignment['restaurant_name']} ({algorithm_assignment['commute_minutes']} min)")
            else:
                unmatched_assignments.append(actual)
                print(f"NO MATCH: {actual_name} -> {actual_restaurant}")
        
        print(f"\nRESULTS:")
        print(f"Matched: {len(matched_assignments)}")
        print(f"Unmatched: {len(unmatched_assignments)}")
        
        # Create comparison data
        comparison_data = [
            ['Fall 2025 vs Algorithm Comparison - All Assigned Interns'],
            [''],
            ['KEY METRICS'],
            ['Total Assigned Interns', len(assigned_interns)],
            ['Successfully Matched', len(matched_assignments)],
            ['Unmatched', len(unmatched_assignments)],
            ['Match Rate', f'{len(matched_assignments)/len(assigned_interns)*100:.1f}%'],
            [''],
            ['MATCHED INTERNS COMPARISON'],
            ['Actual Name', 'Actual Restaurant', 'Algorithm Restaurant', 'Commute (min)', 'Status']
        ]
        
        # Add matched interns
        perfect_matches = 0
        different_matches = 0
        
        for match in matched_assignments:
            if match['actual_restaurant'] == match['algorithm_restaurant']:
                status = 'Perfect Match'
                perfect_matches += 1
            else:
                status = 'Different Assignment'
                different_matches += 1
            
            comparison_data.append([
                match['actual_name'],
                match['actual_restaurant'],
                match['algorithm_restaurant'],
                f"{match['algorithm_commute']:.1f}",
                status
            ])
        
        # Add unmatched interns
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
        comparison_df.to_csv('all_23_assigned_interns_comparison.csv', index=False, header=False)
        
        print(f"\nComparison saved to 'all_23_assigned_interns_comparison.csv'")
        
        # Print summary
        print(f"\nSUMMARY:")
        print(f"Perfect Matches: {perfect_matches}")
        print(f"Different Assignments: {different_matches}")
        
        if matched_assignments:
            avg_commute = sum(m['algorithm_commute'] for m in matched_assignments if m['algorithm_commute']) / len([m for m in matched_assignments if m['algorithm_commute']])
            print(f"Average Algorithm Commute: {avg_commute:.1f} minutes")
        
        return matched_assignments, unmatched_assignments
        
    except Exception as e:
        print(f"Error creating comparison: {e}")
        return [], []

def main():
    """Main function"""
    matched, unmatched = create_23_comparison()
    
    print(f"\n" + "="*80)
    print("23 INTERNS COMPARISON COMPLETE")
    print("="*80)
    print(f"Total comparison created for {len(matched) + len(unmatched)} assigned interns")

if __name__ == "__main__":
    main()
