#!/usr/bin/env python3
"""
Database initialization script for SproutsProject.
This script creates the database tables and populates them with initial data.
"""

from app import create_app, db
from app.models import User, Role, Intern, Restaurant, RestaurantOwner, Internship
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta

def init_database():
    """Initialize the database with tables and seed data."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate them
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating database tables...")
        db.create_all()
        
        # Create roles
        print("Creating user roles...")
        roles = [
            Role(name='admin', description='Administrator with full access'),
            Role(name='intern', description='Intern seeking internship opportunities'),
            Role(name='restaurant_owner', description='Restaurant owner/manager posting internships')
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.commit()
        
        # Create admin user
        print("Creating admin user...")
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User(
            email='admin@sproutsproject.com',
            first_name='Admin',
            last_name='User',
            user_type='admin',
            active=True,
            confirmed_at=datetime.utcnow()
        )
        admin_user.password = 'admin123'
        admin_user.roles = [admin_role]
        db.session.add(admin_user)
        
        # Create sample intern user
        print("Creating sample intern user...")
        intern_role = Role.query.filter_by(name='intern').first()
        intern_user = User(
            email='intern@example.com',
            first_name='John',
            last_name='Doe',
            phone='555-0123',
            user_type='intern',
            active=True,
            confirmed_at=datetime.utcnow()
        )
        intern_user.password = 'intern123'
        intern_user.roles = [intern_role]
        db.session.add(intern_user)
        db.session.flush()
        
        # Create intern profile
        intern_profile = Intern(
            user_id=intern_user.id,
            education_level='bachelor',
            institution='Culinary Institute of America',
            field_of_study='Culinary Arts',
            graduation_year=2024,
            interests='Fine dining, pastry arts, sustainable cooking',
            preferred_locations='Downtown, Midtown',
            preferred_restaurant_types='Fine dining, casual dining',
            is_seeking_internship=True,
            transportation_method='driving',
            max_commute_minutes=45,
            address='456 Student Ave',
            city='New York',
            country='USA',
            postal_code='10002'
        )
        db.session.add(intern_profile)
        db.session.flush()
        
        # Create intern availability
        from app.models.intern import InternAvailability
        intern_availability = InternAvailability(
            intern_id=intern_profile.id,
            monday_am=True,
            monday_pm=True,
            tuesday_am=True,
            tuesday_pm=False,
            wednesday_am=True,
            wednesday_pm=True,
            thursday_am=False,
            thursday_pm=True,
            friday_am=True,
            friday_pm=True,
            saturday_am=False,
            saturday_pm=False,
            sunday_am=False,
            sunday_pm=False
        )
        db.session.add(intern_availability)
        
        # Create sample restaurant owner user
        print("Creating sample restaurant owner...")
        owner_role = Role.query.filter_by(name='restaurant_owner').first()
        owner_user = User(
            email='owner@restaurant.com',
            first_name='Jane',
            last_name='Smith',
            phone='555-0456',
            user_type='restaurant_owner',
            active=True,
            confirmed_at=datetime.utcnow()
        )
        owner_user.password = 'owner123'
        owner_user.roles = [owner_role]
        db.session.add(owner_user)
        db.session.flush()
        
        # Create sample restaurant
        restaurant = Restaurant(
            name='The Golden Spoon',
            description='An upscale dining establishment specializing in contemporary American cuisine with a focus on locally sourced ingredients.',
            cuisine_type='american',
            restaurant_type='fine_dining',
            email='info@goldenspoon.com',
            phone='555-0789',
            website='https://www.goldenspoon.com',
            address='123 Main Street',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            established_year=2015,
            number_of_employees=25,
            seating_capacity=80,
            is_active=True,
            is_verified=True
        )
        db.session.add(restaurant)
        db.session.flush()
        
        # Create restaurant owner profile
        restaurant_owner = RestaurantOwner(
            user_id=owner_user.id,
            restaurant_id=restaurant.id,
            position='General Manager',
            is_primary_contact=True,
            can_post_internships=True,
            can_review_applications=True,
            can_manage_restaurant=True
        )
        db.session.add(restaurant_owner)
        
        # Create sample internships
        print("Creating sample internships...")
        internships = [
            Internship(
                restaurant_id=restaurant.id,
                title='Kitchen Assistant Intern',
                description='Join our kitchen team and learn from experienced chefs. You will assist with food preparation, learn knife skills, and understand kitchen operations in a fine dining environment.',
                department='kitchen',
                required_skills='Basic knife skills, food safety knowledge',
                preferred_skills='Culinary school enrollment, previous kitchen experience',
                education_requirements='High school diploma or equivalent',
                experience_required='No prior experience required',
                start_date=date.today() + timedelta(days=30),
                end_date=date.today() + timedelta(days=120),
                duration_weeks=12,
                hours_per_week=25,
                is_flexible_schedule=True,
                requires_weekends=True,
                requires_evenings=True,
                is_paid=True,
                hourly_rate=15.00,
                other_benefits='Free meals, uniform provided, mentorship program',
                application_deadline=date.today() + timedelta(days=14),
                positions_available=2,
                contact_email='careers@goldenspoon.com',
                contact_person='Chef Michael Johnson',
                application_instructions='Please submit your resume and a brief cover letter explaining your interest in culinary arts.',
                required_documents='Resume, Cover Letter',
                is_active=True,
                is_featured=True
            ),
            Internship(
                restaurant_id=restaurant.id,
                title='Front of House Intern',
                description='Learn the art of hospitality in our front of house operations. Gain experience in customer service, table service, and restaurant management.',
                department='front_of_house',
                required_skills='Customer service skills, communication skills',
                preferred_skills='Previous hospitality experience, bilingual abilities',
                education_requirements='High school diploma or equivalent',
                experience_required='Customer service experience preferred',
                start_date=date.today() + timedelta(days=45),
                end_date=date.today() + timedelta(days=135),
                duration_weeks=12,
                hours_per_week=20,
                is_flexible_schedule=False,
                requires_weekends=True,
                requires_evenings=True,
                is_paid=True,
                hourly_rate=14.00,
                other_benefits='Free meals, professional development workshops',
                application_deadline=date.today() + timedelta(days=21),
                positions_available=1,
                contact_email='hr@goldenspoon.com',
                contact_person='Sarah Williams',
                application_instructions='We are looking for enthusiastic individuals who are passionate about hospitality.',
                required_documents='Resume, Cover Letter, References',
                is_active=True,
                is_featured=False
            )
        ]
        
        for internship in internships:
            db.session.add(internship)
        
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print("\nSample login credentials:")
        print("Admin: admin@sproutsproject.com / admin123")
        print("Intern: intern@example.com / intern123")
        print("Restaurant Owner: owner@restaurant.com / owner123")

if __name__ == '__main__':
    init_database()
