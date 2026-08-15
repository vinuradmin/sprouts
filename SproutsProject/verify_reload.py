#!/usr/bin/env python3
"""
Verify that CSV data was loaded correctly with availability
"""

from app import create_app
from app.models import Intern, Restaurant, User, InternAvailability

def verify_reload():
    """Verify the reloaded data"""
    app = create_app()
    app.app_context().push()
    
    print("=== VERIFYING RELOADED DATA ===")
    
    interns = Intern.query.join(User).all()
    restaurants = Restaurant.query.all()
    
    print(f"Interns: {len(interns)}")
    print(f"Restaurants: {len(restaurants)}")
    
    # Check a few specific interns
    test_interns = ["Angel Ruiz", "Shelsea Vasquez", "Asslin Espinal"]
    
    for intern_name in test_interns:
        intern = None
        # Try exact match first
        intern = Intern.query.join(User).filter(User.full_name == intern_name).first()
        
        if not intern:
            # Try with trailing spaces
            intern = Intern.query.join(User).filter(User.full_name == f"{intern_name} ").first()
        
        if intern:
            print(f"\n{intern_name}:")
            print(f"  Address: {intern.get_full_address()}")
            
            # Check availability
            avail = intern.availability
            if avail:
                print(f"  Availability:")
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    am = getattr(avail, f'{day}_am')
                    pm = getattr(avail, f'{day}_pm')
                    if am or pm:
                        print(f"    {day.capitalize()}: AM={am}, PM={pm}")
            else:
                print(f"  No availability data found")
        else:
            print(f"\n{intern_name}: Not found")
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    verify_reload()
