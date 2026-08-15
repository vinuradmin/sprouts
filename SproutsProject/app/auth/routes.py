from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.models import User, Role, Intern, RestaurantOwner, Restaurant
from app.auth.forms import LoginForm, RegistrationForm, InternRegistrationForm, RestaurantOwnerRegistrationForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register')
def register():
    """Registration type selection."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/register_type.html')

@bp.route('/register/intern', methods=['GET', 'POST'])
def register_intern():
    """Intern registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = InternRegistrationForm()
    if form.validate_on_submit():
        # Create user account
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            user_type='intern'
        )
        user.password = form.password.data
        
        # Assign intern role
        intern_role = Role.query.filter_by(name='intern').first()
        if intern_role:
            user.roles = [intern_role]
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create intern profile
        intern = Intern(
            user_id=user.id,
            education_level=form.education_level.data,
            institution=form.institution.data,
            field_of_study=form.field_of_study.data,
            graduation_year=form.graduation_year.data
        )
        
        db.session.add(intern)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_intern.html', form=form)

@bp.route('/register/restaurant', methods=['GET', 'POST'])
def register_restaurant():
    """Restaurant owner registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RestaurantOwnerRegistrationForm()
    if form.validate_on_submit():
        # Create user account
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            user_type='restaurant_owner'
        )
        user.password = form.password.data
        
        # Assign restaurant owner role
        owner_role = Role.query.filter_by(name='restaurant_owner').first()
        if owner_role:
            user.roles = [owner_role]
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create restaurant
        restaurant = Restaurant(
            name=form.restaurant_name.data,
            description=form.restaurant_description.data,
            cuisine_type=form.cuisine_type.data,
            restaurant_type=form.restaurant_type.data,
            email=form.restaurant_email.data,
            phone=form.restaurant_phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            postal_code=form.postal_code.data
        )
        
        db.session.add(restaurant)
        db.session.flush()  # Get restaurant ID
        
        # Create restaurant owner profile
        restaurant_owner = RestaurantOwner(
            user_id=user.id,
            restaurant_id=restaurant.id,
            position=form.position.data,
            is_primary_contact=True,
            can_post_internships=True,
            can_review_applications=True,
            can_manage_restaurant=True
        )
        
        db.session.add(restaurant_owner)
        db.session.commit()
        
        flash('Registration successful! Please log in. Your restaurant will be verified shortly.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_restaurant.html', form=form)
