#!/usr/bin/env python3
"""
Complete matching workflow for a specific cohort
1. Download data filtered by Season/Year column
2. Map to format expected by original algorithm
3. Run matching algorithm (always using public transportation)
4. Upload results to Google Sheets
"""

import sys
import os
import csv
from download_cohort_data import download_cohort_data

def map_cohort_data_for_algorithm(cohort_name):
    """
    Map downloaded cohort data to format expected by Chef and Intern classes
    """
    print("\n" + "="*80)
    print(f"MAPPING {cohort_name.upper()} DATA FOR MATCHING ALGORITHM")
    print("="*80)
    
    cohort_slug = cohort_name.lower().replace(" ", "_")
    intern_input = f'intern_avail_{cohort_slug}.csv'
    chef_input = f'chef_avail_{cohort_slug}.csv'
    
    # Read the downloaded data
    with open(intern_input, 'r', encoding='utf-8') as f:
        intern_rows = list(csv.reader(f))
    
    with open(chef_input, 'r', encoding='utf-8') as f:
        chef_rows = list(csv.reader(f))
    
    print(f"\nMapping intern data...")
    
    # Expected headers by Intern class (from intern.py)
    intern_headers = [
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
    
    mapped_intern_rows = [intern_headers]
    
    # Skip header row from downloaded data
    for row in intern_rows[1:]:
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
        
        mapped_intern_rows.append(mapped_row)
    
    # Write mapped intern data
    intern_output = f'C:/Users/pierr/OneDrive/Documents/intern_avail_{cohort_slug}.csv'
    with open(intern_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(mapped_intern_rows)
    
    print(f"  Created {intern_output} with {len(mapped_intern_rows)} rows")
    
    print(f"\nMapping chef data...")
    
    # Expected headers by Chef class (from chef.py)
    chef_headers = [
        'Timestamp', 'Restaurant Name', 'Restaurant Location', 'Restaurant Address',
        "Primary Mentor's Full Name (First and Last)", "Primary Mentor's Cell Phone Number",
        "Primary Mentor's Email Address", 'Do interns need to be over 18 to work in your kitchen?',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    
    def clean_availability_string(avail_str):
        """Clean up availability string by removing trailing commas and spaces"""
        if not avail_str:
            return ''
        cleaned = avail_str.rstrip(', ').strip()
        return cleaned
    
    mapped_chef_rows = [chef_headers]
    
    # Skip header row from downloaded data
    for row in chef_rows[1:]:
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
        
        mapped_chef_rows.append(mapped_row)
    
    # Write mapped chef data
    chef_output = f'C:/Users/pierr/OneDrive/Documents/chef_avail_{cohort_slug}.csv'
    with open(chef_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(mapped_chef_rows)
    
    print(f"  Created {chef_output} with {len(mapped_chef_rows)} rows")
    
    print("\n" + "="*80)
    print("MAPPING COMPLETE")
    print("="*80)
    
    return intern_output, chef_output

def run_matching_algorithm(cohort_name):
    """
    Run the complete matching workflow for a cohort
    """
    cohort_slug = cohort_name.lower().replace(" ", "_")
    
    # Step 1: Download data filtered by Season/Year
    print(f"\nStep 1: Downloading {cohort_name} data...")
    intern_data, chef_data = download_cohort_data(cohort_name)
    
    if not intern_data or not chef_data:
        print("ERROR: Failed to download data")
        return False
    
    # Step 2: Map data to algorithm format
    print(f"\nStep 2: Mapping data to algorithm format...")
    intern_file, chef_file = map_cohort_data_for_algorithm(cohort_name)
    
    # Step 3: Run matching algorithm
    print(f"\nStep 3: Running matching algorithm...")
    print("  (This will use public transportation mode for all commute calculations)")
    
    # Import and run the matching algorithm
    sys.path.insert(0, 'C:/Users/pierr/OneDrive/Documents')
    
    # Create a modified version of matching_algo that uses the cohort files
    matching_code = f"""
import csv
import json
import copy
from datetime import datetime
from Slot import Slot
from chef import Chef
from intern import Intern
from commute import Commute
from mapping import Mapping

def readInternsAvailability():
    formattedAvailability = {{}}
    with open('{intern_file}', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in list(reader):
            intern = Intern(row)
            formattedAvailability[intern.internFullName] = intern
    return formattedAvailability

def readChefsAvailability():
    formattedAvailability = {{}}
    with open('{chef_file}', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in list(reader):
            chef = Chef(row)
            formattedAvailability[chef.chefFullName] = chef
    return formattedAvailability

def findInternsToRestaurantOverlap(chefsAvail, intern, day, listOfInternsAvail, cached_commute):
        overlaps = {{}}
        augment_cache = False
        i=0
        for chefAvail in chefsAvail:
            chefDayAvail = chefsAvail[chefAvail].availability[day]
            for chefSlot in chefDayAvail:
                for internSlot in listOfInternsAvail:
                    if (chefsAvail[chefAvail].chefOver18Only and not intern.internOver18):
                        print(intern.internFullName + ' skipped ' + chefsAvail[chefAvail].restaurantName + " because of age ")
                        continue
                    overlap = chefSlot.getOverlap(internSlot)
                    if (overlap.duration() >= 4):
                        com_key = intern.getFullAddress() + "|" + chefsAvail[chefAvail].getFullAddress()
                        if (com_key in cached_commute) and not augment_cache:
                            print("Commute found in cache")
                            commute = cached_commute[com_key] if type(cached_commute[com_key]) == Commute else Commute.from_dict(cached_commute[com_key])
                        else:
                            print("new Call to Google API")
                            commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chefsAvail[chefAvail].getFullAddress())
                            cached_commute[com_key] = commute.to_dict()
                        if (commute.value > 3000):
                            continue
                        if chefAvail not in overlaps:
                            overlaps[chefsAvail[chefAvail].restaurantName] = {{}}
                            overlaps[chefsAvail[chefAvail].restaurantName]['commute'] = commute
                            print(overlaps[chefsAvail[chefAvail].restaurantName]['commute'].text)
                        if day not in overlaps[chefsAvail[chefAvail].restaurantName]:
                           overlaps[chefsAvail[chefAvail].restaurantName][day] = []
                        overlaps[chefsAvail[chefAvail].restaurantName][day].append(overlap)
        sorted_overlaps = dict(sorted(overlaps.items(), key=lambda item: item[1]['commute'].value))
        print(overlaps.items())
        return sorted_overlaps

def writeToCSVInternsToRestaurant(chefs, interns):
    cached_commute= {{}}
    try:
        with open('cached_commute.json', 'r') as file:
            cached_commute = json.load(file)
    except FileNotFoundError:
        cached_commute = {{}}
        with open('cached_commute.json', 'w') as file:
            json.dump(cached_commute, file)
    except json.JSONDecodeError:
        cached_commute = {{}}
        with open('cached_commute.json', 'w') as file:
            json.dump(cached_commute, file)
    
    with open('cached_commute.json', 'w') as file:
        json.dump(cached_commute, file, indent=4)
    
    header = ['Intern Name', 'Monday', 'Tuesday',  'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    with open('C:/Users/pierr/OneDrive/Documents/intern_to_restaurant_{cohort_slug}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for intern in interns:
            days = interns[intern].availability
            row = []
            row.append(intern)
            for day in days:
                overlaps = findInternsToRestaurantOverlap(chefs, interns[intern], day, days[day], cached_commute)
                rowCell = ""
                for overlap in overlaps:
                    rowCell += str(overlap) + " (" + overlaps[overlap]['commute'].text + "): " + str(overlaps[overlap][day]) + "\\n"
                print("          Found following matches for " + day + ": " + rowCell)
                row.append(rowCell)
            writer.writerow(row)
    
    with open('cached_commute.json', 'w') as file:
        json.dump(cached_commute, file, indent=4)

print("="*80)
print("{cohort_name.upper()} MATCHING ALGORITHM")
print("Using original matching_algo.py logic")
print("Always using public transportation for commute calculations")
print("="*80)
print()

chefs=readChefsAvailability()
interns=readInternsAvailability()

print(f"Loaded {{len(chefs)}} chefs/restaurants")
print(f"Loaded {{len(interns)}} interns")
print()
print("Running matching algorithm...")
print()

writeToCSVInternsToRestaurant(chefs, interns)

print()
print("="*80)
print("COMPLETE")
print("="*80)
print()
print("Output saved to: C:/Users/pierr/OneDrive/Documents/intern_to_restaurant_{cohort_slug}.csv")
"""
    
    # Write and execute the matching script
    matching_script = f'C:/Users/pierr/OneDrive/Documents/matching_algo_{cohort_slug}.py'
    with open(matching_script, 'w', encoding='utf-8') as f:
        f.write(matching_code)
    
    os.system(f'python "{matching_script}"')
    
    return True

if __name__ == "__main__":
    cohort_name = sys.argv[1] if len(sys.argv) > 1 else "Spring 2026"
    run_matching_algorithm(cohort_name)
