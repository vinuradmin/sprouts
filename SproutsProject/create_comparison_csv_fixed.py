#!/usr/bin/env python3
"""
Create CSV comparing actual Fall 2025 placements with optimal algorithm
"""

import pandas as pd
import sys
import os
import csv

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_comparison_csv():
    """Create comprehensive comparison CSV"""
    print("=== CREATING COMPARISON CSV ===")
    
    try:
        # Load actual assignments
        active_df = pd.read_excel('C:/Users/pierr/Downloads/sprouts data.xlsx', sheet_name='Active Intern List')
        
        # Get optimal assignments
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        optimal_results = service.find_optimal_assignments(interns, restaurants)
        optimal_assignments = optimal_results.get('assignments', [])
        
        # Create comparison data
        comparison_data = []
        actual_commute_times = []
        optimal_commute_times = []
        
        for idx in range(338, 367):  # Fall 2025 section
            if idx < len(active_df):
                row = active_df.iloc[idx]
                intern_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                
                if intern_name and intern_name.lower() != 'nan' and 'latitude' not in intern_name.lower():
                    # Get actual assignment
                    actual_restaurant = str(row.iloc[14]).strip() if pd.notna(row.iloc[14]) else ''
                    placement = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ''
                    
                    # Get actual commute time (from optimal assignments if available)
                    actual_commute = 'N/A'
                    
                    # Find optimal assignment for this intern
                    optimal_restaurant = 'N/A'
                    optimal_commute = 'N/A'
                    
                    for assignment in optimal_assignments:
                        opt_name = assignment['intern_name']
                        
                        if (intern_name.lower() in opt_name.lower() or 
                            opt_name.lower() in intern_name.lower()):
                            
                            optimal_restaurant = assignment['restaurant_name']
                            optimal_commute = assignment['commute_minutes']
                            optimal_commute_times.append(optimal_commute)
                            
                            # If actual restaurant matches optimal, use that commute
                            if actual_restaurant and actual_restaurant.lower() != 'nan':
                                if (actual_restaurant.lower() in optimal_restaurant.lower() or 
                                    optimal_restaurant.lower() in actual_restaurant.lower()):
                                    actual_commute = optimal_commute
                                    actual_commute_times.append(actual_commute)
                            
                            break
                    
                    comparison_data.append({
                        'intern_name': intern_name,
                        'actual_restaurant': actual_restaurant,
                        'actual_commute': actual_commute,
                        'optimal_restaurant': optimal_restaurant,
                        'optimal_commute': optimal_commute
                    })
        
        # Calculate averages
        avg_actual_commute = sum(actual_commute_times) / len(actual_commute_times) if actual_commute_times else 0
        avg_optimal_commute = sum(optimal_commute_times) / len(optimal_commute_times) if optimal_commute_times else 0
        
        # Write to CSV
        csv_file = 'fall_2025_comparison.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(['Intern Name', 'Actual Restaurant', 'Actual Commute (min)', 'Optimal Restaurant', 'Optimal Commute (min)'])
            
            # Write data
            for data in comparison_data:
                writer.writerow([
                    data['intern_name'],
                    data['actual_restaurant'],
                    data['actual_commute'],
                    data['optimal_restaurant'],
                    data['optimal_commute']
                ])
            
            # Write summary
            writer.writerow([])
            writer.writerow(['SUMMARY STATISTICS'])
            writer.writerow(['Average Actual Commute (min)', f'{avg_actual_commute:.1f}'])
            writer.writerow(['Average Optimal Commute (min)', f'{avg_optimal_commute:.1f}'])
            writer.writerow(['Commute Improvement (min)', f'{avg_actual_commute - avg_optimal_commute:.1f}'])
            writer.writerow(['Total Interns Compared', len(comparison_data)])
            writer.writerow(['Actual Commutes Calculated', len(actual_commute_times)])
            writer.writerow(['Optimal Commutes Available', len(optimal_commute_times)])
        
        print(f"CSV created: {csv_file}")
        print(f"Average actual commute: {avg_actual_commute:.1f} minutes")
        print(f"Average optimal commute: {avg_optimal_commute:.1f} minutes")
        print(f"Commute improvement: {avg_actual_commute - avg_optimal_commute:.1f} minutes")
        
        # Display sample data
        print(f"\n--- SAMPLE DATA ---")
        for i, data in enumerate(comparison_data[:5]):
            print(f"{data['intern_name']}: {data['actual_restaurant']} ({data['actual_commute']} min) vs {data['optimal_restaurant']} ({data['optimal_commute']} min)")
        
        return csv_file, avg_actual_commute, avg_optimal_commute, comparison_data
        
    except Exception as e:
        print(f"Error creating CSV: {e}")
        return None, 0, 0, []

def analyze_comparison_data(comparison_data):
    """Analyze the comparison data"""
    print("\n=== ANALYSIS ===")
    
    # Count different types of matches
    same_matches = 0
    different_matches = 0
    no_optimal = 0
    
    for data in comparison_data:
        if data['optimal_restaurant'] == 'N/A':
            no_optimal += 1
        elif data['actual_restaurant'] == data['optimal_restaurant']:
            same_matches += 1
        else:
            different_matches += 1
    
    print(f"Same matches: {same_matches}")
    print(f"Different matches: {different_matches}")
    print(f"No optimal assignment: {no_optimal}")
    
    # Find best improvements
    improvements = []
    for data in comparison_data:
        if (data['actual_commute'] != 'N/A' and 
            data['optimal_commute'] != 'N/A' and
            data['actual_restaurant'] != data['optimal_restaurant']):
            
            improvement = data['actual_commute'] - data['optimal_commute']
            improvements.append({
                'intern': data['intern_name'],
                'actual': data['actual_restaurant'],
                'optimal': data['optimal_restaurant'],
                'improvement': improvement
            })
    
    if improvements:
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        print(f"\nTop improvements:")
        for imp in improvements[:5]:
            print(f"{imp['intern']}: {imp['actual']} → {imp['optimal']} ({imp['improvement']:.1f} min improvement)")

if __name__ == "__main__":
    # Create comparison CSV
    csv_file, avg_actual, avg_optimal, comparison_data = create_comparison_csv()
    
    if csv_file:
        # Analyze data
        analyze_comparison_data(comparison_data)
        
        print(f"\n=== FINAL SUMMARY ===")
        print(f"CSV file: {csv_file}")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average optimal commute: {avg_optimal:.1f} minutes")
        print(f"Overall improvement: {avg_actual - avg_optimal:.1f} minutes")
    
    print("\n=== CSV CREATION COMPLETE ===")
