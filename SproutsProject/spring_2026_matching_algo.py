#!/usr/bin/env python3
"""
Adapted from original matching_algo.py
Lists restaurant options for Spring 2026 interns sorted by commute time
Outputs to CSV format
"""

import sys
import os
import csv
import json
import copy

# Add paths for imports
sys.path.append('C:/Users/pierr/OneDrive/Documents')

from Slot import Slot
from chef import Chef
from intern import Intern
from commute import Commute

def readInternsAvailability():
    """Read Spring 2026 intern availability from CSV"""
    formattedAvailability = {}
    with open('intern_avail_spring_2026_formatted.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in list(reader):
            try:
                intern = Intern(row)
                formattedAvailability[intern.internFullName] = intern
            except Exception as e:
                print(f"Error processing intern row: {e}")
                continue
    return formattedAvailability

def readChefsAvailability():
    """Read Spring 2026 chef/restaurant availability from CSV"""
    formattedAvailability = {}
    with open('chef_avail_spring_2026_formatted.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in list(reader):
            try:
                chef = Chef(row)
                formattedAvailability[chef.chefFullName] = chef
            except Exception as e:
                print(f"Error processing chef row: {e}")
                continue
    return formattedAvailability

def findInternsToRestaurantOverlap(chefsAvail, intern, day, listOfInternsAvail, cached_commute):
    """Find restaurant options for an intern on a specific day, sorted by commute"""
    overlaps = {}
    augment_cache = False
    
    for chefAvail in chefsAvail:
        chefDayAvail = chefsAvail[chefAvail].availability[day]
        for chefSlot in chefDayAvail:
            for internSlot in listOfInternsAvail:
                # Check age restriction
                if (chefsAvail[chefAvail].chefOver18Only and not intern.internOver18):
                    print(f"{intern.internFullName} skipped {chefsAvail[chefAvail].restaurantName} because of age")
                    continue
                
                # Check time overlap
                overlap = chefSlot.getOverlap(internSlot)
                if (overlap.duration() >= 4):
                    # Get or calculate commute
                    com_key = intern.getFullAddress() + "|" + chefsAvail[chefAvail].getFullAddress()
                    
                    if (com_key in cached_commute) and not augment_cache:
                        print("Commute found in cache")
                        commute = cached_commute[com_key] if type(cached_commute[com_key]) == Commute else Commute.from_dict(cached_commute[com_key])
                    else:
                        print("New call to Google API")
                        commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chefsAvail[chefAvail].getFullAddress())
                        cached_commute[com_key] = commute.to_dict()
                    
                    # Skip if commute too long (50 minutes = 50000 meters in time)
                    if (commute.value > 3000):  # 50 minutes in seconds
                        continue
                    
                    # Store overlap
                    if chefAvail not in overlaps:
                        overlaps[chefsAvail[chefAvail].restaurantName] = {}
                        overlaps[chefsAvail[chefAvail].restaurantName]['commute'] = commute
                        print(overlaps[chefsAvail[chefAvail].restaurantName]['commute'].text)
                    
                    if day not in overlaps[chefsAvail[chefAvail].restaurantName]:
                        overlaps[chefsAvail[chefAvail].restaurantName][day] = []
                    
                    overlaps[chefsAvail[chefAvail].restaurantName][day].append(overlap)
    
    # Sort by commute time
    sorted_overlaps = dict(sorted(overlaps.items(), key=lambda item: item[1]['commute'].value))
    
    return sorted_overlaps

def writeToCSVInternsToRestaurant(chefs, interns):
    """Write intern to restaurant options CSV, sorted by commute time"""
    
    # Load cached commute data
    cached_commute = {}
    try:
        with open('cached_commute.json', 'r') as file:
            cached_commute = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        cached_commute = {}
        with open('cached_commute.json', 'w') as file:
            json.dump(cached_commute, file)
    
    print("="*80)
    print("GENERATING SPRING 2026 INTERN TO RESTAURANT OPTIONS")
    print("Sorted by commute time")
    print("="*80)
    
    # CSV header
    header = ['Intern Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    with open('spring_2026_intern_to_restaurant.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        for intern in interns:
            print(f"\nProcessing: {intern}")
            days = interns[intern].availability
            row = []
            row.append(intern)
            
            for day in days:
                overlaps = findInternsToRestaurantOverlap(chefs, interns[intern], day, days[day], cached_commute)
                rowCell = ""
                
                for overlap in overlaps:
                    rowCell += str(overlap) + " (" + overlaps[overlap]['commute'].text + "): " + str(overlaps[overlap][day]) + "\n"
                
                print(f"  {day}: Found {len(overlaps)} restaurant options")
                row.append(rowCell)
            
            writer.writerow(row)
    
    # Save updated cache
    with open('cached_commute.json', 'w') as file:
        json.dump(cached_commute, file, indent=4)
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print(f"Output saved to: spring_2026_intern_to_restaurant.csv")
    print(f"Commute cache saved to: cached_commute.json")

def main():
    """Main function"""
    print("Spring 2026 Matching Algorithm")
    print("Reading availability data...\n")
    
    chefs = readChefsAvailability()
    interns = readInternsAvailability()
    
    print(f"Loaded {len(chefs)} restaurants")
    print(f"Loaded {len(interns)} interns\n")
    
    writeToCSVInternsToRestaurant(chefs, interns)

if __name__ == "__main__":
    main()
