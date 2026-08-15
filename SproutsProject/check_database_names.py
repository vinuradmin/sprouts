#!/usr/bin/env python3
"""
Check what intern names are actually in the Flask database
"""

from app import create_app
from app.models import Intern, Restaurant, User

def check_database_interns():
    """Check all intern names in the database"""
    app = create_app()
    app.app_context().push()
    
    interns = Intern.query.join(User).all()
    
    print("=== INTERNS IN FLASK DATABASE ===")
    for i, intern in enumerate(interns, 1):
        print(f"{i:2d}. '{intern.user.full_name}'")
    
    print(f"\nTotal: {len(interns)} interns")

def check_database_restaurants():
    """Check all restaurant names in the database"""
    app = create_app()
    app.app_context().push()
    
    restaurants = Restaurant.query.all()
    
    print("\n=== RESTAURANTS IN FLASK DATABASE ===")
    for i, restaurant in enumerate(restaurants, 1):
        print(f"{i:2d}. '{restaurant.name}'")
    
    print(f"\nTotal: {len(restaurants)} restaurants")

if __name__ == "__main__":
    check_database_interns()
    check_database_restaurants()
