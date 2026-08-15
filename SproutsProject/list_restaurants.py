#!/usr/bin/env python3
"""
List all restaurants in database
"""

from app import create_app
from app.models import Restaurant

def list_restaurants():
    """List all restaurants in database"""
    app = create_app()
    app.app_context().push()
    
    print("=== ALL RESTAURANTS IN DATABASE ===")
    
    restaurants = Restaurant.query.all()
    
    for i, restaurant in enumerate(restaurants, 1):
        print(f"{i:2d}. {restaurant.name}")
    
    print(f"\nTotal: {len(restaurants)} restaurants")

if __name__ == "__main__":
    list_restaurants()
