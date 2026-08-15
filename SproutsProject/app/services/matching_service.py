"""
Matching service for pairing interns with restaurants based on availability and preferences.
Adapted from the original matching_algo.py and mapping.py.
"""

import copy
from typing import Dict, List, Tuple, Optional
from app.models import Intern, Restaurant, Internship
from app.services.slot import Slot
from app.services.commute_service import CommuteCache
from app.services.hungarian_matching import HungarianMatchingService
from flask import current_app

class MatchingService:
    """Service for matching interns with restaurants based on various criteria."""
    
    def __init__(self):
        self.commute_cache = CommuteCache()
        self.hungarian_service = HungarianMatchingService()
    
    def find_matches_for_intern(self, intern: Intern, available_internships: List[Internship], 
                               max_commute_minutes: int = 50) -> List[Dict]:
        """
        Find matching internships for a specific intern.
        
        Args:
            intern: Intern object
            available_internships: List of available internship opportunities
            max_commute_minutes: Maximum acceptable commute time in minutes
            
        Returns:
            List of match dictionaries with overlap and commute information
        """
        matches = []
        
        if not intern.availability:
            return matches
        
        for internship in available_internships:
            match = self._evaluate_intern_internship_match(intern, internship, max_commute_minutes)
            if match:
                matches.append(match)
        
        # Sort by total overlap time and commute time
        matches.sort(key=lambda x: (-x['total_overlap_hours'], x['commute_minutes']))
        
        return matches
    
    def find_matches_for_restaurant(self, restaurant_id: int, available_interns: List[Intern],
                                  internship_id: Optional[int] = None) -> List[Dict]:
        """
        Find matching interns for a restaurant's internships.
        
        Args:
            restaurant_id: Restaurant ID
            available_interns: List of available interns
            internship_id: Specific internship ID (optional)
            
        Returns:
            List of match dictionaries
        """
        matches = []
        
        # Get restaurant's internships
        if internship_id:
            internships = [Internship.query.get(internship_id)]
        else:
            internships = Internship.query.filter_by(
                restaurant_id=restaurant_id, 
                is_active=True
            ).all()
        
        for internship in internships:
            for intern in available_interns:
                match = self._evaluate_intern_internship_match(intern, internship)
                if match:
                    match['internship_id'] = internship.id
                    match['internship_title'] = internship.title
                    matches.append(match)
        
        return matches
    
    def _evaluate_intern_internship_match(self, intern: Intern, internship: Internship, 
                                        max_commute_minutes: int = 50) -> Optional[Dict]:
        """
        Evaluate if an intern matches with an internship.
        
        Returns:
            Dictionary with match details or None if no match
        """
        # Check age requirement
        if internship.restaurant.requires_over_18 and not intern.user.is_over_18:
            return None
        
        # Calculate commute
        commute = self.commute_cache.get_commute(
            intern.transportation_method or 'driving',
            intern.get_full_address(),
            internship.restaurant.get_full_address()
        )
        
        if commute.minutes > max_commute_minutes:
            return None
        
        # Check availability overlap
        intern_availability = self._parse_intern_availability(intern)
        restaurant_availability = self._parse_restaurant_availability(internship)
        
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
        
        # Require minimum overlap (at least 2 days, 8 hours total)
        if days_matched < 2 or total_overlap_hours < 8:
            return None
        
        return {
            'intern_id': intern.id,
            'intern_name': intern.user.full_name,
            'restaurant_id': internship.restaurant_id,
            'restaurant_name': internship.restaurant.name,
            'commute': commute.to_dict(),
            'commute_minutes': commute.minutes,
            'overlaps': {day: [slot.to_dict() for slot in slots] for day, slots in overlaps.items()},
            'total_overlap_hours': total_overlap_hours,
            'days_matched': days_matched,
            'match_score': self._calculate_match_score(total_overlap_hours, commute.minutes, days_matched)
        }
    
    def _parse_intern_availability(self, intern: Intern) -> Dict[str, List[Slot]]:
        """Parse intern's availability into Slot objects."""
        availability = {}
        
        if intern.availability:
            # Parse from InternAvailability model
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
                    slots.append(Slot("9AM-1PM"))
                if pm:
                    slots.append(Slot("1PM-9PM"))
                availability[day] = slots
        
        return availability
    
    def _parse_restaurant_availability(self, internship: Internship) -> Dict[str, List[Slot]]:
        """Parse restaurant's availability for an internship."""
        # This would be enhanced based on restaurant's operating hours
        # For now, assume standard restaurant hours
        availability = {}
        
        # Standard restaurant availability (can be customized per restaurant)
        standard_slots = [Slot("9AM-9PM")]  # All day availability
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            availability[day] = standard_slots.copy()
        
        return availability
    
    def _find_day_overlap(self, intern_slots: List[Slot], restaurant_slots: List[Slot]) -> List[Slot]:
        """Find overlapping time slots for a specific day."""
        overlaps = []
        
        for intern_slot in intern_slots:
            for restaurant_slot in restaurant_slots:
                overlap = intern_slot.get_overlap(restaurant_slot)
                if overlap.duration() >= 4:  # Minimum 4-hour shift
                    overlaps.append(overlap)
        
        return overlaps
    
    def _calculate_match_score(self, total_hours: float, commute_minutes: int, days_matched: int) -> float:
        """Calculate a match score based on various factors."""
        # Base score from hours and days
        base_score = (total_hours * 2) + (days_matched * 5)
        
        # Penalty for long commute
        commute_penalty = max(0, commute_minutes - 20) * 0.5
        
        # Bonus for excellent matches
        if total_hours >= 20 and days_matched >= 4:
            base_score += 10
        
        return max(0, base_score - commute_penalty)
    
    def find_optimal_hungarian_assignments(self, interns: List[Intern], restaurants: List[Restaurant]) -> Dict:
        """
        Find optimal assignments using Hungarian Algorithm to minimize total commute time.
        
        Args:
            interns: List of available interns
            restaurants: List of available restaurants
            
        Returns:
            Dictionary with optimal assignments and statistics
        """
        return self.hungarian_service.find_optimal_assignments(interns, restaurants)


