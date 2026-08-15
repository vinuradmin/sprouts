#!/usr/bin/env python3
"""
Create final summary of Fall 2025 comparison
"""

import pandas as pd
import csv

def create_final_summary():
    """Create final summary without encoding issues"""
    print("=== CREATING FINAL FALL 2025 SUMMARY ===")
    
    try:
        # Read the CSV
        df = pd.read_csv('fall_2025_comparison.csv')
        
        # Filter out summary rows
        data_rows = df[df['Intern Name'] != 'SUMMARY STATISTICS'].copy()
        
        # Analysis
        same_matches = data_rows[
            (data_rows['Actual Restaurant'] != 'N/A') & 
            (data_rows['Optimal Restaurant'] != 'N/A') &
            (data_rows['Actual Restaurant'] == data_rows['Optimal Restaurant'])
        ]
        
        different_matches = data_rows[
            (data_rows['Actual Restaurant'] != 'N/A') & 
            (data_rows['Optimal Restaurant'] != 'N/A') &
            (data_rows['Actual Restaurant'] != data_rows['Optimal Restaurant'])
        ]
        
        # Get optimal commutes
        optimal_commutes = data_rows[data_rows['Optimal Commute (min)'] != 'N/A']['Optimal Commute (min)'].astype(float)
        actual_commutes = data_rows[data_rows['Actual Commute (min)'] != 'N/A']['Actual Commute (min)'].astype(float)
        
        avg_optimal = optimal_commutes.mean() if len(optimal_commutes) > 0 else 0
        avg_actual = actual_commutes.mean() if len(actual_commutes) > 0 else 0
        
        # Create final summary CSV
        summary_file = 'fall_2025_final_summary.csv'
        
        with open(summary_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Header
            writer.writerow(['Fall 2025 Intern Matching Analysis'])
            writer.writerow([])
            
            # Summary statistics
            writer.writerow(['KEY METRICS'])
            writer.writerow(['Total Interns Analyzed', len(data_rows)])
            writer.writerow(['Perfect Matches', len(same_matches)])
            writer.writerow(['Different Matches', len(different_matches)])
            writer.writerow(['Actual Commutes Available', len(actual_commutes)])
            writer.writerow(['Optimal Commutes Available', len(optimal_commutes)])
            writer.writerow([])
            
            # Commute comparison
            writer.writerow(['COMMUTE COMPARISON'])
            writer.writerow(['Average Actual Commute (minutes)', f'{avg_actual:.1f}'])
            writer.writerow(['Average Optimal Commute (minutes)', f'{avg_optimal:.1f}'])
            writer.writerow(['Note', 'Limited actual commute data available'])
            writer.writerow([])
            
            # Perfect matches
            if len(same_matches) > 0:
                writer.writerow(['PERFECT MATCHES (Current placements are optimal)'])
                writer.writerow(['Intern Name', 'Restaurant', 'Commute (minutes)'])
                for _, row in same_matches.iterrows():
                    writer.writerow([row['Intern Name'], row['Actual Restaurant'], row['Actual Commute (min)']])
                writer.writerow([])
            
            # Best optimal commutes
            optimal_available = data_rows[data_rows['Optimal Commute (min)'] != 'N/A'].copy()
            optimal_available['Optimal Commute (min)'] = pd.to_numeric(optimal_available['Optimal Commute (min)'])
            
            if len(optimal_available) > 0:
                best_commutes = optimal_available.nsmallest(10, 'Optimal Commute (min)')
                writer.writerow(['TOP 10 OPTIMAL COMMUTES'])
                writer.writerow(['Intern Name', 'Current Restaurant', 'Optimal Restaurant', 'Optimal Commute (minutes)'])
                for _, row in best_commutes.iterrows():
                    actual_restaurant = row['Actual Restaurant'] if row['Actual Restaurant'] != 'N/A' else 'None'
                    writer.writerow([row['Intern Name'], actual_restaurant, row['Optimal Restaurant'], row['Optimal Commute (min)']])
                writer.writerow([])
            
            # All interns comparison
            writer.writerow(['COMPLETE COMPARISON'])
            writer.writerow(['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Status'])
            for _, row in data_rows.iterrows():
                if row['Optimal Restaurant'] == 'N/A':
                    status = 'No Optimal Available'
                elif row['Actual Restaurant'] == row['Optimal Restaurant']:
                    status = 'Perfect Match'
                else:
                    status = 'Improvement Opportunity'
                
                writer.writerow([row['Intern Name'], row['Actual Restaurant'], row['Optimal Restaurant'], status])
        
        print(f"Final summary created: {summary_file}")
        
        # Print key findings
        print(f"\n=== KEY FINDINGS ===")
        print(f"Total interns analyzed: {len(data_rows)}")
        print(f"Perfect matches: {len(same_matches)}")
        print(f"Different matches: {len(different_matches)}")
        print(f"Average optimal commute: {avg_optimal:.1f} minutes")
        
        if len(same_matches) > 0:
            print(f"\nPerfect matches:")
            for _, row in same_matches.iterrows():
                print(f"  {row['Intern Name']} -> {row['Actual Restaurant']} ({row['Actual Commute (min)']} min)")
        
        if len(optimal_available) > 0:
            print(f"\nBest optimal commutes:")
            best_commutes = optimal_available.nsmallest(5, 'Optimal Commute (min)')
            for _, row in best_commutes.iterrows():
                actual_restaurant = row['Actual Restaurant'] if row['Actual Restaurant'] != 'N/A' else 'None'
                print(f"  {row['Intern Name']}: {actual_restaurant} -> {row['Optimal Restaurant']} ({row['Optimal Commute (min)']} min)")
        
        return summary_file
        
    except Exception as e:
        print(f"Error creating final summary: {e}")
        return None

if __name__ == "__main__":
    summary_file = create_final_summary()
    
    if summary_file:
        print(f"\n=== FILES CREATED ===")
        print(f"1. fall_2025_comparison.csv - Detailed comparison")
        print(f"2. {summary_file} - Summary analysis")
    
    print("\n=== SUMMARY CREATION COMPLETE ===")
