from datetime import datetime
from app import db
from .base_model import BaseModel

class Intern(BaseModel):
    """Intern profile model."""
    __tablename__ = 'intern'
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Personal Information
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Transportation and Commute (from original intern.py)
    transportation_method = db.Column(db.String(100))  # Car, Public Transit, etc.
    max_commute_minutes = db.Column(db.Integer, default=50)  # Maximum acceptable commute
    school_end_time = db.Column(db.String(100))  # When school ends each day
    
    # Education
    education_level = db.Column(db.String(100))  # e.g., High School, Bachelor's, Master's
    institution = db.Column(db.String(255))      # School/University name
    field_of_study = db.Column(db.String(255))   # Major/Field of study
    graduation_year = db.Column(db.Integer)      # Expected or actual graduation year
    
    # Skills and Interests
    skills = db.relationship('InternSkill', backref='intern', lazy='dynamic', cascade='all, delete-orphan')
    interests = db.Column(db.String(500))  # Comma-separated list of interests
    
    # CSV Data Fields
    intern_description = db.Column(db.Text)  # From 'interndescription' column
    behavior_notes = db.Column(db.Text)     # From 'Behavior Notes' column
    age = db.Column(db.Integer)              # From 'Age' column
    
    # Work Experience
    work_experience = db.relationship('WorkExperience', backref='intern', lazy='dynamic', cascade='all, delete-orphan')
    
    # Availability
    availability = db.relationship('InternAvailability', backref='intern', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    # Preferences
    preferred_locations = db.Column(db.String(500))  # Comma-separated list of preferred locations
    preferred_restaurant_types = db.Column(db.String(500))  # Comma-separated list of preferred restaurant types
    
    # Documents
    resume_url = db.Column(db.String(500))
    cover_letter_url = db.Column(db.String(500))
    
    # Status
    is_seeking_internship = db.Column(db.Boolean, default=True)
    
    # Relationships
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', foreign_keys='Application.intern_id')
    
    def get_full_address(self):
        """Get complete address string for commute calculations."""
        if not self.address or not self.city:
            return ""
        
        parts = [self.address, self.city]
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        
        return ', '.join(parts)
    
    def is_over_18(self):
        """Check if intern is over 18 years old."""
        if not self.date_of_birth:
            return False
        
        from datetime import date
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or \
           (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        
        return age >= 18

    def __repr__(self):
        return f'<Intern {self.user.full_name}>'


class InternSkill(BaseModel):
    """Skills that an intern possesses."""
    __tablename__ = 'intern_skill'
    
    intern_id = db.Column(db.Integer, db.ForeignKey('intern.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(50))  # e.g., Beginner, Intermediate, Advanced, Expert
    
    def __repr__(self):
        return f'<InternSkill {self.skill_name} ({self.proficiency})>'


class WorkExperience(BaseModel):
    """Work experience for an intern."""
    __tablename__ = 'work_experience'
    
    intern_id = db.Column(db.Integer, db.ForeignKey('intern.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Null means current position
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<WorkExperience {self.position} at {self.company_name}>'


class InternAvailability(BaseModel):
    """Availability schedule for an intern."""
    __tablename__ = 'intern_availability'
    
    intern_id = db.Column(db.Integer, db.ForeignKey('intern.id'), unique=True, nullable=False)
    
    # Weekly availability
    monday_am = db.Column(db.Boolean, default=False)
    monday_pm = db.Column(db.Boolean, default=False)
    tuesday_am = db.Column(db.Boolean, default=False)
    tuesday_pm = db.Column(db.Boolean, default=False)
    wednesday_am = db.Column(db.Boolean, default=False)
    wednesday_pm = db.Column(db.Boolean, default=False)
    thursday_am = db.Column(db.Boolean, default=False)
    thursday_pm = db.Column(db.Boolean, default=False)
    friday_am = db.Column(db.Boolean, default=False)
    friday_pm = db.Column(db.Boolean, default=False)
    saturday_am = db.Column(db.Boolean, default=False)
    saturday_pm = db.Column(db.Boolean, default=False)
    sunday_am = db.Column(db.Boolean, default=False)
    sunday_pm = db.Column(db.Boolean, default=False)
    
    # Other availability details
    start_date = db.Column(db.Date)  # When they can start
    end_date = db.Column(db.Date)    # When they need to finish by
    hours_per_week = db.Column(db.Integer)  # Desired hours per week
    
    def __repr__(self):
        return f'<InternAvailability for Intern {self.intern_id}>'
