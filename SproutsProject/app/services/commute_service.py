"""
Commute calculation service using Google Maps API.
Adapted from the original commute.py to work with the Flask application.
"""

import googlemaps
import json
import os
from flask import current_app

class CommuteService:
    """Service for calculating commute times between locations."""
    
    def __init__(self):
        self.gmaps = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Maps client with API key."""
        api_key = 'AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg'
        if api_key:
            self.gmaps = googlemaps.Client(key=api_key)
    
    def calculate_commute_time(self, transportation_type, origin, destination):
        """
        Calculate commute time between two locations.
        
        Args:
            transportation_type (str): Type of transportation (Car, Public Transit, etc.)
            origin (str): Starting address
            destination (str): Destination address
            
        Returns:
            Commute: Commute object with time and distance information
        """
        if not origin or not destination:
            return Commute('Missing Address', 3000)  # 50 minutes fallback
        
        # If no API key, we cannot calculate commute
        if not self.gmaps:
            current_app.logger.error("No Google Maps API key - cannot calculate commute")
            raise Exception("Google Maps API key not available")
        
        try:
            # Determine Google Maps mode based on transportation type
            google_mode = 'driving' if transportation_type.lower().startswith('car') else 'transit'
            
            # Call Google Maps API
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=google_mode,
                units='imperial'
            )
            
            if result['status'] == 'OK' and result['rows']:
                element = result['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    duration = element['duration']
                    distance = element.get('distance', {})
                    
                    # Return the actual commute time even if it's very long
                    return Commute(
                        text=duration['text'],
                        value=duration['value'],
                        distance_text=distance.get('text', ''),
                        distance_value=distance.get('value', 0)
                    )
                else:
                    current_app.logger.warning(f"API returned error status: {element['status']}")
                    if element['status'] == 'ZERO_RESULTS':
                        # Default to 24 hours for unreachable destinations
                        return Commute('24 hours (unreachable)', 86400)
                    else:
                        raise Exception(f"Google Maps API error: {element['status']}")
            else:
                current_app.logger.warning(f"API returned error: {result.get('status', 'Unknown')}")
                if result.get('status') == 'ZERO_RESULTS':
                    # Default to 24 hours for unreachable destinations
                    return Commute('24 hours (unreachable)', 86400)
                else:
                    raise Exception(f"Google Maps API error: {result.get('status', 'Unknown')}")
                
        except Exception as e:
            current_app.logger.error(f"Commute calculation error: {str(e)}")
            raise e


class Commute:
    """Represents commute information between two locations."""
    
    def __init__(self, text, value, distance_text='', distance_value=0):
        self.text = text  # Human readable time (e.g., "25 mins")
        self.value = value  # Time in seconds
        self.distance_text = distance_text  # Human readable distance (e.g., "5.2 miles")
        self.distance_value = distance_value  # Distance in meters
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"Commute({self.text}, {self.distance_text})"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'text': self.text,
            'value': self.value,
            'distance_text': self.distance_text,
            'distance_value': self.distance_value
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Commute object from dictionary."""
        return cls(
            text=data.get('text', ''),
            value=data.get('value', 0),
            distance_text=data.get('distance_text', ''),
            distance_value=data.get('distance_value', 0)
        )
    
    @property
    def minutes(self):
        """Get commute time in minutes."""
        return round(self.value / 60)
    
    @property
    def is_reasonable(self):
        """Check if commute time is reasonable (under 50 minutes)."""
        return self.value <= 3000  # 50 minutes in seconds
    
    @property
    def miles(self):
        """Get distance in miles (approximate)."""
        return round(self.distance_value * 0.000621371, 1)


class CommuteCache:
    """Cache for storing commute calculations to reduce API calls - matches original cached_commute.json format."""
    
    def __init__(self, cache_file='cached_commute.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file - matches original implementation."""
        try:
            with open(self.cache_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, create it and initialize an empty dict
            cache = {}
            with open(self.cache_file, 'w') as file:
                json.dump(cache, file)
            return cache
        except json.JSONDecodeError:
            # If the file is empty or contains invalid JSON, initialize an empty dict
            cache = {}
            with open(self.cache_file, 'w') as file:
                json.dump(cache, file)
            return cache
    
    def _save_cache(self):
        """Save cache to file with proper formatting - matches original implementation."""
        try:
            with open(self.cache_file, 'w') as file:
                json.dump(self.cache, file, indent=4)
        except IOError as e:
            current_app.logger.error(f"Error saving commute cache: {str(e)}")
    
    def _get_cache_key(self, origin, destination):
        """Generate cache key for origin-destination pair - matches original format."""
        return f"{origin}|{destination}"
    
    def get_commute(self, transportation_type, origin, destination):
        """Get commute from cache or calculate new one - matches original logic."""
        cache_key = self._get_cache_key(origin, destination)
        
        # Check cache first - matches original logic
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if isinstance(cached_data, dict):
                return Commute.from_dict(cached_data)
            else:
                # Handle case where cached data might be a Commute object
                return cached_data if isinstance(cached_data, Commute) else Commute.from_dict(cached_data)
        
        # Calculate new commute - matches original "new Call to Google API" logic
        current_app.logger.info("New call to Google API for commute calculation")
        commute_service = CommuteService()
        commute = commute_service.calculate_commute_time(transportation_type, origin, destination)
        
        # Store in cache - matches original format
        self.cache[cache_key] = commute.to_dict()
        self._save_cache()
        
        return commute
    
    def has_cached_commute(self, origin, destination):
        """Check if commute is cached - matches original logic."""
        cache_key = self._get_cache_key(origin, destination)
        return cache_key in self.cache
    
    def clear_cache(self):
        """Clear all cached commute data."""
        self.cache = {}
        self._save_cache()
    
    def get_cache_stats(self):
        """Get statistics about the cache."""
        return {
            'total_cached_routes': len(self.cache),
            'cache_file': self.cache_file,
            'cache_exists': os.path.exists(self.cache_file)
        }
