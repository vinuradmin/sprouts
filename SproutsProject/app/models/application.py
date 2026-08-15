from datetime import datetime
from app import db
from .base_model import BaseModel

class Application(BaseModel):
    """Application model for intern applications to internships."""
    __tablename__ = 'application'
    
    # Foreign keys
    intern_id = db.Column(db.Integer, db.ForeignKey('intern.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    
    # Application Status
    status = db.Column(db.String(50), default='submitted')  # submitted, under_review, interview_scheduled, accepted, rejected, withdrawn
    
    # Application Content
    cover_letter = db.Column(db.Text)
    additional_notes = db.Column(db.Text)
    
    # Documents
    resume_url = db.Column(db.String(500))
    portfolio_url = db.Column(db.String(500))
    other_documents = db.Column(db.String(1000))  # JSON string of document URLs
    
    # Timeline
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    interview_scheduled_at = db.Column(db.DateTime)
    decision_made_at = db.Column(db.DateTime)
    
    # Interview Details
    interview_date = db.Column(db.DateTime)
    interview_location = db.Column(db.String(255))
    interview_type = db.Column(db.String(50))  # in_person, phone, video
    interview_notes = db.Column(db.Text)
    
    # Decision Details
    rejection_reason = db.Column(db.String(500))
    feedback = db.Column(db.Text)
    
    # Communication
    messages = db.relationship('ApplicationMessage', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('intern_id', 'internship_id', name='unique_application'),)
    
    @property
    def is_pending(self):
        """Check if application is still pending (not decided)."""
        return self.status in ['submitted', 'under_review', 'interview_scheduled']
    
    @property
    def is_accepted(self):
        """Check if application was accepted."""
        return self.status == 'accepted'
    
    @property
    def is_rejected(self):
        """Check if application was rejected."""
        return self.status == 'rejected'
    
    def update_status(self, new_status, notes=None):
        """Update application status with timestamp."""
        self.status = new_status
        
        if new_status == 'under_review':
            self.reviewed_at = datetime.utcnow()
        elif new_status == 'interview_scheduled':
            self.interview_scheduled_at = datetime.utcnow()
        elif new_status in ['accepted', 'rejected']:
            self.decision_made_at = datetime.utcnow()
            if notes:
                self.feedback = notes
        
        self.save()
    
    def __repr__(self):
        return f'<Application {self.intern.user.full_name} -> {self.internship.title}>'


class ApplicationMessage(BaseModel):
    """Messages between intern and restaurant regarding an application."""
    __tablename__ = 'application_message'
    
    # Foreign key
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    
    # Message details
    sender_type = db.Column(db.String(20), nullable=False)  # 'intern' or 'restaurant'
    sender_id = db.Column(db.Integer, nullable=False)  # ID of the user who sent the message
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    def mark_as_read(self):
        """Mark message as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()
    
    def __repr__(self):
        return f'<ApplicationMessage from {self.sender_type} at {self.created_at}>'
