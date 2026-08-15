from app import db
from .base_model import BaseModel

class Restaurant(BaseModel):
    """Restaurant model."""
    __tablename__ = 'restaurant'
    
    # Basic Information
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cuisine_type = db.Column(db.String(100))  # e.g., Italian, Mexican, Asian, etc.
    restaurant_type = db.Column(db.String(100))  # e.g., Fine Dining, Casual, Fast Food, etc.
    
    # CSV Data Fields
    restaurant_location = db.Column(db.String(255))  # From 'Restaurant Location' column
    mentor_name = db.Column(db.String(255))         # From 'Primary Mentor's Full Name' column
    mentor_email = db.Column(db.String(255))        # From 'Primary Mentor's Email Address' column
    mentor_phone = db.Column(db.String(50))          # From 'Primary Mentor's Cell Phone Number' column
    age_requirement = db.Column(db.String(20))       # From 'Do interns need to be over 18' column
    
    # Contact Information
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    website = db.Column(db.String(500))
    
    # Location
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Business Details
    established_year = db.Column(db.Integer)
    number_of_employees = db.Column(db.Integer)
    seating_capacity = db.Column(db.Integer)
    
    # Social Media
    instagram_handle = db.Column(db.String(100))
    facebook_page = db.Column(db.String(500))
    twitter_handle = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Age Requirements (from original chef.py)
    requires_over_18 = db.Column(db.Boolean, default=False)
    
    # Relationships
    owners = db.relationship('RestaurantOwner', backref='restaurant', lazy='dynamic')
    internships = db.relationship('Internship', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_full_address(self):
        """Get complete address string for commute calculations."""
        if not self.address or not self.city:
            return ""
        
        parts = [self.address, self.city]
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        
        return ', '.join(parts)

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class RestaurantOwner(BaseModel):
    """Restaurant owner/manager profile."""
    __tablename__ = 'restaurant_owner'
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    
    # Role in restaurant
    position = db.Column(db.String(100), nullable=False)  # e.g., Owner, Manager, HR Manager
    is_primary_contact = db.Column(db.Boolean, default=False)
    
    # Additional contact info
    direct_phone = db.Column(db.String(20))
    office_extension = db.Column(db.String(10))
    
    # Permissions
    can_post_internships = db.Column(db.Boolean, default=True)
    can_review_applications = db.Column(db.Boolean, default=True)
    can_manage_restaurant = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<RestaurantOwner {self.user.full_name} at {self.restaurant.name}>'
