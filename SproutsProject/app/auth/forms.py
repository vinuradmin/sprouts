from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class InternRegistrationForm(RegistrationForm):
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
    graduation_year = IntegerField('Graduation Year', validators=[Optional()])

class RestaurantOwnerRegistrationForm(RegistrationForm):
    # Restaurant Information
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired(), Length(max=255)])
    restaurant_description = TextAreaField('Restaurant Description', validators=[Optional()])
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
    
    restaurant_email = StringField('Restaurant Email', validators=[DataRequired(), Email()])
    restaurant_phone = StringField('Restaurant Phone', validators=[DataRequired(), Length(max=20)])
    
    # Location
    address = StringField('Address', validators=[DataRequired(), Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    
    # Owner Position
    position = StringField('Your Position', validators=[DataRequired(), Length(max=100)],
                          render_kw={"placeholder": "e.g., Owner, Manager, HR Director"})
