#!/usr/bin/env python3
"""
Check what names were actually loaded from CSV
"""

from app import create_app
from app.models import Intern, User

def check_loaded_names():
    """Check loaded intern names"""
    app = create_app()
    app.app_context().push()
    
    interns = Intern.query.join(User).all()
    
    print("=== LOADED INTERN NAMES ===")
    for i, intern in enumerate(interns, 1):
        print(f"{i:2d}. '{intern.user.full_name}'")
    
    print(f"\nTotal: {len(interns)} interns")

if __name__ == "__main__":
    check_loaded_names()
