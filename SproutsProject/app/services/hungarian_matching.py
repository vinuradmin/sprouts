"""
Hungarian Algorithm implementation for optimal intern-restaurant matching.
Minimizes total commute time while ensuring each intern gets at least 12 hours per week.
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

class HungarianMatchingService:
    """
    Optimal matching service using Hungarian Algorithm to minimize total commute time.
    """
    
    def __init__(self):
        self.commute_cache = CommuteCache('cached_commute.json')  # Use original filename
        self.min_hours_per_week = 12
        self.restaurant_capacity = 2  # How many interns per restaurant
    
    def find_optimal_assignments(self, interns: List[Intern], restaurants: List[Restaurant],
                           min_hours_per_week: int = 12, max_commute_minutes: int = 90,
                           restaurant_capacity: int = 2) -> Dict:
        """
        Optimize intern-restaurant assignments using Modified Hungarian Algorithm.
        Priority: 1) Maximize number of interns matched, 2) Minimize average commute time
        
        Args:
            interns: List of intern objects
            restaurants: List of restaurant objects
            min_hours_per_week: Minimum hours per intern per week
            max_commute_minutes: Maximum commute time in minutes
            restaurant_capacity: Maximum interns per restaurant
            
        Returns:
            Dictionary containing optimization results
        """
        if not interns or not restaurants:
            return {
                'assignments': [],
                'total_interns': len(interns) if interns else 0,
                'matched_interns': 0,
                'unmatched_interns': [{'id': intern.id, 'name': intern.user.full_name} for intern in interns] if interns else [],
                'total_commute_time': 0,
                'average_commute_time': 0,
                'optimization_time': 0,
                'algorithm': 'Modified Hungarian Algorithm (Max Matches First)'
            }
        
        start_time = time.time()
        
        # Step 1: Find maximum possible matches using maximum bipartite matching
        max_matches = self._find_maximum_matches(interns, restaurants, max_commute_minutes, 
                                                min_hours_per_week, restaurant_capacity)
        
        if not max_matches:
            return {
                'assignments': [],
                'total_interns': len(interns),
                'matched_interns': 0,
                'unmatched_interns': [{'id': intern.id, 'name': intern.user.full_name} for intern in interns],
                'total_commute_time': 0,
                'average_commute_time': 0,
                'optimization_time': time.time() - start_time,
                'algorithm': 'Modified Hungarian Algorithm (Max Matches First)'
            }
        
        # Step 2: Among all maximum matchings, find the one with minimum total commute
        best_assignment = self._optimize_commute_for_max_matches(max_matches, interns, restaurants,
                                                               max_commute_minutes, min_hours_per_week,
                                                               restaurant_capacity)
        
        optimization_time = time.time() - start_time
        best_assignment['optimization_time'] = optimization_time
        
        return best_assignment
    
    def _find_maximum_matches(self, interns: List[Intern], restaurants: List[Restaurant],
                            max_commute_minutes: int, min_hours_per_week: int, 
                            restaurant_capacity: int) -> List[Tuple]:
        """
        Find maximum number of possible matches using maximum bipartite matching.
        Returns list of (intern_index, restaurant_index) tuples.
        """
        # Build bipartite graph of valid matches
        valid_edges = []
        
        for i, intern in enumerate(interns):
            for j, restaurant in enumerate(restaurants):
                match_data = self._evaluate_match(intern, restaurant, max_commute_minutes, min_hours_per_week)
                if match_data:
                    # Add edges for restaurant capacity
                    for capacity_slot in range(restaurant_capacity):
                        expanded_restaurant_idx = j * restaurant_capacity + capacity_slot
                        valid_edges.append((i, expanded_restaurant_idx, match_data))
        
        if not valid_edges:
            return []
        
        # Use maximum bipartite matching to find maximum number of matches
        n_interns = len(interns)
        n_positions = len(restaurants) * restaurant_capacity
        
        # Create adjacency list for maximum matching
        graph = [[] for _ in range(n_interns)]
        for intern_idx, restaurant_idx, match_data in valid_edges:
            graph[intern_idx].append((restaurant_idx, match_data))
        
        # Find maximum matching using augmenting paths
        match_restaurant = [-1] * n_positions
        match_intern = [-1] * n_interns
        
        def dfs(intern_idx, visited):
            for restaurant_idx, match_data in graph[intern_idx]:
                if restaurant_idx in visited:
                    continue
                visited.add(restaurant_idx)
                
                if match_restaurant[restaurant_idx] == -1 or dfs(match_restaurant[restaurant_idx], visited):
                    match_restaurant[restaurant_idx] = intern_idx
                    match_intern[intern_idx] = restaurant_idx
                    return True
            return False
        
        # Find maximum matching
        for intern_idx in range(n_interns):
            visited = set()
            dfs(intern_idx, visited)
        
        # Convert back to original restaurant indices and collect match data
        max_matches = []
        for intern_idx in range(n_interns):
            if match_intern[intern_idx] != -1:
                expanded_restaurant_idx = match_intern[intern_idx]
                original_restaurant_idx = expanded_restaurant_idx // restaurant_capacity
                
                # Find the match data for this pair
                for edge_intern_idx, edge_restaurant_idx, match_data in valid_edges:
                    if (edge_intern_idx == intern_idx and 
                        edge_restaurant_idx == expanded_restaurant_idx):
                        max_matches.append((intern_idx, original_restaurant_idx, match_data))
                        break
        
        return max_matches
    
    def _optimize_commute_for_max_matches(self, max_matches: List[Tuple], interns: List[Intern],
                                        restaurants: List[Restaurant], max_commute_minutes: int,
                                        min_hours_per_week: int, restaurant_capacity: int) -> Dict:
        """
        Among all maximum matchings, find the one with minimum total commute time.
        """
        if not max_matches:
            return {
                'assignments': [],
                'total_interns': len(interns),
                'matched_interns': 0,
                'unmatched_interns': [{'id': intern.id, 'name': intern.user.full_name} for intern in interns],
                'total_commute_time': 0,
                'average_commute_time': 0,
                'optimization_time': 0,
                'algorithm': 'Modified Hungarian Algorithm (Max Matches First)'
            }
        
        # For the maximum matching found, calculate the optimal assignment
        assignments = []
        total_commute_time = 0
        matched_intern_ids = set()
        
        for intern_idx, restaurant_idx, match_data in max_matches:
            assignments.append(match_data)
            total_commute_time += match_data['commute_minutes']
            matched_intern_ids.add(match_data['intern_id'])
        
        # Calculate results
        matched_count = len(assignments)
        unmatched_interns = [intern for intern in interns if intern.id not in matched_intern_ids]
        average_commute = total_commute_time / matched_count if matched_count > 0 else 0
        
        return {
            'assignments': assignments,
            'total_interns': len(interns),
            'matched_interns': matched_count,
            'unmatched_interns': [{'id': intern.id, 'name': intern.user.full_name} for intern in unmatched_interns],
            'total_commute_time': total_commute_time,
            'average_commute_time': average_commute,
            'optimization_time': 0,  # Will be set by caller
            'algorithm': 'Modified Hungarian Algorithm (Max Matches First)'
        }
    
    def _get_valid_pairs(self, interns: List[Intern], restaurants: List[Restaurant]) -> List[Tuple]:
        """
        Get all valid intern-restaurant pairs that meet minimum hour requirements.
        
        Returns:
            List of tuples (intern, restaurant, commute_time, total_hours)
        """
        valid_pairs = []
        
        for intern in interns:
            if not intern.availability:
                continue
                
            intern_availability = self._parse_intern_availability(intern)
            
            for restaurant in restaurants:
                # Check age requirement
                if restaurant.requires_over_18 and not self._is_intern_over_18(intern):
                    continue
                
                # Calculate optimal commute across all transportation options
                try:
                    from app.services.transportation_optimizer import TransportationOptimizer
                    optimizer = TransportationOptimizer()
                    
                    optimal_commute = optimizer.get_optimal_commute(
                        intern.get_full_address(),
                        restaurant.get_full_address(),
                        intern.transportation_method or 'driving'
                    )
                    
                    # If no optimal commute found, skip this pair
                    if optimal_commute is None or optimal_commute > 120:
                        continue
                    
                    commute_minutes = optimal_commute
                    
                except Exception as e:
                    # Log the exception for debugging and skip this pair
                    current_app.logger.error(f"Optimal commute calculation failed for {intern.get_full_address()} -> {restaurant.get_full_address()}: {str(e)}")
                    continue
                
                # Check if they can work together for exactly 12 hours minimum
                restaurant_availability = self._parse_restaurant_availability(restaurant)
                total_hours, schedule = self._calculate_weekly_overlap(
                    intern_availability, restaurant_availability
                )
                
                # Require exactly 12 hours per intern - no more, no less
                if total_hours >= 12:
                    # Trim schedule to exactly 12 hours
                    trimmed_schedule, actual_hours = self._trim_schedule_to_hours(schedule, 12)
                    if actual_hours == 12:
                        valid_pairs.append((intern, restaurant, commute_minutes, actual_hours, trimmed_schedule))
        
        return valid_pairs
    
    def _create_cost_matrix(self, valid_pairs: List[Tuple]) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Create cost matrix for Hungarian Algorithm with average commute optimization.
        
        Returns:
            Tuple of (cost_matrix, intern_indices, restaurant_indices)
        """
        # Get unique interns and restaurants from valid pairs
        interns_in_pairs = list(set(pair[0] for pair in valid_pairs))
        restaurants_in_pairs = list(set(pair[1] for pair in valid_pairs))
        
        # Expand restaurants based on capacity
        expanded_restaurants = []
        restaurant_indices = []
        for restaurant in restaurants_in_pairs:
            for capacity_slot in range(self.restaurant_capacity):
                expanded_restaurants.append(restaurant)
                restaurant_indices.append(restaurant.id)
        
        intern_indices = [intern.id for intern in interns_in_pairs]
        
        # Create cost matrix (interns x restaurant_slots)
        n_interns = len(interns_in_pairs)
        n_restaurant_slots = len(expanded_restaurants)
        
        # Make matrix square by padding with dummy assignments
        matrix_size = max(n_interns, n_restaurant_slots)
        cost_matrix = np.full((matrix_size, matrix_size), float('inf'))
        
        # Fill in actual costs with average commute optimization
        for intern, restaurant, commute_time, total_hours, schedule in valid_pairs:
            intern_idx = interns_in_pairs.index(intern)
            
            # Find all slots for this restaurant
            for rest_idx, expanded_restaurant in enumerate(expanded_restaurants):
                if expanded_restaurant.id == restaurant.id:
                    # AVERAGE COMMUTE OPTIMIZATION: Add penalty for long commutes
                    base_cost = commute_time
                    
                    # Add exponential penalty for commutes > 25 minutes (lower threshold)
                    if commute_time > 25:
                        penalty = (commute_time - 25) * 5  # Heavy penalty for long commutes
                        base_cost += penalty
                    
                    # Add additional penalty for commutes > 35 minutes
                    if commute_time > 35:
                        extra_penalty = (commute_time - 35) * 10  # Very heavy penalty
                        base_cost += extra_penalty
                    
                    # Add extreme penalty for commutes > 40 minutes
                    if commute_time > 40:
                        extreme_penalty = (commute_time - 40) * 20  # Extreme penalty
                        base_cost += extreme_penalty
                    
                    # Give bonus for good availability (12+ hours)
                    if total_hours >= 12:
                        availability_bonus = -2  # Small bonus for good availability
                        base_cost += availability_bonus
                    
                    cost_matrix[intern_idx, rest_idx] = base_cost
        
        return cost_matrix, intern_indices, restaurant_indices
    
    def _parse_intern_availability(self, intern: Intern) -> Dict[str, List[Slot]]:
        """Parse intern's availability into Slot objects using actual CSV data."""
        from app.services.csv_data_loader import CSVDataLoader
        import csv
        import re
        
        availability = {}
        
        # Load actual CSV data for this intern
        try:
            with open('../intern_avail_fall.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    full_name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                    if intern.user.full_name in full_name or full_name in intern.user.full_name:
                        # Parse each day's availability from CSV
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        
                        for day in days:
                            time_str = row.get(day, '').strip()
                            slots = []
                            
                            if time_str and time_str != 'Unavailable' and time_str != '':
                                # Parse time slots using enhanced logic with 1-hour discontinuity tolerance
                                slots = self._parse_time_slots_enhanced(time_str)
                            
                            availability[day] = slots
                        break
                        
        except Exception as e:
            current_app.logger.error(f"Error parsing CSV availability for {intern.user.full_name}: {str(e)}")
            # Fallback to original method
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
                
                for day, (am, pm) in days.items():
                    slots = []
                    if am:
                        slots.append(Slot("9AM-1PM"))  # 4 hours
                    if pm:
                        slots.append(Slot("1PM-9PM"))  # 8 hours
                    availability[day] = slots
        
        return availability
    
    def _parse_restaurant_availability(self, restaurant: Restaurant) -> Dict[str, List[Slot]]:
        """Parse restaurant's availability into Slot objects using actual CSV data."""
        import csv
        import re
        
        availability = {}
        
        # Load actual CSV data for this restaurant
        try:
            with open('../chef_avail_fall.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    restaurant_name = row.get('Restaurant Name', '').strip()
                    if restaurant.name.strip() in restaurant_name or restaurant_name in restaurant.name.strip():
                        # Parse each day's availability from CSV
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        
                        for day in days:
                            time_str = row.get(day, '').strip()
                            slots = []
                            
                            if time_str and time_str != 'Unavailable' and time_str != '':
                                # Parse time slots using enhanced logic with 1-hour discontinuity tolerance
                                slots = self._parse_time_slots_enhanced(time_str)
                            
                            availability[day] = slots
                        break
                        
        except Exception as e:
            current_app.logger.error(f"Error parsing CSV availability for {restaurant.name}: {str(e)}")
            # Fallback to default availability (9AM-9PM)
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                availability[day] = [Slot("9AM-9PM")]
        
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
    
    def _combine_slots_original(self, individual_slots: List[str]) -> List[Slot]:
        """Combine slots using the exact same logic as the original algorithm."""
        if not individual_slots:
            return []
        
        slots = []
        prev_slot = None
        
        for slot_string in individual_slots:
            slot_string = slot_string.strip()
            if not slot_string:
                continue
                
            new_slot = Slot(slot_string)
            
            # If it's an all-day slot, just return it
            if new_slot.is_all_day():
                return [new_slot]
            
            # If slots are adjacent, combine them
            if prev_slot and prev_slot.is_adjacent(new_slot):
                prev_slot.add_and_combine(new_slot)
                continue
            
            # Only keep slots that are at least 4 hours long
            if prev_slot and prev_slot.duration() >= 4:
                slots.append(prev_slot)
            
            prev_slot = new_slot
        
        # Add the last slot if it's long enough
        if prev_slot and prev_slot.duration() >= 4:
            slots.append(prev_slot)
            
        return slots
    
    def _find_day_overlap(self, intern_slots: List[Slot], restaurant_slots: List[Slot]) -> List[Slot]:
        """Find overlapping time slots between intern and restaurant for a day."""
        overlaps = []
        
        for intern_slot in intern_slots:
            for restaurant_slot in restaurant_slots:
                overlap = intern_slot.get_overlap(restaurant_slot)
                if overlap:
                    overlaps.append(overlap)
        
        # Filter by minimum 4 hours per day (no merging needed)
        filtered_overlaps = [slot for slot in overlaps if slot.duration() >= 4]
        
        return filtered_overlaps
    
    def _merge_consecutive_slots(self, slots: List[Slot]) -> List[Slot]:
        """Merge consecutive time slots into continuous blocks."""
        if not slots:
            return slots
        
        # Sort slots by start time
        sorted_slots = sorted(slots, key=lambda x: x.start)
        
        merged = []
        current = sorted_slots[0]
        
        for next_slot in sorted_slots[1:]:
            # Check if slots are consecutive or overlapping
            if next_slot.start <= current.end:
                # Merge them by taking the max end time
                current_end = max(current.end, next_slot.end)
                current = Slot(f"{current.start}-{current_end}")
            else:
                # No overlap, add current and start new
                merged.append(current)
                current = next_slot
        
        merged.append(current)
        return merged
    
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
                schedule[day] = [slot.to_dict() for slot in day_overlaps]
        
        return total_hours, schedule
    
    def _trim_schedule_to_hours(self, schedule: Dict, target_hours: int) -> Tuple[Dict, int]:
        """
        Trim a schedule to exactly the target number of hours.
        
        Args:
            schedule: Dictionary of day -> list of slot dictionaries
            target_hours: Target number of hours (e.g., 12)
            
        Returns:
            Tuple of (trimmed_schedule, actual_hours)
        """
        trimmed_schedule = {}
        total_hours = 0
        
        # Sort days to prioritize certain days (e.g., weekdays first)
        day_priority = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in day_priority:
            if day not in schedule or total_hours >= target_hours:
                continue
                
            day_slots = schedule[day]
            trimmed_day_slots = []
            
            for slot_dict in day_slots:
                if total_hours >= target_hours:
                    break
                    
                slot_hours = slot_dict['duration']
                remaining_hours = target_hours - total_hours
                
                if slot_hours <= remaining_hours:
                    # Take the entire slot
                    trimmed_day_slots.append(slot_dict)
                    total_hours += slot_hours
                else:
                    # Trim the slot to fit exactly
                    trimmed_slot = slot_dict.copy()
                    trimmed_slot['end'] = trimmed_slot['start'] + remaining_hours
                    trimmed_slot['duration'] = remaining_hours
                    trimmed_day_slots.append(trimmed_slot)
                    total_hours += remaining_hours
                    break
            
            if trimmed_day_slots:
                trimmed_schedule[day] = trimmed_day_slots
        
        return trimmed_schedule, total_hours
    
    def _trim_overlaps_to_hours(self, overlaps: Dict, target_hours: int) -> Tuple[Dict, int]:
        """
        Trim overlap slots to exactly the target number of hours.
        
        Args:
            overlaps: Dictionary of day -> list of Slot objects
            target_hours: Target number of hours (e.g., 12)
            
        Returns:
            Tuple of (trimmed_overlaps, actual_hours)
        """
        trimmed_overlaps = {}
        total_hours = 0
        
        # Sort days to prioritize certain days (e.g., weekdays first)
        day_priority = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in day_priority:
            if day not in overlaps or total_hours >= target_hours:
                continue
                
            day_slots = overlaps[day]
            trimmed_day_slots = []
            
            for slot in day_slots:
                if total_hours >= target_hours:
                    break
                    
                slot_hours = slot.duration()
                remaining_hours = target_hours - total_hours
                
                if slot_hours <= remaining_hours:
                    # Take the entire slot
                    trimmed_day_slots.append(slot)
                    total_hours += slot_hours
                else:
                    # Trim the slot to fit exactly
                    from app.services.slot import Slot
                    trimmed_slot = Slot(f"{slot.start}-{slot.start + remaining_hours}")
                    trimmed_day_slots.append(trimmed_slot)
                    total_hours += remaining_hours
                    break
            
            if trimmed_day_slots:
                trimmed_overlaps[day] = trimmed_day_slots
        
        return trimmed_overlaps, total_hours
    
    def _calculate_match_score(self, total_hours: float, commute_minutes: int, days_matched: int) -> float:
        """Calculate match score based on hours, commute, and days."""
        # Higher score is better
        base_score = total_hours * 10  # 10 points per hour
        commute_penalty = commute_minutes * 2  # 2 points penalty per minute
        days_bonus = days_matched * 5  # 5 points bonus per day
        
        return max(0, base_score - commute_penalty + days_bonus)
    
    def _evaluate_match_raw(self, intern: Intern, restaurant: Restaurant, 
                        max_commute_minutes: int, min_hours_per_week: int) -> Optional[Dict]:
        """
        Evaluate all possible overlaps between intern and restaurant without trimming.
        Returns all available time slots, not just the optimized 12-hour schedule.
        """
        current_app.logger.info(f"Raw evaluation: {intern.user.full_name} -> {restaurant.name}")
        
        # Check age requirement
        if restaurant.requires_over_18 and not intern.is_over_18():
            current_app.logger.info(f"  Age requirement failed: restaurant requires 18+, intern is {intern.is_over_18()}")
            return None
        
        # Check if intern has availability data
        if not intern.availability:
            current_app.logger.info(f"  No availability data for intern {intern.user.full_name}")
            return None
        
        # Calculate optimal commute across all transportation options
        try:
            from app.services.transportation_optimizer import TransportationOptimizer
            optimizer = TransportationOptimizer()
            
            optimal_commute = optimizer.get_optimal_commute(
                intern.get_full_address(),
                restaurant.get_full_address(),
                intern.transportation_method or 'driving'
            )
            
            # If no optimal commute found, skip this pair
            if optimal_commute is None or optimal_commute > max_commute_minutes:
                current_app.logger.info(f"  No valid commute found or too long: {optimal_commute}")
                return None
            
        except Exception as e:
            current_app.logger.error(f"Optimal commute calculation failed: {str(e)}")
            return None
        
        # Check availability overlap
        intern_availability = self._parse_intern_availability(intern)
        restaurant_availability = self._parse_restaurant_availability(restaurant)
        
        overlaps = {}
        total_overlap_hours = 0
        days_matched = 0
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_overlap = self._find_day_overlap(
                intern_availability.get(day, []),
                restaurant_availability.get(day, [])
            )
            
            if day_overlap:
                overlaps[day] = day_overlap
                day_hours = sum(slot.duration() for slot in day_overlap)
                total_overlap_hours += day_hours
                days_matched += 1
                current_app.logger.info(f"  {day}: {day_hours} hours overlap")
        
        current_app.logger.info(f"  Total: {days_matched} days, {total_overlap_hours} hours")
        
        # Return all overlaps without any trimming or minimum hour requirements
        return {
            'intern_id': intern.id,
            'intern_name': intern.user.full_name,
            'restaurant_id': restaurant.id,
            'restaurant_name': restaurant.name,
            'commute_minutes': optimal_commute,
            'overlaps': {day: [slot.to_dict() for slot in slots] for day, slots in overlaps.items()},
            'total_overlap_hours': total_overlap_hours,
            'days_matched': days_matched,
            'match_score': self._calculate_match_score(total_overlap_hours, optimal_commute, days_matched)
        }
    
    def _evaluate_match(self, intern: Intern, restaurant: Restaurant, 
                      max_commute_minutes: int, min_hours_per_week: int) -> Optional[Dict]:
        """
        Evaluate if an intern-restaurant pair is a valid match.
        
        Returns:
            Dictionary with match data if valid, None otherwise
        """
        current_app.logger.info(f"Evaluating match: {intern.user.full_name} -> {restaurant.name}")
        
        # Check age requirement
        if restaurant.requires_over_18 and not intern.is_over_18():
            current_app.logger.info(f"  Age requirement failed: restaurant requires 18+, intern is {intern.is_over_18()}")
            return None
        
        # Check if intern has availability data
        if not intern.availability:
            current_app.logger.info(f"  No availability data for intern {intern.user.full_name}")
            return None
        
        # Calculate commute
        intern_address = intern.get_full_address()
        restaurant_address = restaurant.get_full_address()
        
        current_app.logger.info(f"  Calculating commute: {intern_address} -> {restaurant_address}")
        
        if not intern_address or not restaurant_address:
            current_app.logger.info(f"  Missing address data")
            return None
        
        # Calculate optimal commute across all transportation options
        try:
            from app.services.transportation_optimizer import TransportationOptimizer
            optimizer = TransportationOptimizer()
            
            optimal_commute = optimizer.get_optimal_commute(
                intern_address,
                restaurant_address,
                intern.transportation_method or 'driving'
            )
            
            current_app.logger.info(f"  Optimal commute time: {optimal_commute} minutes")
            
            if optimal_commute is None or optimal_commute > max_commute_minutes:
                current_app.logger.info(f"  No valid commute found or too long: {optimal_commute}")
                return None
            
        except Exception as e:
            current_app.logger.error(f"Optimal commute calculation failed: {str(e)}")
            return None
        
        # Check availability overlap
        intern_availability = self._parse_intern_availability(intern)
        restaurant_availability = self._parse_restaurant_availability(restaurant)
        
        current_app.logger.info(f"  Intern availability days: {list(intern_availability.keys())}")
        current_app.logger.info(f"  Restaurant availability days: {list(restaurant_availability.keys())}")
        
        overlaps = {}
        total_overlap_hours = 0
        days_matched = 0
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_overlap = self._find_day_overlap(
                intern_availability.get(day, []),
                restaurant_availability.get(day, [])
            )
            
            if day_overlap:
                overlaps[day] = day_overlap
                day_hours = sum(slot.duration() for slot in day_overlap)
                total_overlap_hours += day_hours
                days_matched += 1
                current_app.logger.info(f"  {day}: {day_hours} hours overlap")
        
        current_app.logger.info(f"  Total: {days_matched} days, {total_overlap_hours} hours")
        
        # Require exactly 12 hours per intern (minimum overlap of at least 2 days)
        if days_matched < 2 or total_overlap_hours < 12:
            current_app.logger.info(f"  Insufficient overlap: {days_matched} days < 2 or {total_overlap_hours} hours < 12")
            return None
        
        # Trim schedule to exactly 12 hours
        if total_overlap_hours > 12:
            trimmed_overlaps, actual_hours = self._trim_overlaps_to_hours(overlaps, 12)
            if actual_hours == 12:
                overlaps = trimmed_overlaps
                total_overlap_hours = actual_hours
            else:
                current_app.logger.info(f"  Could not trim to exactly 12 hours: got {actual_hours}")
                return None
        
        current_app.logger.info(f"  VALID MATCH FOUND!")
        
        return {
            'intern_id': intern.id,
            'intern_name': intern.user.full_name,
            'restaurant_id': restaurant.id,
            'restaurant_name': restaurant.name,
            'commute_minutes': optimal_commute,
            'overlaps': {day: [slot.to_dict() for slot in slots] for day, slots in overlaps.items()},
            'total_overlap_hours': total_overlap_hours,
            'days_matched': days_matched,
            'match_score': self._calculate_match_score(total_overlap_hours, optimal_commute, days_matched)
        }
    
    def _get_match_details(self, intern: Intern, restaurant: Restaurant) -> Optional[Dict]:
        """Get detailed match information for an intern-restaurant pair."""
        intern_availability = self._parse_intern_availability(intern)
        restaurant_availability = self._parse_restaurant_availability(restaurant)
        
        total_hours, schedule = self._calculate_weekly_overlap(
            intern_availability, restaurant_availability
        )
        
        if total_hours >= self.min_hours_per_week:
            return {
                'total_hours': total_hours,
                'schedule': schedule
            }
        
        return None
    
    def _is_intern_over_18(self, intern: Intern) -> bool:
        """Check if intern is over 18."""
        # This would need to be implemented based on intern's age field
        # For now, assume all interns are over 18
        return True
    
    def _calculate_efficiency_score(self, assignments: List[Dict], total_interns: int) -> float:
        """Calculate efficiency score for the matching."""
        if not assignments or total_interns == 0:
            return 0.0
        
        assignment_rate = len(assignments) / total_interns
        avg_commute = sum(a['commute_minutes'] for a in assignments) / len(assignments)
        
        # Score based on assignment rate and low commute times
        # Perfect score (100) = 100% assignment rate with 0 commute
        # Penalty for long commutes and unassigned interns
        efficiency = (assignment_rate * 100) - (avg_commute * 0.5)
        
        return max(0, min(100, efficiency))
    
    def set_restaurant_capacity(self, capacity: int):
        """Set how many interns each restaurant can take."""
        self.restaurant_capacity = max(1, capacity)
    
    def set_minimum_hours(self, hours: int):
        """Set minimum hours per week for interns."""
        self.min_hours_per_week = max(1, hours)
