from datetime import datetime
from app import db
from .base_model import BaseModel

class Internship(BaseModel):
    """Internship opportunity model."""
    __tablename__ = 'internship'
    
    # Foreign key to Restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    
    # Basic Information
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100))  # e.g., Kitchen, Front of House, Management
    
    # Requirements
    required_skills = db.Column(db.String(500))  # Comma-separated list
    preferred_skills = db.Column(db.String(500))  # Comma-separated list
    education_requirements = db.Column(db.String(255))
    experience_required = db.Column(db.String(255))
    
    # Duration and Schedule
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    duration_weeks = db.Column(db.Integer)
    hours_per_week = db.Column(db.Integer)
    is_flexible_schedule = db.Column(db.Boolean, default=False)
    
    # Schedule requirements
    requires_weekends = db.Column(db.Boolean, default=False)
    requires_evenings = db.Column(db.Boolean, default=False)
    
    # Compensation
    is_paid = db.Column(db.Boolean, default=False)
    hourly_rate = db.Column(db.Float)
    stipend_amount = db.Column(db.Float)
    other_benefits = db.Column(db.String(500))  # e.g., meals, transportation
    
    # Application Details
    application_deadline = db.Column(db.Date)
    positions_available = db.Column(db.Integer, default=1)
    positions_filled = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Contact Information
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    contact_person = db.Column(db.String(255))
    
    # Application Instructions
    application_instructions = db.Column(db.Text)
    required_documents = db.Column(db.String(500))  # e.g., resume, cover letter, portfolio
    
    # Relationships
    applications = db.relationship('Application', backref='internship', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_expired(self):
        """Check if the application deadline has passed."""
        if self.application_deadline:
            return datetime.utcnow().date() > self.application_deadline
        return False
    
    @property
    def is_full(self):
        """Check if all positions are filled."""
        return self.positions_filled >= self.positions_available
    
    @property
    def available_positions(self):
        """Get number of available positions."""
        return max(0, self.positions_available - self.positions_filled)
    
    def __repr__(self):
        return f'<Internship {self.title} at {self.restaurant.name}>'
