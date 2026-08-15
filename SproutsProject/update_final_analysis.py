#!/usr/bin/env python3
"""
Update the final actual vs algorithm assignment analysis
Highlight remaining edge cases with availability issues
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def update_final_analysis():
    """Update final analysis with availability issue highlights"""
    print("="*80)
    print("UPDATING FINAL ANALYSIS")
    print("Highlighting availability issues for remaining edge cases")
    print("="*80)
    
    try:
        from app import create_app
        from app.services.hungarian_matching import HungarianMatchingService
        from app.services.transportation_optimizer import TransportationOptimizer
        from app.models import Intern, Restaurant
        
        app = create_app()
        app.app_context().push()
        
        # Get current algorithm results
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        
        matching_service = HungarianMatchingService()
        result = matching_service.find_optimal_assignments(
            interns, 
            restaurants, 
            max_commute_minutes=90,
            restaurant_capacity=2
        )
        
        assignments = result.get('assignments', [])
        unmatched = result.get('unmatched_interns', [])
        
        print(f"Current algorithm result: {len(assignments)} assigned, {len(unmatched)} unassigned")
        
        # Load Excel data for actual assignments
        excel_file = 'C:/Users/pierr/Downloads/sprouts data.xlsx'
        df_excel = pd.read_excel(excel_file, sheet_name='Active Intern List', header=2)
        
        # Create comprehensive analysis
        analysis_data = []
        
        print(f"\n1. PROCESSING ASSIGNED INTERNS")
        print("-" * 40)
        
        # Process assigned interns
        for assignment in assignments:
            intern_name = assignment.get('intern_name', '')
            algorithm_restaurant = assignment.get('restaurant_name', '')
            algorithm_commute = assignment.get('commute_minutes', 0)
            
            # Find actual assignment from Excel
            actual_restaurant = 'None'
            actual_commute = 0
            
            excel_match = df_excel[df_excel['Name'].str.contains(intern_name.split()[0], na=False, case=False)]
            if not excel_match.empty:
                actual_restaurant = str(excel_match.iloc[0]['Restaurant']).strip()
                if actual_restaurant and actual_restaurant != 'nan':
                    # Calculate actual commute
                    try:
                        optimizer = TransportationOptimizer()
                        intern = next((i for i in interns if intern_name in i.user.full_name), None)
                        if intern:
                            actual_rest_db = next((r for r in restaurants if actual_restaurant in r.name or r.name in actual_restaurant), None)
                            if actual_rest_db:
                                actual_commute = optimizer.get_optimal_commute(
                                    intern.get_full_address(),
                                    actual_rest_db.get_full_address(),
                                    intern.transportation_method or 'driving'
                                )
                    except:
                        pass
            
            # Calculate delta
            if actual_commute and algorithm_commute:
                delta = actual_commute - algorithm_commute
                delta_pct = (delta / actual_commute * 100) if actual_commute > 0 else 0
            else:
                delta = 0
                delta_pct = 0
            
            # Determine status
            if actual_restaurant != 'None' and algorithm_restaurant:
                if delta > 0:
                    status = "Algorithm Better"
                elif delta < 0:
                    status = "Actual Better"
                else:
                    status = "Same"
            elif algorithm_restaurant:
                status = "Algorithm Only"
            else:
                status = "No Assignment"
            
            analysis_data.append({
                'Intern Name': intern_name,
                'Actual Restaurant': actual_restaurant,
                'Algorithm Restaurant': algorithm_restaurant,
                'Actual Commute': actual_commute,
                'Algorithm Commute': algorithm_commute,
                'Delta (min)': delta,
                'Delta %': delta_pct,
                'Status': status,
                'Availability Issue': False
            })
        
        print(f"Processed {len(analysis_data)} assigned interns")
        
        print(f"\n2. PROCESSING UNASSIGNED INTERNS WITH AVAILABILITY ISSUES")
        print("-" * 40)
        
        # Process unassigned interns with availability issues
        availability_issue_interns = ['Eric Willis', 'Gavin Patane', 'Andrea Caballero']
        
        for unmatched_intern in unmatched:
            intern_name = unmatched_intern.get('name', '')
            
            # Check if this is an availability issue case
            is_availability_issue = any(case in intern_name for case in availability_issue_interns)
            
            # Find actual assignment from Excel
            actual_restaurant = 'None'
            actual_commute = 0
            
            excel_match = df_excel[df_excel['Name'].str.contains(intern_name.split()[0], na=False, case=False)]
            if not excel_match.empty:
                actual_restaurant = str(excel_match.iloc[0]['Restaurant']).strip()
                if actual_restaurant and actual_restaurant != 'nan':
                    # Calculate actual commute
                    try:
                        optimizer = TransportationOptimizer()
                        intern = next((i for i in interns if intern_name in i.user.full_name), None)
                        if intern:
                            actual_rest_db = next((r for r in restaurants if actual_restaurant in r.name or r.name in actual_restaurant), None)
                            if actual_rest_db:
                                actual_commute = optimizer.get_optimal_commute(
                                    intern.get_full_address(),
                                    actual_rest_db.get_full_address(),
                                    intern.transportation_method or 'driving'
                                )
                    except:
                        pass
            
            # Determine availability issue details
            availability_details = ""
            if is_availability_issue:
                intern = next((i for i in interns if intern_name in i.user.full_name), None)
                if intern:
                    if not intern.availability:
                        availability_details = "NO AVAILABILITY DATA"
                    else:
                        # Check if all False
                        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                        has_any = False
                        for day in days:
                            am = getattr(intern.availability, f'{day}_am')
                            pm = getattr(intern.availability, f'{day}_pm')
                            if am or pm:
                                has_any = True
                                break
                        
                        if not has_any:
                            availability_details = "ALL AVAILABILITY FALSE"
                        else:
                            availability_details = "INSUFFICIENT OVERLAP"
            
            analysis_data.append({
                'Intern Name': intern_name,
                'Actual Restaurant': actual_restaurant,
                'Algorithm Restaurant': 'None',
                'Actual Commute': actual_commute,
                'Algorithm Commute': 0,
                'Delta (min)': 0,
                'Delta %': 0,
                'Status': 'Actual Only (Availability Issue)',
                'Availability Issue': is_availability_issue,
                'Availability Details': availability_details if is_availability_issue else ''
            })
        
        print(f"Processed {len([d for d in analysis_data if d['Availability Issue']])} availability issue cases")
        
        print(f"\n3. CREATING FINAL ANALYSIS FILE")
        print("-" * 40)
        
        # Create DataFrame
        final_df = pd.DataFrame(analysis_data)
        
        # Sort by status and availability issues
        final_df['Sort_Order'] = final_df.apply(lambda x: (
            0 if x['Availability Issue'] else 1,  # Availability issues first
            x['Status'],  # Then by status
            x['Intern Name']  # Then by name
        ), axis=1)
        
        final_df = final_df.sort_values('Sort_Order').drop('Sort_Order', axis=1)
        
        # Save to CSV
        final_df.to_csv('final_complete_analysis_with_availability_issues.csv', index=False)
        print(f"Saved final analysis to 'final_complete_analysis_with_availability_issues.csv'")
        
        # Create summary
        print(f"\n4. CREATING SUMMARY")
        print("-" * 40)
        
        total_interns = len(analysis_data)
        assigned_count = len([d for d in analysis_data if d['Algorithm Restaurant'] != 'None'])
        availability_issue_count = len([d for d in analysis_data if d['Availability Issue']])
        actual_only_count = len([d for d in analysis_data if d['Status'] == 'Actual Only (Availability Issue)'])
        
        print(f"Total interns: {total_interns}")
        print(f"Algorithm assigned: {assigned_count}")
        print(f"Availability issues: {availability_issue_count}")
        print(f"Actual assignments only: {actual_only_count}")
        print(f"Coverage rate: {assigned_count / total_interns * 100:.1f}%")
        
        print(f"\nAvailability Issue Cases:")
        for data in analysis_data:
            if data['Availability Issue']:
                print(f"  {data['Intern Name']}: {data['Availability Details']}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Updating final analysis with availability issue highlights...")
    
    success = update_final_analysis()
    
    print(f"\n" + "="*80)
    print("FINAL ANALYSIS UPDATE COMPLETE")
    print("="*80)
    
    if success:
        print("SUCCESS: Final analysis updated with availability issue highlights")
        print("The remaining edge cases are now clearly marked")

if __name__ == "__main__":
    main()
