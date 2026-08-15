"""
CSV Data Loader for SproutsProject
Handles loading intern and restaurant data from CSV files
"""

import csv
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Role, Intern, Restaurant, InternAvailability
from app.services.slot import Slot
from app.services.commute_service import CommuteCache

class CSVDataLoader:
    """Loads data from original CSV files and creates database records."""
    
    def __init__(self):
        self.commute_cache = CommuteCache()
        
        # Default paths to latest CSV files (use project directory)
        self.default_intern_csv = "intern_avail_fall.csv"
        self.default_restaurant_csv = "chef_avail_fall.csv"
    
    def load_data_from_csv(self, clear_existing: bool = False, intern_csv_path: str = None, restaurant_csv_path: str = None) -> Dict:
        """Load interns and restaurants from CSV files and create database records."""
        
        # Use provided paths or defaults
        intern_path = intern_csv_path or self.default_intern_csv
        restaurant_path = restaurant_csv_path or self.default_restaurant_csv
        
        if clear_existing:
            self.clear_existing_data()
        
        # Load interns and restaurants
        interns = self.load_interns_from_csv_file(intern_path)
        restaurants = self.load_restaurants_from_csv(restaurant_path)
        
        return {
            'interns_loaded': len(interns),
            'restaurants_loaded': len(restaurants),
            'intern_csv_path': intern_path,
            'restaurant_csv_path': restaurant_path
        }
    
    def load_interns_from_csv_file(self, csv_path: str) -> List[Intern]:
        """Load interns from specified CSV file."""
        interns = []
        
        if not os.path.exists(csv_path):
            current_app.logger.warning(f"Intern CSV file not found: {csv_path}")
            return interns
        
        try:
            with open(csv_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Create user account
                    email = row.get('Email Address', f"intern_{len(interns)}@example.com")
                    
                    # Check if user already exists
                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user:
                        continue
                    
                    user = User(
                        email=email,
                        first_name=row.get('First Name', 'Unknown'),
                        last_name=row.get('Last Name', 'User'),
                        user_type='intern',
                        active=True
                    )
                    user.password = 'intern123'  # Default password
                    
                    # Add intern role
                    intern_role = Role.query.filter_by(name='intern').first()
                    if intern_role:
                        user.roles = [intern_role]
                    
                    db.session.add(user)
                    db.session.flush()
                    
                    # Create intern profile
                    intern = Intern(
                        user_id=user.id,
                        address=row.get('Street Address', ''),
                        city=row.get('City', ''),
                        postal_code=row.get('Zip Code', ''),
                        country='USA',
                        transportation_method=row.get('What transportation will you use?', 'driving'),
                        max_commute_minutes=self._parse_commute_max(row.get('How long are you willing to commute to your internship?', '50')),
                        school_end_time=row.get("If you are currently attending school, what time do you finish each day? If your end time varies by the day, please specify accordingly. \nIf you're not currently enrolled in school, write 'n/a'.", 'n/a'),
                        is_seeking_internship=True,
                        # New CSV fields
                        intern_description=row.get('interndescription', ''),
                        behavior_notes=row.get('Behavior Notes', ''),
                        age=self._parse_age(row.get('Age', ''))
                    )
                    db.session.add(intern)
                    db.session.flush()
                    
                    # Create availability
                    availability = self._parse_intern_availability(row, intern.id)
                    if availability:
                        db.session.add(availability)
                    
                    interns.append(intern)
                    
                db.session.commit()
                current_app.logger.info(f"Loaded {len(interns)} interns from CSV")
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error loading interns from CSV: {str(e)}")
            
        return interns
    
    def load_restaurants_from_csv(self, csv_path: str = None) -> List[Restaurant]:
        """Load restaurants/chefs from CSV file and create database records."""
        restaurants = []
        
        restaurant_path = csv_path or self.default_restaurant_csv
        
        if not os.path.exists(restaurant_path):
            current_app.logger.warning(f"Restaurant CSV file not found: {restaurant_path}")
            return restaurants
        
        try:
            with open(restaurant_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Create restaurant owner user
                    email = row.get("Primary Mentor's Email Address", f"chef_{len(restaurants)}@example.com")
                    if not email or email.strip() == '':
                        email = f"chef_{len(restaurants)}@example.com"
                    
                    # Check if user already exists
                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user:
                        continue
                    
                    full_name = row.get("Primary Mentor's Full Name (First and Last)", "Unknown Chef")
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0] if name_parts else "Unknown"
                    last_name = name_parts[1] if len(name_parts) > 1 else "Chef"
                    
                    user = User(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        phone=row.get("Primary Mentor's Cell Phone Number", ''),
                        user_type='restaurant_owner',
                        active=True
                    )
                    user.password = 'chef123'  # Default password
                    
                    # Add restaurant owner role
                    owner_role = Role.query.filter_by(name='restaurant_owner').first()
                    if owner_role:
                        user.roles = [owner_role]
                    
                    db.session.add(user)
                    db.session.flush()
                    
                    restaurant_name = row.get('Restaurant Name', 'Unknown Restaurant')
                    restaurant_address = row.get('Restaurant Address', '')
                    
                    restaurant = Restaurant(
                        name=restaurant_name,
                        address=restaurant_address,
                        city='Oakland',  # Default city
                        country='USA',
                        email=email,  # Now guaranteed to have a value
                        phone=row.get("Primary Mentor's Cell Phone Number", ""),
                        is_active=True,
                        is_verified=True,
                        requires_over_18=row.get("Do interns need to be over 18 to work in your kitchen?", "No").lower() == 'yes',
                        # New CSV fields
                        restaurant_location=row.get('Restaurant Location', ''),
                        mentor_name=row.get("Primary Mentor's Full Name (First and Last)", ''),
                        mentor_email=row.get("Primary Mentor's Email Address", ''),
                        mentor_phone=row.get("Primary Mentor's Cell Phone Number", ''),
                        age_requirement=row.get("Do interns need to be over 18 to work in your kitchen?", '')
                    )
                    db.session.add(restaurant)
                    db.session.flush()
                    
                    # Create restaurant owner profile
                    from app.models.restaurant import RestaurantOwner
                    existing_owner = RestaurantOwner.query.filter_by(user_id=user.id).first()
                    if not existing_owner:
                        owner = RestaurantOwner(
                            user_id=user.id,
                            restaurant_id=restaurant.id,
                            position='Chef Mentor'
                        )
                        db.session.add(owner)
                    
                    restaurants.append(restaurant)
                    
                db.session.commit()
                current_app.logger.info(f"Loaded {len(restaurants)} restaurants from CSV")
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error loading restaurants from CSV: {str(e)}")
            
        return restaurants
    
    def _parse_commute_max(self, commute_str: str) -> int:
        """Parse commute maximum from string format."""
        try:
            # Extract number from strings like "30 minutes", "1 hour", etc.
            if 'hour' in commute_str.lower():
                return 60  # 1 hour = 60 minutes
            elif 'minute' in commute_str.lower():
                import re
                numbers = re.findall(r'\d+', commute_str)
                return int(numbers[0]) if numbers else 50
            else:
                return 50  # Default
        except:
            return 50
    
    def _parse_age(self, age_str: str) -> int:
        """Parse age from string."""
        try:
            if age_str and age_str.strip():
                return int(age_str.strip())
            return None
        except:
            return None
    
    def _parse_intern_availability(self, row: Dict, intern_id: int) -> InternAvailability:
        """Parse intern availability from CSV row."""
        try:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            availability_data = {'intern_id': intern_id}
            
            for day in days:
                day_slots = row.get(day, '')
                am, pm = self._parse_day_slots(day_slots)
                availability_data[f'{day.lower()}_am'] = am
                availability_data[f'{day.lower()}_pm'] = pm
            
            return InternAvailability(**availability_data)
            
        except Exception as e:
            current_app.logger.error(f"Error parsing availability: {str(e)}")
            return None
    
    def _parse_restaurant_availability(self, row: Dict, restaurant_id: int) -> Dict[str, List[Slot]]:
        """Parse restaurant availability from CSV row."""
        availability = {}
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            day_slots = row.get(day, '').strip()
            if day_slots and day_slots != 'Unavailable' and day_slots != '':
                # Parse individual time slots and merge consecutive ones
                individual_slots = day_slots.split(',')
                merged_slots = self._merge_time_slots(individual_slots)
                availability[day] = merged_slots
            else:
                availability[day] = []
        
        return availability
    
    def _merge_time_slots(self, individual_slots: List[str]) -> List[Slot]:
        """Merge consecutive time slots into continuous blocks."""
        if not individual_slots:
            return []
        
        slots = []
        for slot_str in individual_slots:
            slot_str = slot_str.strip()
            if slot_str:
                try:
                    slot = Slot(slot_str)
                    slots.append(slot)
                except:
                    continue
        
        # Merge consecutive slots
        if len(slots) > 1:
            slots = self._merge_consecutive_slots(slots)
        
        return slots
    
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
                # Merge them
                current_end = max(current.end, next_slot.end)
                current = Slot(f"{current.start}-{current_end}")
            else:
                # No overlap, add current and start new
                merged.append(current)
                current = next_slot
        
        merged.append(current)
        return merged
    
    def _parse_day_slots(self, day_slots_str: str) -> tuple:
        """Parse day slots string into AM/PM boolean values."""
        if not day_slots_str or day_slots_str.strip() == '' or day_slots_str.strip() == 'Unavailable':
            return False, False
        
        try:
            # Parse AM/PM time slots like "11AM-12PM, 12PM-1PM, 1PM-2PM"
            import re
            
            has_am = False
            has_pm = False
            
            # Handle "All Day (9AM-9PM)" format
            if 'ALL DAY' in day_slots_str.upper():
                match = re.search(r'(\d+)AM-(\d+)PM', day_slots_str.upper())
                if match:
                    start_hour = int(match.group(1))
                    end_hour = int(match.group(2)) + 12
                    if start_hour < 12:
                        has_am = True
                    if end_hour > 12:
                        has_pm = True
            else:
                # Parse individual time slots
                individual_slots = day_slots_str.split(',')
                for slot in individual_slots:
                    slot = slot.strip()
                    # Match patterns like "11AM-12PM", "12PM-1PM", "5PM-6PM"
                    match = re.match(r'(\d+)(AM|PM)-(\d+)(AM|PM)', slot)
                    if match:
                        start_hour = int(match.group(1))
                        start_period = match.group(2)
                        end_hour = int(match.group(3))
                        end_period = match.group(4)
                        
                        # Convert to 24-hour format for checking
                        if start_period == 'AM':
                            if start_hour == 12:
                                start_hour = 0
                        else:
                            start_hour = start_hour
                        if start_period == 'PM':
                            if start_hour != 12:
                                start_hour += 12
                        
                        if end_period == 'AM':
                            if end_hour == 12:
                                end_hour = 0
                        else:
                            end_hour = end_hour
                        if end_period == 'PM':
                            if end_hour != 12:
                                end_hour += 12
                        
                        # Check AM/PM coverage
                        if start_hour < 12 and end_hour > 9:
                            has_am = True
                        if end_hour > 12:
                            has_pm = True
            
            return has_am, has_pm
            
        except Exception as e:
            current_app.logger.error(f"Error parsing day slots '{day_slots_str}': {str(e)}")
            return False, False
    
    def clear_existing_data(self):
        """Clear existing intern and restaurant data."""
        try:
            # Delete in proper order to avoid foreign key constraints
            InternAvailability.query.delete()
            Intern.query.delete()
            Restaurant.query.delete()
            User.query.filter(User.user_type.in_(['intern', 'restaurant_owner'])).delete()
            db.session.commit()
            current_app.logger.info("Cleared existing data")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error clearing data: {str(e)}")
