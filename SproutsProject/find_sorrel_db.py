#!/usr/bin/env python3
"""
Find Sorrel Restaurant in database
"""

from app import create_app
from app.models import Restaurant

def find_sorrel_db():
    """Find Sorrel Restaurant in database"""
    app = create_app()
    app.app_context().push()
    
    print("=== FINDING SORREL IN DATABASE ===")
    
    restaurants = Restaurant.query.all()
    
    for restaurant in restaurants:
        if 'sorrel' in restaurant.name.lower():
            print(f"Found: '{restaurant.name}' (ID: {restaurant.id})")
    
    print(f"\nAll restaurants containing 'Sorrel':")
    for restaurant in restaurants:
        if 'sorrel' in restaurant.name.lower():
            print(f"  - {restaurant.name}")

if __name__ == "__main__":
    find_sorrel_db()
