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

def get_commute_time_for_actual_match(intern_name, actual_restaurant):
    """Get commute time for actual restaurant assignment"""
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        service = HungarianMatchingService()
        
        # Find intern and restaurant
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        target_intern = None
        for intern in interns:
            if (intern_name.lower() in intern.user.full_name.lower() or 
                intern.user.full_name.lower() in intern_name.lower()):
                target_intern = intern
                break
        
        target_restaurant = None
        for restaurant in restaurants:
            if (actual_restaurant.lower() in restaurant.name.lower() or 
                restaurant.name.lower() in actual_restaurant.lower()):
                target_restaurant = restaurant
                break
        
        if target_intern and target_restaurant:
            # Calculate commute
            commute_info = service.commute_cache.get_commute(
                target_intern.get_full_address(),
                target_restaurant.get_full_address()
            )
            
            if commute_info:
                return commute_info.value // 60000  # Convert milliseconds to minutes
        
        return None
        
    except Exception as e:
        print(f"Error getting commute for {intern_name} -> {actual_restaurant}: {e}")
        return None

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
                    
                    # Get actual commute time
                    actual_commute = None
                    if actual_restaurant and actual_restaurant.lower() != 'nan':
                        actual_commute = get_commute_time_for_actual_match(intern_name, actual_restaurant)
                        if actual_commute:
                            actual_commute_times.append(actual_commute)
                    
                    # Find optimal assignment
                    optimal_restaurant = 'N/A'
                    optimal_commute = 'N/A'
                    
                    for assignment in optimal_assignments:
                        opt_name = assignment['intern_name']
                        
                        if (intern_name.lower() in opt_name.lower() or 
                            opt_name.lower() in intern_name.lower()):
                            
                            optimal_restaurant = assignment['restaurant_name']
                            optimal_commute = assignment['commute_minutes']
                            optimal_commute_times.append(optimal_commute)
                            break
                    
                    comparison_data.append({
                        'intern_name': intern_name,
                        'actual_restaurant': actual_restaurant,
                        'actual_commute': actual_commute if actual_commute is not None else 'N/A',
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
        
        print(f"✅ CSV created: {csv_file}")
        print(f"📊 Average actual commute: {avg_actual_commute:.1f} minutes")
        print(f"📊 Average optimal commute: {avg_optimal_commute:.1f} minutes")
        print(f"📈 Commute improvement: {avg_actual_commute - avg_optimal_commute:.1f} minutes")
        
        # Display sample data
        print(f"\n--- SAMPLE DATA ---")
        for i, data in enumerate(comparison_data[:5]):
            print(f"{data['intern_name']}: {data['actual_restaurant']} ({data['actual_commute']} min) vs {data['optimal_restaurant']} ({data['optimal_commute']} min)")
        
        return csv_file, avg_actual_commute, avg_optimal_commute
        
    except Exception as e:
        print(f"Error creating CSV: {e}")
        return None, 0, 0

def create_detailed_analysis():
    """Create detailed analysis with additional metrics"""
    print("\n=== CREATING DETAILED ANALYSIS ===")
    
    try:
        # Load the CSV we just created
        df = pd.read_csv('fall_2025_comparison.csv')
        
        # Skip summary rows
        data_rows = df[df['Intern Name'] != 'SUMMARY STATISTICS'].copy()
        
        # Analysis
        total_interns = len(data_rows)
        
        # Filter out N/A values for commute analysis
        actual_commutes = data_rows[data_rows['Actual Commute (min)'] != 'N/A']['Actual Commute (min)'].astype(float)
        optimal_commutes = data_rows[data_rows['Optimal Commute (min)'] != 'N/A']['Optimal Commute (min)'].astype(float)
        
        # Find matches
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
        
        print(f"📊 DETAILED ANALYSIS:")
        print(f"Total interns: {total_interns}")
        print(f"Same matches: {len(same_matches)}")
        print(f"Different matches: {len(different_matches)}")
        print(f"No optimal assignment: {len(no_optimal)}")
        print(f"Actual commutes calculated: {len(actual_commutes)}")
        print(f"Optimal commutes available: {len(optimal_commutes)}")
        
        # Best and worst improvements
        if len(different_matches) > 0:
            different_matches_clean = different_matches[
                (different_matches['Actual Commute (min)'] != 'N/A') & 
                (different_matches['Optimal Commute (min)'] != 'N/A')
            ].copy()
            
            different_matches_clean['Actual Commute (min)'] = different_matches_clean['Actual Commute (min)'].astype(float)
            different_matches_clean['Optimal Commute (min)'] = different_matches_clean['Optimal Commute (min)'].astype(float)
            
            different_matches_clean['Improvement'] = different_matches_clean['Actual Commute (min)'] - different_matches_clean['Optimal Commute (min)']
            
            best_improvement = different_matches_clean.loc[different_matches_clean['Improvement'].idxmax()]
            worst_case = different_matches_clean.loc[different_matches_clean['Improvement'].idxmin()]
            
            print(f"\n🏆 BEST IMPROVEMENT:")
            print(f"{best_improvement['Intern Name']}: {best_improvement['Actual Restaurant']} ({best_improvement['Actual Commute (min)']} min) → {best_improvement['Optimal Restaurant']} ({best_improvement['Optimal Commute (min)']} min)")
            print(f"Improvement: {best_improvement['Improvement']:.1f} minutes")
            
            print(f"\n⚠️ WORST CASE (actual better):")
            print(f"{worst_case['Intern Name']}: {worst_case['Actual Restaurant']} ({worst_case['Actual Commute (min)']} min) → {worst_case['Optimal Restaurant']} ({worst_case['Optimal Commute (min)']} min)")
            print(f"Difference: {worst_case['Improvement']:.1f} minutes")
        
        return {
            'total_interns': total_interns,
            'same_matches': len(same_matches),
            'different_matches': len(different_matches),
            'no_optimal': len(no_optimal),
            'actual_commutes': len(actual_commutes),
            'optimal_commutes': len(optimal_commutes)
        }
        
    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        return {}

if __name__ == "__main__":
    # Create comparison CSV
    csv_file, avg_actual, avg_optimal = create_comparison_csv()
    
    if csv_file:
        # Create detailed analysis
        analysis = create_detailed_analysis()
        
        print(f"\n=== FINAL SUMMARY ===")
        print(f"CSV file: {csv_file}")
        print(f"Average actual commute: {avg_actual:.1f} minutes")
        print(f"Average optimal commute: {avg_optimal:.1f} minutes")
        print(f"Overall improvement: {avg_actual - avg_optimal:.1f} minutes")
        
        if analysis:
            print(f"Same matches: {analysis['same_matches']}")
            print(f"Different matches: {analysis['different_matches']}")
            print(f"No optimal assignment: {analysis['no_optimal']}")
    
    print("\n=== CSV CREATION COMPLETE ===")
