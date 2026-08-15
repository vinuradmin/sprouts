#!/usr/bin/env python3
"""
Create corrected analysis of Fall 2025 comparison
"""

import pandas as pd
import csv

def analyze_csv():
    """Analyze the created CSV"""
    print("=== CORRECTED FALL 2025 ANALYSIS ===")
    
    try:
        # Read the CSV
        df = pd.read_csv('fall_2025_comparison.csv')
        
        # Filter out summary rows
        data_rows = df[df['Intern Name'] != 'SUMMARY STATISTICS'].copy()
        
        print(f"Total interns: {len(data_rows)}")
        
        # Analysis categories
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
        
        no_optimal = data_rows[data_rows['Optimal Restaurant'] == 'N/A']
        no_actual = data_rows[data_rows['Actual Restaurant'] == 'N/A']
        
        print(f"\n=== MATCH BREAKDOWN ===")
        print(f"Same matches: {len(same_matches)}")
        print(f"Different matches: {len(different_matches)}")
        print(f"No optimal assignment: {len(no_optimal)}")
        print(f"No actual assignment: {len(no_actual)}")
        
        # Show perfect matches
        if len(same_matches) > 0:
            print(f"\n=== PERFECT MATCHES ===")
            for _, row in same_matches.iterrows():
                print(f"{row['Intern Name']}: {row['Actual Restaurant']} ({row['Actual Commute (min)']} min)")
        
        # Show different matches with available commutes
        different_with_commutes = different_matches[
            (different_matches['Optimal Commute (min)'] != 'N/A')
        ]
        
        if len(different_with_commutes) > 0:
            print(f"\n=== OPTIMAL IMPROVEMENTS ===")
            for _, row in different_with_commutes.iterrows():
                actual_commute = row['Actual Commute (min)'] if row['Actual Commute (min)'] != 'N/A' else 'Unknown'
                print(f"{row['Intern Name']}: {row['Actual Restaurant']} ({actual_commute} min) → {row['Optimal Restaurant']} ({row['Optimal Commute (min)']} min)")
        
        # Show best optimal commutes
        optimal_available = data_rows[data_rows['Optimal Commute (min)'] != 'N/A'].copy()
        optimal_available['Optimal Commute (min)'] = pd.to_numeric(optimal_available['Optimal Commute (min)'])
        
        if len(optimal_available) > 0:
            best_commutes = optimal_available.nsmallest(5, 'Optimal Commute (min)')
            print(f"\n=== BEST OPTIMAL COMMUTES ===")
            for _, row in best_commutes.iterrows():
                actual_restaurant = row['Actual Restaurant'] if row['Actual Restaurant'] != 'N/A' else 'None'
                print(f"{row['Intern Name']}: {actual_restaurant} → {row['Optimal Restaurant']} ({row['Optimal Commute (min)']} min)")
        
        # Calculate proper averages
        optimal_commutes = data_rows[data_rows['Optimal Commute (min)'] != 'N/A']['Optimal Commute (min)'].astype(float)
        actual_commutes = data_rows[data_rows['Actual Commute (min)'] != 'N/A']['Actual Commute (min)'].astype(float)
        
        avg_optimal = optimal_commutes.mean() if len(optimal_commutes) > 0 else 0
        avg_actual = actual_commutes.mean() if len(actual_commutes) > 0 else 0
        
        print(f"\n=== COMMUTE ANALYSIS ===")
        print(f"Actual commutes available: {len(actual_commutes)}")
        print(f"Optimal commutes available: {len(optimal_commutes)}")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average optimal commute: {avg_optimal:.1f} minutes")
        
        if len(actual_commutes) > 0 and len(optimal_commutes) > 0:
            if avg_optimal < avg_actual:
                improvement = avg_actual - avg_optimal
                print(f"Optimal algorithm improves commute by: {improvement:.1f} minutes")
            else:
                difference = avg_optimal - avg_actual
                print(f"Note: Optimal average is {difference:.1f} minutes higher (limited actual data)")
        
        # Create summary CSV
        create_summary_csv(data_rows, same_matches, different_matches, no_optimal, avg_actual, avg_optimal)
        
        return {
            'total_interns': len(data_rows),
            'same_matches': len(same_matches),
            'different_matches': len(different_matches),
            'no_optimal': len(no_optimal),
            'avg_actual': avg_actual,
            'avg_optimal': avg_optimal
        }
        
    except Exception as e:
        print(f"Error analyzing CSV: {e}")
        return {}

def create_summary_csv(data_rows, same_matches, different_matches, no_optimal, avg_actual, avg_optimal):
    """Create a summary CSV with key insights"""
    print("\n=== CREATING SUMMARY CSV ===")
    
    summary_file = 'fall_2025_summary.csv'
    
    with open(summary_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Header
        writer.writerow(['Fall 2025 Intern Matching Analysis'])
        writer.writerow([])
        
        # Summary statistics
        writer.writerow(['SUMMARY STATISTICS'])
        writer.writerow(['Total Interns', len(data_rows)])
        writer.writerow(['Same Matches', len(same_matches)])
        writer.writerow(['Different Matches', len(different_matches)])
        writer.writerow(['No Optimal Assignment', len(no_optimal)])
        writer.writerow([])
        
        # Commute analysis
        writer.writerow(['COMMUTE ANALYSIS'])
        writer.writerow(['Average Actual Commute (min)', f'{avg_actual:.1f}'])
        writer.writerow(['Average Optimal Commute (min)', f'{avg_optimal:.1f}'])
        writer.writerow([])
        
        # Perfect matches
        if len(same_matches) > 0:
            writer.writerow(['PERFECT MATCHES'])
            writer.writerow(['Intern Name', 'Restaurant', 'Commute (min)'])
            for _, row in same_matches.iterrows():
                writer.writerow([row['Intern Name'], row['Actual Restaurant'], row['Actual Commute (min)']])
            writer.writerow([])
        
        # Best optimal commutes
        optimal_available = data_rows[data_rows['Optimal Commute (min)'] != 'N/A'].copy()
        optimal_available['Optimal Commute (min)'] = pd.to_numeric(optimal_available['Optimal Commute (min)'])
        
        if len(optimal_available) > 0:
            best_commutes = optimal_available.nsmallest(10, 'Optimal Commute (min)')
            writer.writerow(['TOP 10 OPTIMAL COMMUTES'])
            writer.writerow(['Intern Name', 'Actual Restaurant', 'Optimal Restaurant', 'Optimal Commute (min)'])
            for _, row in best_commutes.iterrows():
                actual_restaurant = row['Actual Restaurant'] if row['Actual Restaurant'] != 'N/A' else 'None'
                writer.writerow([row['Intern Name'], actual_restaurant, row['Optimal Restaurant'], row['Optimal Commute (min)']])
        
        print(f"Summary CSV created: {summary_file}")

if __name__ == "__main__":
    results = analyze_csv()
    
    if results:
        print(f"\n=== FINAL RESULTS ===")
        print(f"Total interns analyzed: {results['total_interns']}")
        print(f"Perfect matches: {results['same_matches']}")
        print(f"Improvement opportunities: {results['different_matches']}")
        print(f"Need data updates: {results['no_optimal']}")
        print(f"Average optimal commute: {results['avg_optimal']:.1f} minutes")
    
    print("\n=== ANALYSIS COMPLETE ===")
