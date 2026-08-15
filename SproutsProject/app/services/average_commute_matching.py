"""
Enhanced Hungarian matching service that optimizes for AVERAGE commute time
instead of total commute time for better individual fairness
"""

import numpy as np
import time
from scipy.optimize import linear_sum_assignment
from typing import Dict, List, Tuple, Optional
from app.models import Intern, Restaurant, Internship
from app.services.slot import Slot
from app.services.enhanced_slot import EnhancedSlot
from app.services.commute_service import CommuteCache
from flask import current_app

class AverageCommuteMatchingService:
    """
    Enhanced matching service that optimizes for AVERAGE commute time
    while ensuring business rule compliance.
    """
    
    def __init__(self):
        self.commute_cache = CommuteCache('cached_commute.json')
    
    def find_optimal_assignments_avg_commute(self, interns: List[Intern], restaurants: List[Restaurant], 
                                           max_commute_minutes: int = 45) -> Dict:
        """
        Find optimal assignments that minimize AVERAGE commute time.
        
        Args:
            interns: List of interns seeking placements
            restaurants: List of available restaurants
            max_commute_minutes: Maximum allowed commute time
            
        Returns:
            Dictionary with assignments and statistics
        """
        print(f"Finding optimal assignments for {len(interns)} interns and {len(restaurants)} restaurants")
        print(f"Optimizing for AVERAGE commute with max {max_commute_minutes} minutes")
        
        start_time = time.time()
        
        # Step 1: Create cost matrix focusing on average commute
        cost_matrix, intern_names, restaurant_names = self._create_average_commute_matrix(
            interns, restaurants, max_commute_minutes
        )
        
        if not cost_matrix or not cost_matrix.size:
            return {
                'assignments': [],
                'total_interns': len(interns),
                'matched_interns': 0,
                'optimization_time': 0,
                'algorithm': 'average_commute_optimization'
            }
        
        # Step 2: Apply Hungarian algorithm for average optimization
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Step 3: Build assignments
        assignments = []
        matched_count = 0
        
        for i, j in zip(row_ind, col_ind):
            if i < len(intern_names) and j < len(restaurant_names):
                intern_name = intern_names[i]
                restaurant_name = restaurant_names[j]
                cost = cost_matrix[i, j]
                
                # Only include valid assignments (not infinite cost)
                if cost < 999999:
                    # Get detailed match info
                    intern = next((i for i in interns if i.user.full_name == intern_name), None)
                    restaurant = next((r for r in restaurants if r.name == restaurant_name), None)
                    
                    if intern and restaurant:
                        match_info = self._evaluate_match(intern, restaurant, max_commute_minutes, 12)
                        if match_info:
                            assignments.append({
                                'intern_name': intern_name,
                                'restaurant_name': restaurant_name,
                                'commute_minutes': match_info['commute_minutes'],
                                'total_overlap_hours': match_info['total_overlap_hours'],
                                'days_matched': match_info['days_matched'],
                                'match_score': match_info['match_score']
                            })
                            matched_count += 1
        
        # Step 4: Calculate statistics
        optimization_time = time.time() - start_time
        
        if assignments:
            avg_commute = sum(a['commute_minutes'] for a in assignments) / len(assignments)
            max_commute = max(a['commute_minutes'] for a in assignments)
            min_commute = min(a['commute_minutes'] for a in assignments)
        else:
            avg_commute = max_commute = min_commute = 0
        
        result = {
            'assignments': assignments,
            'total_interns': len(interns),
            'matched_interns': matched_count,
            'average_commute': avg_commute,
            'max_commute': max_commute,
            'min_commute': min_commute,
            'optimization_time': optimization_time,
            'algorithm': 'average_commute_optimization',
            'max_commute_constraint': max_commute_minutes
        }
        
        print(f"Average commute optimization completed in {optimization_time:.2f}s")
        print(f"Matched {matched_count}/{len(interns)} interns")
        print(f"Average commute: {avg_commute:.1f} minutes")
        print(f"Commute range: {min_commute}-{max_commute} minutes")
        
        return result
    
    def _create_average_commute_matrix(self, interns: List[Intern], restaurants: List[Restaurant], 
                                    max_commute_minutes: int) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Create cost matrix optimized for AVERAGE commute minimization.
        """
        print("Creating average commute cost matrix...")
        
        intern_names = [intern.user.full_name for intern in interns]
        restaurant_names = [restaurant.name for restaurant in restaurants]
        
        # Initialize cost matrix
        cost_matrix = np.full((len(interns), len(restaurants)), 999999.0)
        
        valid_matches = 0
        
        for i, intern in enumerate(interns):
            for j, restaurant in enumerate(restaurants):
                # Step 1: Check business rules compliance
                match = self._evaluate_match(intern, restaurant, max_commute_minutes, 12)
                
                if match:
                    # Step 2: Calculate cost based on average commute optimization
                    commute = match['commute_minutes']
                    hours = match['total_overlap_hours']
                    
                    # Cost function optimized for average:
                    # - Primary: commute time (lower is better)
                    # - Secondary: availability (higher is better)
                    # - Penalty for long commutes
                    
                    base_cost = commute
                    
                    # Add penalty for commutes > 30 minutes to discourage extreme values
                    if commute > 30:
                        penalty = (commute - 30) * 2  # Exponential penalty for long commutes
                        base_cost += penalty
                    
                    # Incentivize good availability (12+ hours gets bonus)
                    if hours >= 12:
                        availability_bonus = -5  # Reduce cost for good availability
                        base_cost += availability_bonus
                    
                    cost_matrix[i, j] = base_cost
                    valid_matches += 1
                else:
                    # Invalid match gets infinite cost
                    cost_matrix[i, j] = 999999.0
        
        print(f"Created cost matrix with {valid_matches} valid matches")
        return cost_matrix, intern_names, restaurant_names
    
    def _evaluate_match(self, intern: Intern, restaurant: Restaurant, max_commute: int, 
                        min_hours: int) -> Optional[Dict]:
        """
        Evaluate if intern-restaurant match is valid and calculate metrics.
        """
        try:
            # Check age restriction
            if restaurant.over_18_only and not intern.is_over_18():
                return None
            
            # Get availability
            intern_availability = self._parse_intern_availability(intern)
            restaurant_availability = self._parse_restaurant_availability(restaurant)
            
            # Calculate weekly overlap
            total_hours, schedule = self._calculate_weekly_overlap(intern_availability, restaurant_availability)
            
            # Check minimum requirements
            if total_hours < min_hours:
                return None
            
            # Count days with 4+ hours
            days_with_4_plus = sum(1 for day_slots in schedule.values() 
                                 if day_slots and sum(slot.duration() for slot in day_slots) >= 4)
            
            if days_with_4_plus < 2:
                return None
            
            # Calculate commute
            try:
                commute_info = self.commute_cache.get_commute(
                    intern.get_full_address(),
                    restaurant.get_full_address()
                )
                
                if not commute_info:
                    return None
                
                commute_minutes = commute_info.value // 60000  # Convert to minutes
                
                # Check max commute constraint
                if commute_minutes > max_commute:
                    return None
                    
            except Exception as e:
                current_app.logger.error(f"Commute calculation error: {e}")
                return None
            
            # Calculate match score (lower is better for cost matrix)
            match_score = commute_minutes - (total_hours * 0.5)  # Prefer more hours
            
            return {
                'commute_minutes': commute_minutes,
                'total_overlap_hours': total_hours,
                'days_matched': days_with_4_plus,
                'match_score': match_score,
                'schedule': schedule
            }
            
        except Exception as e:
            current_app.logger.error(f"Error evaluating match: {e}")
            return None
    
    def _parse_intern_availability(self, intern: Intern) -> Dict[str, List[Slot]]:
        """Parse intern availability using enhanced logic."""
        availability = {}
        
        # Try CSV first, fallback to database
        try:
            import pandas as pd
            csv_path = 'C:/Users/pierr/OneDrive/Documents/intern_avail_fall.csv'
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if intern.user.full_name in full_name or full_name in intern.user.full_name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = self._parse_time_slots_enhanced(time_str)
                        availability[day] = slots
                    break
        except:
            # Fallback to database availability
            if intern.availability:
                avail = intern.availability
                days = {
                    'Monday': (avail.monday_am, avail.monday_pm),
                    'Tuesday': (avail.tuesday_am, avail.tuesday_pm),
                    'Wednesday': (avail.wednesday_am, avail.wednesday_pm),
                    'Thursday': (avail.thursday_am, avail.thursday_pm),
                    'Friday': (avail.friday_am, avail.friday_pm),
                    'Saturday': (avail.saturday_am, avail.saturday_pm),
                    'Sunday': (avail.sunday_am, avail.sunday_pm),
                }
                
                for day, (am_slot, pm_slot) in days.items():
                    slots = []
                    if am_slot and am_slot != 'Unavailable':
                        slots.append(Slot(am_slot))
                    if pm_slot and pm_slot != 'Unavailable':
                        slots.append(Slot(pm_slot))
                    availability[day] = slots
        
        return availability
    
    def _parse_restaurant_availability(self, restaurant: Restaurant) -> Dict[str, List[Slot]]:
        """Parse restaurant availability using enhanced logic."""
        availability = {}
        
        try:
            import pandas as pd
            csv_path = 'C:/Users/pierr/OneDrive/Documents/chef_avail_fall.csv'
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                restaurant_name = row.get('Restaurant Name', '').strip()
                if restaurant.name in restaurant_name or restaurant_name in restaurant.name:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    
                    for day in days:
                        time_str = row.get(day, '').strip()
                        slots = self._parse_time_slots_enhanced(time_str)
                        availability[day] = slots
                    break
        except:
            # Fallback to default availability
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                availability[day] = [Slot("9AM-5PM")]  # Default 8-hour day
        
        return availability
    
    def _parse_time_slots_enhanced(self, time_str: str) -> List[Slot]:
        """Parse time slots using enhanced logic with 1-hour discontinuity tolerance."""
        if not time_str or time_str.strip() == '' or time_str.strip() == 'Unavailable':
            return []
        
        # Use EnhancedSlot for better merging
        enhanced_slots = EnhancedSlot.combineSlots(time_str, max_gap_hours=1, min_duration_hours=4)
        
        # Convert back to regular Slot objects for compatibility
        slots = []
        for enhanced_slot in enhanced_slots:
            slot = Slot(f"{enhanced_slot.start}-{enhanced_slot.end}")
            slots.append(slot)
        
        return slots
    
    def _calculate_weekly_overlap(self, intern_availability: Dict, restaurant_availability: Dict) -> Tuple[float, Dict]:
        """Calculate total weekly overlap hours and schedule."""
        total_hours = 0
        schedule = {}
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_overlaps = self._find_day_overlap(
                intern_availability.get(day, []),
                restaurant_availability.get(day, [])
            )
            
            if day_overlaps:
                day_hours = sum(slot.duration() for slot in day_overlaps)
                total_hours += day_hours
                schedule[day] = day_overlaps
        
        return total_hours, schedule
    
    def _find_day_overlap(self, intern_slots: List[Slot], restaurant_slots: List[Slot]) -> List[Slot]:
        """Find overlapping time slots between intern and restaurant for a day."""
        overlaps = []
        
        for intern_slot in intern_slots:
            for restaurant_slot in restaurant_slots:
                overlap = intern_slot.get_overlap(restaurant_slot)
                if overlap and overlap.duration() >= 1:  # Minimum 1 hour
                    overlaps.append(overlap)
        
        return overlaps

# Convenience function for backward compatibility
def find_optimal_assignments_average_commute(interns: List[Intern], restaurants: List[Restaurant], 
                                           max_commute_minutes: int = 45) -> Dict:
    """
    Convenience function to find optimal assignments using average commute optimization.
    """
    service = AverageCommuteMatchingService()
    return service.find_optimal_assignments_avg_commute(interns, restaurants, max_commute_minutes)
