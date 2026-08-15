#!/usr/bin/env python3
"""
Reload CSV data to fix availability issues
"""

from app import create_app
from app.services.csv_data_loader import CSVDataLoader

def reload_csv_data():
    """Reload data from CSV files"""
    app = create_app()
    app.app_context().push()
    
    print("=== RELOADING CSV DATA ===")
    
    loader = CSVDataLoader()
    
    # Clear existing data and reload from CSV
    print("Clearing existing data...")
    result = loader.load_data_from_csv(
        clear_existing=True,
        intern_csv_path="../intern_avail_fall.csv",
        restaurant_csv_path="../chef_avail_fall.csv"
    )
    
    print(f"Load result: {result}")
    
    print("=== CSV DATA RELOADED ===")

if __name__ == "__main__":
    reload_csv_data()
