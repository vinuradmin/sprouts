#!/usr/bin/env python3
"""
Verify that all Flask Hungarian algorithm matches appear in the original algorithm options
"""

import csv
import json
import re
from collections import defaultdict
from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

def read_csv_dict(filename):
    """Read CSV file into list of dictionaries"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

def parse_original_results():
    """Parse the original intern_to_restaurant.csv results"""
    print("=== PARSING ORIGINAL RESULTS ===")
    
    results_data = read_csv_dict('intern_to_restaurant.csv')
    original_options = {}
    
    for row in results_data:
        intern_name = row.get('Intern Name', '').strip()
        if not intern_name:
            continue
            
        original_options[intern_name] = set()
        
        # Parse each day's matches
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_matches = row.get(day, '').strip()
            if day_matches:
                # Parse restaurant matches for this day
                lines = day_matches.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Extract restaurant name, commute time, and availability
                        match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                        if match:
                            restaurant = match.group(1).strip()
                            original_options[intern_name].add(restaurant)
    
    print(f"Parsed options for {len(original_options)} interns")
    return original_options

def get_flask_matches():
    """Get Flask Hungarian algorithm matches"""
    print("\n=== GETTING FLASK MATCHES ===")
    
    app = create_app()
    app.app_context().push()
    
    service = HungarianMatchingService()
    interns = Intern.query.all()
    restaurants = Restaurant.query.all()
    
    print(f"Found {len(interns)} interns and {len(restaurants)} restaurants in database")
    
    # Run matching algorithm
    matches = service.find_optimal_assignments(interns, restaurants)
    
    flask_matches = {}
    for assignment in matches.get('assignments', []):
        intern_id = assignment.get('intern_id')
        intern = Intern.query.get(intern_id)
        if intern:
            intern_name = intern.user.full_name
            restaurant_id = assignment.get('restaurant_id')
            restaurant = Restaurant.query.get(restaurant_id)
            if restaurant:
                flask_matches[intern_name] = restaurant.name
    
    print(f"Flask algorithm matched {len(flask_matches)} interns")
    return flask_matches

def verify_matches(original_options, flask_matches):
    """Verify that all Flask matches appear in original options"""
    print("\n=== VERIFYING MATCHES ===")
    
    verification_results = {
        'verified': [],
        'not_found': [],
        'name_mismatch': [],
        'total_flask_matches': len(flask_matches),
        'total_original_interns': len(original_options)
    }
    
    for flask_intern, flask_restaurant in flask_matches.items():
        # Try to find the intern in original data
        original_intern_found = False
        restaurant_found = False
        
        # Direct match
        if flask_intern in original_options:
            original_intern_found = True
            if flask_restaurant in original_options[flask_intern]:
                restaurant_found = True
                verification_results['verified'].append({
                    'intern': flask_intern,
                    'restaurant': flask_restaurant
                })
            else:
                verification_results['not_found'].append({
                    'intern': flask_intern,
                    'restaurant': flask_restaurant,
                    'available_options': list(original_options[flask_intern])[:5]  # Show first 5 options
                })
        else:
            # Try to find similar names (accounting for spacing differences)
            for original_intern in original_options.keys():
                # Normalize names for comparison
                normalized_flask = flask_intern.replace('  ', ' ').strip()
                normalized_original = original_intern.replace('  ', ' ').strip()
                
                if normalized_flask == normalized_original or flask_intern.strip() == original_intern.strip():
                    original_intern_found = True
                    if flask_restaurant in original_options[original_intern]:
                        restaurant_found = True
                        verification_results['verified'].append({
                            'intern': flask_intern,
                            'restaurant': flask_restaurant,
                            'matched_as': original_intern
                        })
                    else:
                        verification_results['not_found'].append({
                            'intern': flask_intern,
                            'restaurant': flask_restaurant,
                            'matched_as': original_intern,
                            'available_options': list(original_options[original_intern])[:5]
                        })
                    break
            
            if not original_intern_found:
                verification_results['name_mismatch'].append({
                    'intern': flask_intern,
                    'restaurant': flask_restaurant
                })
    
    # Print results
    print(f"\nVerification Summary:")
    print(f"Verified matches: {len(verification_results['verified'])}")
    print(f"Restaurant not in original options: {len(verification_results['not_found'])}")
    print(f"Name mismatch: {len(verification_results['name_mismatch'])}")
    
    verification_rate = len(verification_results['verified']) / len(flask_matches) * 100
    print(f"Verification rate: {verification_rate:.1f}%")
    
    # Show details for non-verified matches
    if verification_results['not_found']:
        print(f"\nMatches where restaurant not found in original options:")
        for item in verification_results['not_found'][:5]:  # Show first 5
            intern = item['intern']
            restaurant = item['restaurant']
            matched_as = item.get('matched_as', intern)
            options = item['available_options']
            print(f"  {intern} -> {restaurant}")
            print(f"    Matched as: {matched_as}")
            print(f"    Available options: {', '.join(options)}")
            print()
    
    if verification_results['name_mismatch']:
        print(f"\nName mismatches:")
        for item in verification_results['name_mismatch']:
            print(f"  {item['intern']} -> {item['restaurant']}")
    
    return verification_results

def main():
    """Main verification function"""
    print("Starting match verification...")
    
    # Parse original results
    original_options = parse_original_results()
    
    # Get Flask matches
    flask_matches = get_flask_matches()
    
    # Verify matches
    verification_results = verify_matches(original_options, flask_matches)
    
    # Save results
    with open('match_verification.json', 'w') as f:
        json.dump(verification_results, f, indent=2, default=str)
    
    print(f"\n=== VERIFICATION COMPLETE ===")
    print(f"Results saved to match_verification.json")
    
    return verification_results

if __name__ == "__main__":
    main()
