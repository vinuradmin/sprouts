#!/usr/bin/env python3
"""
List restaurant options for Spring 2026 interns sorted by commute time
Uses the original matching algorithm from matching_service.py
"""

import sys
import os
import csv
import pandas as pd

# Add paths
sys.path.append('C:/Users/pierr/OneDrive/Documents')
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import Intern, Restaurant
from app.services.matching_service import MatchingService
from app.services.transportation_optimizer import TransportationOptimizer

def load_spring_2026_data():
    """Load Spring 2026 intern and restaurant data from CSV"""
    print("Loading Spring 2026 data from CSV files...")
    
    # Load intern data
    df_interns = pd.read_csv('intern_avail_spring_2026.csv')
    print(f"  Loaded {len(df_interns)} intern rows")
    
    # Load chef/restaurant data
    df_restaurants = pd.read_csv('chef_avail_spring_2026.csv')
    print(f"  Loaded {len(df_restaurants)} restaurant rows")
    
    return df_interns, df_restaurants

def find_restaurant_options_for_interns():
    """Find and list restaurant options for each Spring 2026 intern sorted by commute"""
    print("="*80)
    print("SPRING 2026 RESTAURANT OPTIONS BY COMMUTE TIME")
    print("="*80)
    
    app = create_app()
    app.app_context().push()
    
    # Load Spring 2026 data
    df_interns, df_restaurants = load_spring_2026_data()
    
    # Get all active restaurants from database
    all_restaurants = Restaurant.query.filter_by(is_active=True).all()
    print(f"\nFound {len(all_restaurants)} active restaurants in database")
    
    # Get transportation optimizer for commute calculations
    optimizer = TransportationOptimizer()
    
    # Prepare output data
    output_rows = []
    
    print(f"\n{'='*80}")
    print("PROCESSING INTERNS")
    print(f"{'='*80}\n")
    
    # Process each Spring 2026 intern
    for idx, intern_row in df_interns.iterrows():
        if idx == 0:  # Skip header row
            continue
            
        # Extract intern info using iloc for positional access
        timestamp = intern_row.iloc[0] if len(intern_row) > 0 else ''
        first_name = str(intern_row.iloc[1]).strip() if len(intern_row) > 1 else ''
        last_name = str(intern_row.iloc[2]).strip() if len(intern_row) > 2 else ''
        
        if not first_name or not last_name:
            continue
            
        intern_name = f"{first_name} {last_name}"
        print(f"\n{idx}. {intern_name}")
        print("-" * 40)
        
        # Try to find intern in database
        intern = Intern.query.join(Intern.user).filter(
            (Intern.user.has(full_name=intern_name)) |
            (Intern.user.has(first_name=first_name))
        ).first()
        
        if not intern:
            print(f"   WARNING: Intern not found in database")
            output_rows.append({
                'Intern Name': intern_name,
                'Restaurant': 'NOT IN DATABASE',
                'Commute (min)': '',
                'Status': 'Intern not found'
            })
            continue
        
        # Get intern address
        intern_address = intern.get_full_address()
        if not intern_address or intern_address == ', , ':
            print(f"   WARNING: No address for intern")
            output_rows.append({
                'Intern Name': intern_name,
                'Restaurant': 'NO ADDRESS',
                'Commute (min)': '',
                'Status': 'Missing address'
            })
            continue
        
        # Calculate commute to each restaurant
        restaurant_options = []
        
        for restaurant in all_restaurants:
            restaurant_address = restaurant.get_full_address()
            if not restaurant_address or restaurant_address == ', , ':
                continue
            
            try:
                # Calculate commute time
                commute_minutes = optimizer.get_optimal_commute(
                    intern_address,
                    restaurant_address,
                    intern.transportation_method or 'driving'
                )
                
                # Check age restriction
                age_ok = True
                if restaurant.requires_over_18 and not intern.user.is_over_18:
                    age_ok = False
                
                restaurant_options.append({
                    'name': restaurant.name,
                    'commute': commute_minutes,
                    'age_ok': age_ok
                })
            except Exception as e:
                print(f"   Error calculating commute to {restaurant.name}: {e}")
                continue
        
        # Sort by commute time
        restaurant_options.sort(key=lambda x: x['commute'])
        
        print(f"   Found {len(restaurant_options)} restaurant options")
        print(f"   Top 5 by commute:")
        
        # Add top options to output
        for i, option in enumerate(restaurant_options[:10]):  # Top 10
            status = "OK" if option['age_ok'] else "AGE RESTRICTED"
            
            if i < 5:  # Print top 5
                print(f"      {i+1}. {option['name']}: {option['commute']} min ({status})")
            
            output_rows.append({
                'Intern Name': intern_name,
                'Restaurant': option['name'],
                'Commute (min)': option['commute'],
                'Rank': i + 1,
                'Status': status
            })
    
    # Save to CSV
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}\n")
    
    output_file = 'spring_2026_restaurant_options_by_commute.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Intern Name', 'Restaurant', 'Commute (min)', 'Rank', 'Status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"Saved {len(output_rows)} rows to: {output_file}")
    
    # Create summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    unique_interns = len(set(row['Intern Name'] for row in output_rows if row['Restaurant'] not in ['NOT IN DATABASE', 'NO ADDRESS']))
    print(f"Interns processed: {unique_interns}")
    print(f"Total restaurant options listed: {len(output_rows)}")
    print(f"Average options per intern: {len(output_rows) / unique_interns if unique_interns > 0 else 0:.1f}")
    
    return output_file

def main():
    """Main function"""
    print("Finding restaurant options for Spring 2026 interns...")
    print("Sorted by commute time using original matching algorithm\n")
    
    output_file = find_restaurant_options_for_interns()
    
    print(f"\n{'='*80}")
    print("COMPLETE")
    print(f"{'='*80}")
    print(f"\nResults saved to: {output_file}")
    print("Each intern has their restaurant options listed, sorted by commute time")

if __name__ == "__main__":
    main()