class OptimizedMatchingService:
    """Advanced matching service that finds optimal intern-restaurant pairings."""
    
    def __init__(self):
        self.matching_service = MatchingService()
    
    def find_optimal_assignments(self, interns: List[Intern], internships: List[Internship],
                               max_assignments_per_restaurant: int = 1) -> List[Dict]:
        """
        Find optimal assignments using a simplified version of the mapping algorithm.
        
        Args:
            interns: List of available interns
            internships: List of available internships
            max_assignments_per_restaurant: Maximum interns per restaurant
            
        Returns:
            List of optimal assignments
        """
        assignments = []
        used_interns = set()
        used_internships = set()
        
        # Get all possible matches
        all_matches = []
        for intern in interns:
            matches = self.matching_service.find_matches_for_intern(intern, internships)
            for match in matches:
                match['intern_obj'] = intern
                all_matches.append(match)
        
        # Sort by match score (highest first)
        all_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Greedily assign best matches
        for match in all_matches:
            intern_id = match['intern_id']
            restaurant_id = match['restaurant_id']
            
            # Check if intern or restaurant already assigned
            if intern_id in used_interns:
                continue
            
            # Check restaurant capacity
            restaurant_assignments = sum(1 for a in assignments if a['restaurant_id'] == restaurant_id)
            if restaurant_assignments >= max_assignments_per_restaurant:
                continue
            
            # Make assignment
            assignments.append({
                'intern_id': intern_id,
                'intern_name': match['intern_name'],
                'restaurant_id': restaurant_id,
                'restaurant_name': match['restaurant_name'],
                'match_score': match['match_score'],
                'commute_minutes': match['commute_minutes'],
                'total_overlap_hours': match['total_overlap_hours'],
                'days_matched': match['days_matched'],
                'overlaps': match['overlaps']
            })
            
            used_interns.add(intern_id)
        
        return assignments
    
    def generate_matching_report(self, assignments: List[Dict]) -> Dict:
        """Generate a comprehensive matching report."""
        if not assignments:
            return {
                'total_matches': 0,
                'average_commute': 0,
                'average_hours': 0,
                'unmatched_interns': 0,
                'assignments': []
            }
        
        total_commute = sum(a['commute_minutes'] for a in assignments)
        total_hours = sum(a['total_overlap_hours'] for a in assignments)
        
        return {
            'total_matches': len(assignments),
            'average_commute': round(total_commute / len(assignments), 1),
            'average_hours': round(total_hours / len(assignments), 1),
            'total_hours': total_hours,
            'assignments': assignments,
            'success_rate': len(assignments)  # This would be calculated against total interns
        }
