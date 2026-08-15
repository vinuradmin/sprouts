from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime

class InternProfileForm(FlaskForm):
    # User Information
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    
    # Personal Information
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'Prefer not to say'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-binary'),
        ('other', 'Other')
    ], validators=[Optional()])
    
    # Address
    address = StringField('Address', validators=[Optional(), Length(max=255)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    
    # Education
    education_level = SelectField('Education Level', choices=[
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    institution = StringField('School/University', validators=[DataRequired(), Length(max=255)])
    field_of_study = StringField('Field of Study', validators=[Optional(), Length(max=255)])
    graduation_year = IntegerField('Graduation Year', validators=[
        Optional(), 
        NumberRange(min=1950, max=datetime.now().year + 10)
    ])
    
    # Transportation and Commute (from original scripts)
    transportation_method = SelectField('Transportation Method', choices=[
        ('car', 'Car/Driving'),
        ('public_transit', 'Public Transit'),
        ('bicycle', 'Bicycle'),
        ('walking', 'Walking'),
        ('other', 'Other')
    ], validators=[Optional()])
    
    max_commute_minutes = IntegerField('Maximum Commute Time (minutes)', validators=[
        Optional(), 
        NumberRange(min=5, max=120)
    ], default=50)
    
    school_end_time = StringField('School End Time', validators=[Optional(), Length(max=100)],
                                 render_kw={"placeholder": "e.g., 3:00 PM, varies by day, n/a"})
    
    # Interests and Preferences
    interests = TextAreaField('Interests', validators=[Optional(), Length(max=500)],
                             render_kw={"placeholder": "Describe your interests in the culinary field..."})
    
    preferred_locations = StringField('Preferred Locations', validators=[Optional(), Length(max=500)],
                                    render_kw={"placeholder": "e.g., Downtown, Suburbs, Specific neighborhoods..."})
    
    preferred_restaurant_types = StringField('Preferred Restaurant Types', validators=[Optional(), Length(max=500)],
                                           render_kw={"placeholder": "e.g., Fine Dining, Casual, Fast Food..."})
    
    # Availability
    is_seeking_internship = BooleanField('Currently seeking internship opportunities', default=True)
    
    submit = SubmitField('Update Profile')

class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired(), Length(min=50, max=2000)],
                                render_kw={"rows": 8, "placeholder": "Tell us why you're interested in this internship and what you can bring to the role..."})
    
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)],
                                   render_kw={"rows": 4, "placeholder": "Any additional information you'd like to share..."})
    
    submit = SubmitField('Submit Application')

class SkillForm(FlaskForm):
    skill_name = StringField('Skill', validators=[DataRequired(), Length(max=100)])
    proficiency = SelectField('Proficiency Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Add Skill')

class WorkExperienceForm(FlaskForm):
    company_name = StringField('Company/Restaurant Name', validators=[DataRequired(), Length(max=255)])
    position = StringField('Position', validators=[DataRequired(), Length(max=255)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    is_current = BooleanField('This is my current position')
    description = TextAreaField('Job Description', validators=[Optional(), Length(max=1000)],
                               render_kw={"rows": 4, "placeholder": "Describe your responsibilities and achievements..."})
    
    submit = SubmitField('Add Experience')

class AvailabilityForm(FlaskForm):
    # Weekly availability
    monday_am = BooleanField('Monday AM')
    monday_pm = BooleanField('Monday PM')
    tuesday_am = BooleanField('Tuesday AM')
    tuesday_pm = BooleanField('Tuesday PM')
    wednesday_am = BooleanField('Wednesday AM')
    wednesday_pm = BooleanField('Wednesday PM')
    thursday_am = BooleanField('Thursday AM')
    thursday_pm = BooleanField('Thursday PM')
    friday_am = BooleanField('Friday AM')
    friday_pm = BooleanField('Friday PM')
    saturday_am = BooleanField('Saturday AM')
    saturday_pm = BooleanField('Saturday PM')
    sunday_am = BooleanField('Sunday AM')
    sunday_pm = BooleanField('Sunday PM')
    
    # Other details
    start_date = DateField('Available Start Date', validators=[Optional()])
    end_date = DateField('Available End Date', validators=[Optional()])
    hours_per_week = IntegerField('Preferred Hours per Week', validators=[
        Optional(), 
        NumberRange(min=1, max=60)
    ])
    
    submit = SubmitField('Update Availability')
