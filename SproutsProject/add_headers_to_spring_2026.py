#!/usr/bin/env python3
"""
Add proper headers to Spring 2026 CSV files to match the format expected by Chef and Intern classes
"""

import csv

# Expected headers from the original fall CSV files
INTERN_HEADERS = ['Timestamp', 'First Name', 'Last Name', 'Referral Partner', '', 'Rating', '', 'ready?', 'Chef ready?', 'restaurantname', 'chefname', 'Chef first name', 'chef email', 'schedule', 'trialdate', 'trialtime', 'start', 'end', 'hours', 'Compensation', 'Secondary Chef Name', 'Secondary Chef Email', 'Secondary Chef Phone', 'chefphone', 'restaurantaddress', 'internname', 'interndescription', 'Behavior Notes', 'intern phone', 'Off', 'Are there any breaks or holidays you will be unable to work during? Please write the date ranges separated by a comma if there are multiple. ', 'Closures', 'Street Address', 'City', 'Zip Code', 'Are you over 18 years old?', 'Age', 'What transportation will you use?', 'How long are you willing to commute to your internship?', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

CHEF_HEADERS = ['Newest Info', 'Restaurant Name', 'Season', 'Timestamp', 'Status', 'Over 18', 'City', 'Restaurant Address', 'Chef Name', 'Chef Phone', 'Chef Email', '', 'Interested', 'Completed', 'Training', 'Notes', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def add_headers_to_csv(input_file, output_file, headers):
    """Add headers to a CSV file"""
    print(f"Processing {input_file}...")
    
    # Read all rows
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    print(f"  Read {len(rows)} rows")
    
    # Write with headers
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  Saved to {output_file} with headers")

def main():
    print("="*80)
    print("ADDING HEADERS TO SPRING 2026 CSV FILES")
    print("="*80)
    print()
    
    # Add headers to intern CSV
    add_headers_to_csv(
        'intern_avail_spring_2026.csv',
        'intern_avail_spring_2026_with_headers.csv',
        INTERN_HEADERS
    )
    
    print()
    
    # Add headers to chef CSV
    add_headers_to_csv(
        'chef_avail_spring_2026.csv',
        'chef_avail_spring_2026_with_headers.csv',
        CHEF_HEADERS
    )
    
    print()
    print("="*80)
    print("COMPLETE")
    print("="*80)
    print("\nCreated files:")
    print("  - intern_avail_spring_2026_with_headers.csv")
    print("  - chef_avail_spring_2026_with_headers.csv")

if __name__ == "__main__":
    main()
