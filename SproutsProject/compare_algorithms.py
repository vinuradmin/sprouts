#!/usr/bin/env python3
"""
Comprehensive comparison between original CSV-based algorithm and Flask implementation
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
    parsed_matches = {}
    
    for row in results_data:
        intern_name = row.get('Intern Name', '').strip()
        if not intern_name:
            continue
            
        parsed_matches[intern_name] = {}
        
        # Parse each day's matches
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_matches = row.get(day, '').strip()
            if day_matches:
                # Parse restaurant matches for this day
                matches = []
                lines = day_matches.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Extract restaurant name, commute time, and availability
                        match = re.match(r'([^:]+)\s*\(([^)]+)\):\s*\[(\d+)-(\d+)\]', line)
                        if match:
                            restaurant = match.group(1).strip()
                            commute = match.group(2).strip()
                            start_time = int(match.group(3))
                            end_time = int(match.group(4))
                            
                            matches.append({
                                'restaurant': restaurant,
                                'commute': commute,
                                'availability': (start_time, end_time)
                            })
                
                if matches:
                    parsed_matches[intern_name][day] = matches
    
    print(f"Parsed matches for {len(parsed_matches)} interns")
    return parsed_matches

def run_flask_algorithm():
    """Run the Flask implementation matching algorithm"""
    print("\n=== RUNNING FLASK ALGORITHM ===")
    
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
            flask_matches[intern_name] = assignment
    
    print(f"Flask algorithm processed {len(flask_matches)} interns")
    return flask_matches

def compare_algorithms(original_matches, flask_matches):
    """Compare results between original and Flask algorithms"""
    print("\n=== COMPARING ALGORITHMS ===")
    
    # Statistics
    original_interns = set(original_matches.keys())
    flask_interns = set(flask_matches.keys())
    
    common_interns = original_interns & flask_interns
    original_only = original_interns - flask_interns
    flask_only = flask_interns - original_interns
    
    print(f"Interns in original only: {len(original_only)}")
    print(f"Interns in Flask only: {len(flask_only)}")
    print(f"Common interns: {len(common_interns)}")
    
    # Detailed comparison for common interns
    print("\n=== DETAILED COMPARISON ===")
    
    for intern_name in list(common_interns)[:5]:  # Show first 5 for brevity
        print(f"\nIntern: {intern_name}")
        
        original = original_matches.get(intern_name, {})
        flask = flask_matches.get(intern_name, {})
        
        print("Original matches:")
        for day, matches in original.items():
            if matches:
                print(f"  {day}: {len(matches)} matches")
                for match in matches[:2]:  # Show first 2 matches
                    print(f"    - {match['restaurant']} ({match['commute']})")
        
        print("Flask matches:")
        restaurant = Restaurant.query.get(flask.get('restaurant_id'))
        if restaurant:
            score = flask.get('score', 0)
            total_hours = flask.get('total_hours', 0)
            print(f"  - {restaurant.name} (Score: {score:.2f}, Hours: {total_hours})")
    
    return {
        'original_count': len(original_matches),
        'flask_count': len(flask_matches),
        'common_count': len(common_interns),
        'original_only': list(original_only),
        'flask_only': list(flask_only)
    }

def main():
    """Main comparison function"""
    print("Starting algorithm comparison...")
    
    # Parse original results
    original_matches = parse_original_results()
    
    # Run Flask algorithm
    flask_matches = run_flask_algorithm()
    
    # Compare results
    comparison_stats = compare_algorithms(original_matches, flask_matches)
    
    # Save comparison results
    with open('algorithm_comparison.json', 'w') as f:
        json.dump({
            'stats': comparison_stats,
            'original_sample': dict(list(original_matches.items())[:3]),
            'flask_sample': dict(list(flask_matches.items())[:3])
        }, f, indent=2, default=str)
    
    print(f"\n=== COMPARISON COMPLETE ===")
    print(f"Results saved to algorithm_comparison.json")
    print(f"Original algorithm: {comparison_stats['original_count']} interns")
    print(f"Flask algorithm: {comparison_stats['flask_count']} interns")
    print(f"Common interns: {comparison_stats['common_count']}")

if __name__ == "__main__":
    main()
