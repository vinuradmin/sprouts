"""
Transportation optimization service to handle multiple transportation options
"""

import re
from typing import List, Optional
from app.services.commute_service import CommuteCache

class TransportationOptimizer:
    """
    Service to optimize commute times across multiple transportation options
    """
    
    def __init__(self):
        self.commute_cache = CommuteCache('cached_commute.json')
    
    def parse_transportation_options(self, transportation_string: str) -> List[str]:
        """
        Parse transportation string to extract individual transportation methods.
        
        Args:
            transportation_string: String like "Car (I drive), Public transportation (e.g. bus, BART)"
            
        Returns:
            List of transportation methods
        """
        if not transportation_string or transportation_string.strip() == '':
            return ['driving']  # Default fallback
        
        # Common transportation patterns
        transport_patterns = [
            r'Car\s*\([^)]*\)',  # Car with details
            r'Public transportation\s*\([^)]*\)',  # Public transport with details
            r'Ridesharing or rental\s*\([^)]*\)',  # Ridesharing with details
            r'driving',  # Simple driving
            r'walking',  # Walking
            r'bicycling',  # Bicycling
            r'Skateboard',  # Skateboard
        ]
        
        # Split by common separators
        separators = [',', '&', ';']
        
        # Try to split by separators first
        for sep in separators:
            if sep in transportation_string:
                parts = [part.strip() for part in transportation_string.split(sep)]
                # Clean up each part
                clean_parts = []
                for part in parts:
                    # Extract the main transportation method
                    part = part.strip()
                    
                    # Handle Car variations
                    if 'Car' in part:
                        clean_parts.append('driving')
                    elif 'Public transportation' in part or 'BART' in part or 'bus' in part.lower():
                        clean_parts.append('transit')
                    elif 'Ridesharing' in part or 'Uber' in part or 'Lyft' in part:
                        clean_parts.append('rideshare')
                    elif 'walk' in part.lower():
                        clean_parts.append('walking')
                    elif 'bicycle' in part.lower() or 'bike' in part.lower():
                        clean_parts.append('bicycling')
                    elif 'Skateboard' in part:
                        clean_parts.append('skateboard')
                    elif 'driving' in part.lower():
                        clean_parts.append('driving')
                    else:
                        # Fallback: try to extract from the first word
                        words = part.split()
                        if words:
                            first_word = words[0].lower()
                            if first_word in ['car', 'public', 'ridesharing', 'walk', 'bicycle', 'skateboard']:
                                clean_parts.append(first_word)
                            else:
                                clean_parts.append('driving')  # Default fallback
                
                return list(set(clean_parts))  # Remove duplicates
        
        # If no separators found, try to extract single method
        transport_string = transportation_string.strip()
        
        if 'Car' in transport_string:
            return ['driving']
        elif 'Public transportation' in transport_string or 'BART' in transport_string or 'bus' in transport_string.lower():
            return ['transit']
        elif 'Ridesharing' in transport_string or 'Uber' in transport_string or 'Lyft' in transport_string:
            return ['rideshare']
        elif 'walk' in transport_string.lower():
            return ['walking']
        elif 'bicycle' in transport_string.lower() or 'bike' in transport_string.lower():
            return ['bicycling']
        elif 'Skateboard' in transport_string:
            return ['skateboard']
        elif 'driving' in transport_string.lower():
            return ['driving']
        else:
            return ['driving']  # Default fallback
    
    def get_optimal_commute(self, origin_address: str, destination_address: str, 
                          transportation_string: str) -> Optional[int]:
        """
        Get the optimal commute time across all transportation options.
        
        Args:
            origin_address: Starting address
            destination_address: Destination address
            transportation_string: Transportation options string
            
        Returns:
            Minimum commute time in minutes, or None if calculation fails
        """
        transport_options = self.parse_transportation_options(transportation_string)
        
        if not transport_options:
            return None
        
        commute_times = []
        
        for transport_method in transport_options:
            try:
                # Get commute for this transportation method
                commute_info = self.commute_cache.get_commute(
                    transport_method,
                    origin_address,
                    destination_address
                )
                
                if commute_info:
                    # Convert seconds to minutes (Google Maps API returns seconds)
                    commute_minutes = round(commute_info.value / 60)  # Convert seconds to minutes with proper rounding
                    # Only add to list if it's a reasonable commute time
                    if commute_minutes > 0 and commute_minutes < 180:  # Filter out 0 and unrealistic values (increased to 3 hours for Bay Area traffic)
                        commute_times.append(commute_minutes)
                    
            except Exception as e:
                # Skip this transportation method if calculation fails
                continue
        
        if not commute_times:
            return None
        
        # Return the minimum commute time across all options
        return min(commute_times)
    
    def get_transportation_comparison(self, origin_address: str, destination_address: str, 
                                     transportation_string: str) -> dict:
        """
        Get detailed comparison of commute times across all transportation options.
        
        Args:
            origin_address: Starting address
            destination_address: Destination address
            transportation_string: Transportation options string
            
        Returns:
            Dictionary with commute times for each transportation method
        """
        transport_options = self.parse_transportation_options(transportation_string)
        
        if not transport_options:
            return {}
        
        commute_comparison = {}
        
        for transport_method in transport_options:
            try:
                # Get commute for this transportation method
                commute_info = self.commute_cache.get_commute(
                    transport_method,
                    origin_address,
                    destination_address
                )
                
                if commute_info:
                    # Convert seconds to minutes (Google Maps API returns seconds)
                    commute_minutes = round(commute_info.value / 60)  # Convert seconds to minutes with proper rounding
                    commute_comparison[transport_method] = commute_minutes
                    
            except Exception as e:
                # Skip this transportation method if calculation fails
                commute_comparison[transport_method] = None
        
        return commute_comparison

# Convenience function for backward compatibility
def get_optimal_commute_time(origin_address: str, destination_address: str, 
                              transportation_string: str) -> Optional[int]:
    """
    Convenience function to get optimal commute time.
    
    Args:
        origin_address: Starting address
        destination_address: Destination address
        transportation_string: Transportation options string
        
    Returns:
        Minimum commute time in minutes
    """
    optimizer = TransportationOptimizer()
    return optimizer.get_optimal_commute(origin_address, destination_address, transportation_string)
