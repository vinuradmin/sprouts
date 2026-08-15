#!/usr/bin/env python3
"""
Map Spring 2026 CSV data to match the exact format expected by the original matching_algo.py
"""

import csv

def map_intern_csv():
    """Map Spring 2026 intern CSV to format expected by Intern class"""
    print("Mapping intern CSV...")
    
    # Read Spring 2026 intern data
    with open('intern_avail_spring_2026.csv', 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    
    # Expected headers by Intern class (from intern.py)
    headers = [
        'Timestamp', 'First Name', 'Last Name', 'Referral Partner', '', 'Rating', '', 'ready?', 
        'Chef ready?', 'restaurantname', 'chefname', 'Chef first name', 'chef email', 'schedule', 
        'trialdate', 'trialtime', 'start', 'end', 'hours', 'Compensation', 'Secondary Chef Name', 
        'Secondary Chef Email', 'Secondary Chef Phone', 'chefphone', 'restaurantaddress', 
        'internname', 'interndescription', 'Behavior Notes', 'intern phone', 'Off', 
        'Are there any breaks or holidays you will be unable to work during? Please write the date ranges separated by a comma if there are multiple. ',
        'Closures', 'Street Address', 'City', 'Zip Code', 'Are you over 18 years old?', 'Age',
        'What transportation will you use?', 'How long are you willing to commute to your internship?',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    
    # Spring 2026 columns mapping (0-indexed):
    # 0: Timestamp, 1: First Name, 2: Last Name, 3: Referral Partner
    # 32: Street Address, 33: City, 34: Zip Code, 35: Over 18, 36: Age
    # 37: Transportation, 38: Commute preference
    # 39-45: Monday-Sunday availability
    
    mapped_rows = [headers]  # Start with header row
    
    for row in rows:
        if len(row) < 46:
            continue
        
        mapped_row = [
            row[0],   # Timestamp
            row[1],   # First Name
            row[2],   # Last Name
            row[3] if len(row) > 3 else '',   # Referral Partner
            '',       # Empty column
            '',       # Rating
            '',       # Empty
            '',       # ready?
            '',       # Chef ready?
            '',       # restaurantname
            '',       # chefname
            '',       # Chef first name
            '',       # chef email
            '',       # schedule
            '',       # trialdate
            '',       # trialtime
            '',       # start
            '',       # end
            '',       # hours
            '',       # Compensation
            '',       # Secondary Chef Name
            '',       # Secondary Chef Email
            '',       # Secondary Chef Phone
            '',       # chefphone
            '',       # restaurantaddress
            '',       # internname
            '',       # interndescription
            '',       # Behavior Notes
            row[28] if len(row) > 28 else '',  # intern phone
            '',       # Off
            row[30] if len(row) > 30 else '',  # Breaks/holidays
            '',       # Closures
            row[32] if len(row) > 32 else '',  # Street Address
            row[33] if len(row) > 33 else '',  # City
            row[34] if len(row) > 34 else '',  # Zip Code
            row[35] if len(row) > 35 else '',  # Are you over 18?
            row[36] if len(row) > 36 else '',  # Age
            row[37] if len(row) > 37 else '',  # Transportation
            row[38] if len(row) > 38 else '',  # Commute preference
            row[39] if len(row) > 39 else '',  # Monday
            row[40] if len(row) > 40 else '',  # Tuesday
            row[41] if len(row) > 41 else '',  # Wednesday
            row[42] if len(row) > 42 else '',  # Thursday
            row[43] if len(row) > 43 else '',  # Friday
            row[44] if len(row) > 44 else '',  # Saturday
            row[45] if len(row) > 45 else ''   # Sunday
        ]
        
        mapped_rows.append(mapped_row)
    
    # Write to new CSV
    with open('C:/Users/pierr/OneDrive/Documents/intern_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(mapped_rows)
    
    print(f"  Created intern_avail_spring_2026.csv with {len(mapped_rows)} rows")

def clean_availability_string(avail_str):
    """Clean up availability string by removing trailing commas and spaces"""
    if not avail_str:
        return ''
    # Remove trailing comma and space, then strip
    cleaned = avail_str.rstrip(', ').strip()
    return cleaned

def map_chef_csv():
    """Map Spring 2026 chef CSV to format expected by Chef class"""
    print("Mapping chef CSV...")
    
    # Read Spring 2026 chef data
    with open('chef_avail_spring_2026.csv', 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    
    # Expected headers by Chef class (from chef.py)
    headers = [
        'Timestamp', 'Restaurant Name', 'Restaurant Location', 'Restaurant Address',
        "Primary Mentor's Full Name (First and Last)", "Primary Mentor's Cell Phone Number",
        "Primary Mentor's Email Address", 'Do interns need to be over 18 to work in your kitchen?',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    
    # Spring 2026 columns mapping:
    # 3: Timestamp, 1: Restaurant Name, 6: City (Location), 7: Address
    # 8: Chef Name, 9: Chef Phone, 10: Chef Email, 5: Over 18 requirement
    # 26-32: Monday-Sunday (columns AA-AG)
    
    mapped_rows = [headers]  # Start with header row
    
    for row in rows:
        if len(row) < 33:
            continue
        
        mapped_row = [
            row[3] if len(row) > 3 else '',   # Timestamp
            row[1] if len(row) > 1 else '',   # Restaurant Name
            row[6] if len(row) > 6 else '',   # Restaurant Location (City)
            row[7] if len(row) > 7 else '',   # Restaurant Address
            row[8] if len(row) > 8 else '',   # Chef Name
            row[9] if len(row) > 9 else '',   # Chef Phone
            row[10] if len(row) > 10 else '', # Chef Email
            row[5] if len(row) > 5 else '',   # Over 18 requirement
            clean_availability_string(row[26] if len(row) > 26 else ''), # Monday
            clean_availability_string(row[27] if len(row) > 27 else ''), # Tuesday
            clean_availability_string(row[28] if len(row) > 28 else ''), # Wednesday
            clean_availability_string(row[29] if len(row) > 29 else ''), # Thursday
            clean_availability_string(row[30] if len(row) > 30 else ''), # Friday
            clean_availability_string(row[31] if len(row) > 31 else ''), # Saturday
            clean_availability_string(row[32] if len(row) > 32 else '')  # Sunday
        ]
        
        mapped_rows.append(mapped_row)
    
    # Write to new CSV
    with open('C:/Users/pierr/OneDrive/Documents/chef_avail_spring_2026.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(mapped_rows)
    
    print(f"  Created chef_avail_spring_2026.csv with {len(mapped_rows)} rows")

def main():
    print("="*80)
    print("MAPPING SPRING 2026 DATA FOR ORIGINAL MATCHING_ALGO.PY")
    print("="*80)
    print()
    
    map_intern_csv()
    print()
    map_chef_csv()
    
    print()
    print("="*80)
    print("COMPLETE")
    print("="*80)
    print("\nMapped files created in C:/Users/pierr/OneDrive/Documents/:")
    print("  - intern_avail_spring_2026.csv")
    print("  - chef_avail_spring_2026.csv")
    print("\nThese files are now compatible with the original matching_algo.py")

if __name__ == "__main__":
    main()
