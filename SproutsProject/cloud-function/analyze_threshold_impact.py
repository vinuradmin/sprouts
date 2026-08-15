"""
Analyze the impact of different commute thresholds on match counts
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

def analyze_threshold_impact():
    """Test different commute thresholds and their impact"""
    
    print("=" * 80)
    print("COMMUTE THRESHOLD IMPACT ANALYSIS")
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
    
    # Test different thresholds (in minutes)
    thresholds = [120, 150, 180, 240]
    
    # Store results for each threshold
    threshold_results = {}
    
    for threshold_minutes in thresholds:
        threshold_seconds = threshold_minutes * 60
        
        total_matches = 0
        intern_match_counts = {}
        commute_filtered_count = 0
        
        for intern_name, intern in interns.items():
            matches_for_intern = 0
            
            for rest_name, chef in chefs.items():
                # Check age
                if chef.chefOver18Only and not intern.internOver18:
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
                            if overlap.duration() >= 4:
                                has_overlap = True
                                break
                        if has_overlap:
                            break
                    if has_overlap:
                        break
                
                if not has_overlap:
                    continue
                
                # Check commute with this threshold
                try:
                    commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chef.getFullAddress())
                    
                    if commute.value > threshold_seconds:
                        commute_filtered_count += 1
                        continue
                    
                    matches_for_intern += 1
                    total_matches += 1
                except:
                    continue
            
            intern_match_counts[intern_name] = matches_for_intern
        
        threshold_results[threshold_minutes] = {
            'total_matches': total_matches,
            'avg_matches_per_intern': total_matches / len(interns) if interns else 0,
            'intern_counts': intern_match_counts,
            'commute_filtered': commute_filtered_count
        }
    
    # Display results
    print("=" * 80)
    print("RESULTS BY THRESHOLD")
    print("=" * 80)
    print()
    
    baseline_threshold = 120
    baseline_total = threshold_results[baseline_threshold]['total_matches']
    
    for threshold in thresholds:
        result = threshold_results[threshold]
        total = result['total_matches']
        avg = result['avg_matches_per_intern']
        
        increase = total - baseline_total
        increase_pct = (increase / baseline_total * 100) if baseline_total > 0 else 0
        
        marker = " (CURRENT)" if threshold == baseline_threshold else ""
        
        print(f"{threshold} minutes{marker}:")
        print(f"  Total matches: {total}")
        print(f"  Avg per intern: {avg:.1f}")
        
        if threshold != baseline_threshold:
            print(f"  Increase from {baseline_threshold}min: +{increase} matches (+{increase_pct:.1f}%)")
        
        print()
    
    # Show per-intern breakdown for key thresholds
    print("=" * 80)
    print("PER-INTERN COMPARISON (120min vs 180min)")
    print("=" * 80)
    print()
    
    print(f"{'Intern Name':<30} {'120min':<10} {'180min':<10} {'Gain':<10}")
    print("-" * 60)
    
    for intern_name in sorted(interns.keys()):
        count_120 = threshold_results[120]['intern_counts'][intern_name]
        count_180 = threshold_results[180]['intern_counts'][intern_name]
        gain = count_180 - count_120
        
        gain_str = f"+{gain}" if gain > 0 else str(gain)
        print(f"{intern_name:<30} {count_120:<10} {count_180:<10} {gain_str:<10}")
    
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print()
    
    # Calculate recommendation
    increase_150 = threshold_results[150]['total_matches'] - baseline_total
    increase_180 = threshold_results[180]['total_matches'] - baseline_total
    increase_240 = threshold_results[240]['total_matches'] - baseline_total
    
    increase_150_pct = (increase_150 / baseline_total * 100) if baseline_total > 0 else 0
    increase_180_pct = (increase_180 / baseline_total * 100) if baseline_total > 0 else 0
    increase_240_pct = (increase_240 / baseline_total * 100) if baseline_total > 0 else 0
    
    if increase_150 > 5:
        print(f"RECOMMENDED: Increase to 150 minutes")
        print(f"  Gain: +{increase_150} matches (+{increase_150_pct:.1f}%)")
        print(f"  Rationale: Moderate increase, reasonable for public transit in Bay Area")
    elif increase_180 > 10:
        print(f"RECOMMENDED: Increase to 180 minutes (3 hours)")
        print(f"  Gain: +{increase_180} matches (+{increase_180_pct:.1f}%)")
        print(f"  Rationale: Significant increase in matches, still reasonable for dedicated internship")
    else:
        print(f"RECOMMENDED: Keep at 120 minutes")
        print(f"  Rationale: Minimal gains from increasing threshold")
        print(f"    150min: +{increase_150} matches (+{increase_150_pct:.1f}%)")
        print(f"    180min: +{increase_180} matches (+{increase_180_pct:.1f}%)")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    analyze_threshold_impact()
