from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, BooleanField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, ValidationError
from datetime import datetime, date

class RestaurantProfileForm(FlaskForm):
    # Basic Information
    name = StringField('Restaurant Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)],
                               render_kw={"rows": 4, "placeholder": "Describe your restaurant..."})
    
    cuisine_type = SelectField('Cuisine Type', choices=[
        ('american', 'American'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('indian', 'Indian'),
        ('french', 'French'),
        ('thai', 'Thai'),
        ('mediterranean', 'Mediterranean'),
        ('fusion', 'Fusion'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    restaurant_type = SelectField('Restaurant Type', choices=[
        ('fine_dining', 'Fine Dining'),
        ('casual_dining', 'Casual Dining'),
        ('fast_casual', 'Fast Casual'),
        ('fast_food', 'Fast Food'),
        ('cafe', 'Cafe'),
        ('bakery', 'Bakery'),
        ('food_truck', 'Food Truck'),
        ('catering', 'Catering'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    # Contact Information
    email = StringField('Restaurant Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=500)])
    
    # Location
    address = StringField('Address', validators=[DataRequired(), Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    
    # Business Details
    established_year = IntegerField('Established Year', validators=[
        Optional(), 
        NumberRange(min=1800, max=datetime.now().year)
    ])
    number_of_employees = IntegerField('Number of Employees', validators=[
        Optional(), 
        NumberRange(min=1, max=10000)
    ])
    seating_capacity = IntegerField('Seating Capacity', validators=[
        Optional(), 
        NumberRange(min=1, max=1000)
    ])
    
    # Social Media
    instagram_handle = StringField('Instagram Handle', validators=[Optional(), Length(max=100)])
    facebook_page = StringField('Facebook Page URL', validators=[Optional(), Length(max=500)])
    twitter_handle = StringField('Twitter Handle', validators=[Optional(), Length(max=100)])
    
    # Age Requirements (from original chef.py)
    requires_over_18 = BooleanField('Require interns to be over 18 years old')
    
    submit = SubmitField('Update Profile')

class InternshipForm(FlaskForm):
    # Basic Information
    title = StringField('Internship Title', validators=[DataRequired(), Length(max=255)],
                       render_kw={"placeholder": "e.g., Kitchen Assistant Intern, Front of House Intern"})
    
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=50, max=2000)],
                               render_kw={"rows": 6, "placeholder": "Describe the internship role, responsibilities, and what the intern will learn..."})
    
    department = SelectField('Department', choices=[
        ('kitchen', 'Kitchen'),
        ('front_of_house', 'Front of House'),
        ('management', 'Management'),
        ('pastry', 'Pastry'),
        ('bar', 'Bar/Beverage'),
        ('catering', 'Catering'),
        ('administration', 'Administration'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    # Requirements
    required_skills = StringField('Required Skills', validators=[Optional(), Length(max=500)],
                                 render_kw={"placeholder": "e.g., Basic knife skills, Customer service experience"})
    
    preferred_skills = StringField('Preferred Skills', validators=[Optional(), Length(max=500)],
                                  render_kw={"placeholder": "e.g., Food safety certification, Bilingual"})
    
    education_requirements = StringField('Education Requirements', validators=[Optional(), Length(max=255)],
                                        render_kw={"placeholder": "e.g., High school diploma, Culinary school enrollment"})
    
    experience_required = StringField('Experience Required', validators=[Optional(), Length(max=255)],
                                     render_kw={"placeholder": "e.g., No experience required, 6 months restaurant experience"})
    
    # Duration and Schedule
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    duration_weeks = IntegerField('Duration (weeks)', validators=[
        Optional(), 
        NumberRange(min=1, max=52)
    ])
    hours_per_week = IntegerField('Hours per Week', validators=[
        DataRequired(), 
        NumberRange(min=1, max=60)
    ])
    
    is_flexible_schedule = BooleanField('Flexible Schedule Available')
    requires_weekends = BooleanField('Weekend Work Required')
    requires_evenings = BooleanField('Evening Work Required')
    
    # Compensation
    is_paid = BooleanField('This is a Paid Internship')
    hourly_rate = FloatField('Hourly Rate ($)', validators=[
        Optional(), 
        NumberRange(min=0, max=100)
    ])
    stipend_amount = FloatField('Monthly Stipend ($)', validators=[
        Optional(), 
        NumberRange(min=0, max=5000)
    ])
    other_benefits = StringField('Other Benefits', validators=[Optional(), Length(max=500)],
                                render_kw={"placeholder": "e.g., Free meals, Transportation allowance, Training opportunities"})
    
    # Application Details
    application_deadline = DateField('Application Deadline', validators=[Optional()])
    positions_available = IntegerField('Number of Positions', validators=[
        DataRequired(), 
        NumberRange(min=1, max=50)
    ], default=1)
    
    # Contact Information
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=255)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Application Instructions
    application_instructions = TextAreaField('Application Instructions', validators=[Optional(), Length(max=1000)],
                                           render_kw={"rows": 4, "placeholder": "Any specific instructions for applicants..."})
    
    required_documents = StringField('Required Documents', validators=[Optional(), Length(max=500)],
                                    render_kw={"placeholder": "e.g., Resume, Cover Letter, Portfolio"})
    
    # Status
    is_featured = BooleanField('Feature this Internship')
    
    submit = SubmitField('Post Internship')
    
    def validate_end_date(self, end_date):
        if end_date.data and self.start_date.data:
            if end_date.data <= self.start_date.data:
                raise ValidationError('End date must be after start date.')
    
    def validate_application_deadline(self, application_deadline):
        if application_deadline.data:
            if application_deadline.data <= date.today():
                raise ValidationError('Application deadline must be in the future.')
            if self.start_date.data and application_deadline.data >= self.start_date.data:
                raise ValidationError('Application deadline must be before start date.')

class ApplicationReviewForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('under_review', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    
    feedback = TextAreaField('Feedback/Notes', validators=[Optional(), Length(max=1000)],
                            render_kw={"rows": 4, "placeholder": "Provide feedback to the applicant..."})
    
    interview_date = DateField('Interview Date', validators=[Optional()])
    interview_location = StringField('Interview Location', validators=[Optional(), Length(max=255)])
    interview_type = SelectField('Interview Type', choices=[
        ('', 'Select Type'),
        ('in_person', 'In Person'),
        ('phone', 'Phone'),
        ('video', 'Video Call')
    ], validators=[Optional()])
    
    submit = SubmitField('Update Application')
