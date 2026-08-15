#!/usr/bin/env python3
"""
Find specific interns in the database
"""

from app import create_app
from app.models import Intern, User

def find_interns():
    """Find specific interns"""
    app = create_app()
    app.app_context().push()
    
    interns = Intern.query.join(User).all()
    
    target_names = ["Angel", "Shelsea", "Asslin"]
    
    print("=== FINDING TARGET INTERNS ===")
    
    for intern in interns:
        full_name = intern.user.full_name
        for target in target_names:
            if target in full_name:
                print(f"Found: '{full_name}' (ID: {intern.id})")
                
                # Check availability
                avail = intern.availability
                if avail:
                    print(f"  Has availability data")
                    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    has_any = False
                    for day in days:
                        am = getattr(avail, f'{day}_am')
                        pm = getattr(avail, f'{day}_pm')
                        if am or pm:
                            has_any = True
                            break
                    print(f"  Has any availability: {has_any}")
                else:
                    print(f"  No availability data")
                print()

if __name__ == "__main__":
    find_interns()
