"""
Analyze all configurable parameters and their impact on matching results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    read_sheet_data,
    filter_by_cohort,
    rows_to_dict_list,
    Intern,
    Chef,
    Commute,
    load_commute_cache
)

def test_parameter_impact():
    """Test impact of different parameter configurations"""
    
    print("=" * 80)
    print("MATCHING ALGORITHM PARAMETER ANALYSIS")
    print("=" * 80)
    print()
    
    # Load cache
    load_commute_cache()
    
    # Read and filter data
    intern_data = read_sheet_data('Intern Availabilities')
    chef_data = read_sheet_data('Chef Availabilities')
    
    cohort_name = "Summer 2026"
    filtered_interns = filter_by_cohort(intern_data, cohort_name)
    filtered_chefs = filter_by_cohort(chef_data, cohort_name)
    
    # Convert to dicts and create objects
    intern_dicts = rows_to_dict_list(filtered_interns)
    chef_dicts = rows_to_dict_list(filtered_chefs)
    
    # Create interns and chefs
    interns = {}
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except:
            pass
    
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.restaurantName] = chef
        except:
            pass
    
    print(f"Testing {len(interns)} interns against {len(chefs)} restaurants")
    print()
    
    # Current baseline
    baseline_matches = calculate_matches(interns, chefs, 
                                        min_overlap_hours=4, 
                                        commute_threshold_minutes=180,
                                        enforce_age=True)
    
    print("=" * 80)
    print("CURRENT CONFIGURATION (BASELINE)")
    print("=" * 80)
    print(f"  Minimum overlap: 4 hours")
    print(f"  Commute threshold: 180 minutes")
    print(f"  Age restrictions: Enforced")
    print(f"  Total matches: {baseline_matches}")
    print(f"  Avg per intern: {baseline_matches / len(interns):.1f}")
    print()
    
    # Test different configurations
    scenarios = []
    
    # Scenario 1: Reduce minimum overlap to 3 hours
    matches_3hr = calculate_matches(interns, chefs, 
                                    min_overlap_hours=3, 
                                    commute_threshold_minutes=180,
                                    enforce_age=True)
    scenarios.append({
        'name': 'Reduce overlap to 3 hours',
        'matches': matches_3hr,
        'change': matches_3hr - baseline_matches,
        'impact': 'HIGH' if matches_3hr - baseline_matches > 20 else 'MEDIUM' if matches_3hr - baseline_matches > 10 else 'LOW'
    })
    
    # Scenario 2: Reduce minimum overlap to 2 hours
    matches_2hr = calculate_matches(interns, chefs, 
                                    min_overlap_hours=2, 
                                    commute_threshold_minutes=180,
                                    enforce_age=True)
    scenarios.append({
        'name': 'Reduce overlap to 2 hours',
        'matches': matches_2hr,
        'change': matches_2hr - baseline_matches,
        'impact': 'HIGH' if matches_2hr - baseline_matches > 20 else 'MEDIUM' if matches_2hr - baseline_matches > 10 else 'LOW'
    })
    
    # Scenario 3: Disable age restrictions
    matches_no_age = calculate_matches(interns, chefs, 
                                       min_overlap_hours=4, 
                                       commute_threshold_minutes=180,
                                       enforce_age=False)
    scenarios.append({
        'name': 'Disable age restrictions',
        'matches': matches_no_age,
        'change': matches_no_age - baseline_matches,
        'impact': 'HIGH' if matches_no_age - baseline_matches > 20 else 'MEDIUM' if matches_no_age - baseline_matches > 10 else 'LOW'
    })
    
    # Scenario 4: Combination - 3 hours + no age
    matches_combo = calculate_matches(interns, chefs, 
                                     min_overlap_hours=3, 
                                     commute_threshold_minutes=180,
                                     enforce_age=False)
    scenarios.append({
        'name': '3-hour overlap + no age restrictions',
        'matches': matches_combo,
        'change': matches_combo - baseline_matches,
        'impact': 'HIGH' if matches_combo - baseline_matches > 20 else 'MEDIUM' if matches_combo - baseline_matches > 10 else 'LOW'
    })
    
    # Display results
    print("=" * 80)
    print("SCENARIO ANALYSIS")
    print("=" * 80)
    print()
    
    for scenario in scenarios:
        change_pct = (scenario['change'] / baseline_matches * 100) if baseline_matches > 0 else 0
        print(f"{scenario['name']}")
        print(f"  Total matches: {scenario['matches']}")
        print(f"  Change: +{scenario['change']} (+{change_pct:.1f}%)")
        print(f"  Impact: {scenario['impact']}")
        print()
    
    # Find best scenario
    best_scenario = max(scenarios, key=lambda x: x['matches'])
    
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    print(f"HIGHEST IMPACT: {best_scenario['name']}")
    print(f"  Would add +{best_scenario['change']} matches (+{(best_scenario['change']/baseline_matches*100):.1f}%)")
    print()
    
    # Specific recommendations
    print("PARAMETER IMPACT RANKING:")
    print()
    
    sorted_scenarios = sorted(scenarios, key=lambda x: x['change'], reverse=True)
    for i, scenario in enumerate(sorted_scenarios, 1):
        change_pct = (scenario['change'] / baseline_matches * 100) if baseline_matches > 0 else 0
        print(f"  {i}. {scenario['name']}: +{scenario['change']} matches (+{change_pct:.1f}%)")
    
    print()
    print("=" * 80)
    print("DETAILED BREAKDOWN")
    print("=" * 80)
    print()
    
    # Show filter breakdown for current config
    age_filtered, schedule_filtered, commute_filtered = get_filter_breakdown(
        interns, chefs, min_overlap_hours=4, commute_threshold_minutes=180, enforce_age=True
    )
    
    total_potential = len(interns) * len(chefs)
    
    print(f"Total potential combinations: {total_potential}")
    print(f"Filtered by age: {age_filtered} ({(age_filtered/total_potential*100):.1f}%)")
    print(f"Filtered by schedule: {schedule_filtered} ({(schedule_filtered/total_potential*100):.1f}%)")
    print(f"Filtered by commute: {commute_filtered} ({(commute_filtered/total_potential*100):.1f}%)")
    print(f"Valid matches: {baseline_matches} ({(baseline_matches/total_potential*100):.1f}%)")
    print()
    
    print("BIGGEST BOTTLENECK:")
    bottlenecks = [
        ('Age restrictions', age_filtered),
        ('Schedule conflicts', schedule_filtered),
        ('Commute distance', commute_filtered)
    ]
    bottlenecks.sort(key=lambda x: x[1], reverse=True)
    
    for name, count in bottlenecks:
        pct = (count / total_potential * 100)
        print(f"  {name}: {count} ({pct:.1f}%)")
    
    print()
    print("=" * 80)

def calculate_matches(interns, chefs, min_overlap_hours, commute_threshold_minutes, enforce_age):
    """Calculate total matches with given parameters"""
    total_matches = 0
    commute_threshold_seconds = commute_threshold_minutes * 60
    
    for intern in interns.values():
        for chef in chefs.values():
            # Check age
            if enforce_age and chef.chefOver18Only and not intern.internOver18:
                continue
            
            # Check schedule overlap
            has_overlap = False
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern.availability[day]
                chef_slots = chef.availability[day]
                
                if not intern_slots or not chef_slots:
                    continue
                
                for chef_slot in chef_slots:
                    for intern_slot in intern_slots:
                        overlap = chef_slot.getOverlap(intern_slot)
                        if overlap.duration() >= min_overlap_hours:
                            has_overlap = True
                            break
                    if has_overlap:
                        break
                if has_overlap:
                    break
            
            if not has_overlap:
                continue
            
            # Check commute
            try:
                commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                if commute.value > commute_threshold_seconds:
                    continue
            except:
                continue
            
            total_matches += 1
    
    return total_matches

def get_filter_breakdown(interns, chefs, min_overlap_hours, commute_threshold_minutes, enforce_age):
    """Get breakdown of how many combinations are filtered by each criterion"""
    age_filtered = 0
    schedule_filtered = 0
    commute_filtered = 0
    commute_threshold_seconds = commute_threshold_minutes * 60
    
    for intern in interns.values():
        for chef in chefs.values():
            # Check age
            if enforce_age and chef.chefOver18Only and not intern.internOver18:
                age_filtered += 1
                continue
            
            # Check schedule overlap
            has_overlap = False
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                intern_slots = intern.availability[day]
                chef_slots = chef.availability[day]
                
                if not intern_slots or not chef_slots:
                    continue
                
                for chef_slot in chef_slots:
                    for intern_slot in intern_slots:
                        overlap = chef_slot.getOverlap(intern_slot)
                        if overlap.duration() >= min_overlap_hours:
                            has_overlap = True
                            break
                    if has_overlap:
                        break
                if has_overlap:
                    break
            
            if not has_overlap:
                schedule_filtered += 1
                continue
            
            # Check commute
            try:
                commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                if commute.value > commute_threshold_seconds:
                    commute_filtered += 1
                    continue
            except:
                commute_filtered += 1
                continue
    
    return age_filtered, schedule_filtered, commute_filtered

if __name__ == "__main__":
    test_parameter_impact()
