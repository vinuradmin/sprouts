"""
Google Cloud Function for Sprouts Matching Algorithm
Handles HTTP requests from Google Apps Script and runs matching algorithm
"""

from flask import Flask, request, jsonify
from google.oauth2 import service_account
from google.auth import default
from googleapiclient.discovery import build
from google.cloud import storage
import googlemaps
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg')
CACHE_BUCKET = os.environ.get('CACHE_BUCKET', 'sprouts-commute-cache')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Commute cache (loaded from GCS at start, saved at end)
commute_cache = {}

def load_commute_cache():
    """Load commute cache from Google Cloud Storage"""
    global commute_cache
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(CACHE_BUCKET)
        blob = bucket.blob('commute_cache.json')
        
        if blob.exists():
            cache_data = json.loads(blob.download_as_text())
            commute_cache = cache_data
            print(f"[CACHE] Loaded {len(commute_cache)} cached commutes from GCS")
            return True
    except Exception as e:
        print(f"[CACHE] Failed to load cache: {e}")
        commute_cache = {}
    
    return False

def save_commute_cache():
    """Save commute cache to Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(CACHE_BUCKET)
        blob = bucket.blob('commute_cache.json')
        
        blob.upload_from_string(
            json.dumps(commute_cache, indent=2),
            content_type='application/json'
        )
        print(f"[CACHE] Saved {len(commute_cache)} cached commutes to GCS")
        return True
    except Exception as e:
        print(f"[CACHE] Failed to save cache: {e}")
    
    return False

def get_sheets_service():
    """
    Get Google Sheets API service
    Uses built-in credentials in Cloud Function, service account key locally
    """
    # Check if running in Cloud Function
    if os.getenv('FUNCTION_NAME') or os.getenv('K_SERVICE'):
        # Running in Cloud Function - use default credentials (built-in service account)
        creds, _ = default(scopes=SCOPES)
    else:
        # Running locally - use service account key file
        creds = service_account.Credentials.from_service_account_file(
            'service-account-key.json', scopes=SCOPES)
    
    return build('sheets', 'v4', credentials=creds)

def read_sheet_data(sheet_name):
    """Read all data from a sheet into memory"""
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_name
    ).execute()
    return result.get('values', [])

def find_column_index(header_row, column_name):
    """Find the index of a column by name"""
    for i, cell in enumerate(header_row):
        if str(cell).strip() == column_name:
            return i
    return None

def filter_by_cohort(data, cohort_name):
    """Filter data by Season/Year column"""
    if not data or len(data) < 2:
        return []
    
    # Find header row and Season/Year column
    header_row = None
    season_year_col = None
    
    for i, row in enumerate(data):
        season_year_col = find_column_index(row, 'Season/Year')
        if season_year_col is not None:
            header_row = i
            break
    
    if header_row is None or season_year_col is None:
        return []
    
    # Filter rows by cohort
    filtered = [data[header_row]]  # Include header
    
    for i in range(header_row + 1, len(data)):
        row = data[i]
        if len(row) > season_year_col:
            if str(row[season_year_col]).strip() == cohort_name:
                filtered.append(row)
    
    return filtered

def get_commute_time(origin, destination):
    """
    Calculate commute time using Google Maps API
    Always uses transit mode (public transportation)
    Uses cache to avoid redundant API calls
    """
    cache_key = f"{origin}|{destination}"
    
    # Check cache
    if cache_key in commute_cache:
        print(f"[CACHE HIT] {origin[:30]}... -> {destination[:30]}...")
        return commute_cache[cache_key]
    
    print(f"[CACHE MISS] {origin[:30]}... -> {destination[:30]}... (calling API)")
    
    try:
        # Always use transit mode
        result = gmaps.distance_matrix(origin, destination, mode='transit')
        
        if result['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            if 'duration' in element:
                duration = element['duration']
                commute = {
                    'text': duration['text'],
                    'value': duration['value'],
                    'timestamp': datetime.utcnow().isoformat()
                }
                commute_cache[cache_key] = commute
                return commute
    except Exception as e:
        print(f"Error calculating commute: {e}")
    
    # Return error value
    return {'text': 'Error', 'value': 100000}

def parse_availability(avail_str):
    """Parse availability string into list of time slots"""
    if not avail_str or avail_str == 'Unavailable' or avail_str.strip() == '':
        return []
    
    # Clean and split by comma
    slots = [s.strip() for s in avail_str.split(',')]
    return [s for s in slots if s and s != 'Unavailable']

def parse_time_slot(slot_str):
    """
    Parse a time slot string like '10AM-11AM' into start and end hours
    Returns tuple (start_hour, end_hour) in 24-hour format
    """
    if not slot_str or '-' not in slot_str:
        return None
    
    try:
        parts = slot_str.split('-')
        if len(parts) != 2:
            return None
        
        start_str = parts[0].strip()
        end_str = parts[1].strip()
        
        # Convert to 24-hour format
        def to_24_hour(time_str):
            time_str = time_str.upper()
            if 'PM' in time_str:
                hour = int(time_str.replace('PM', '').strip())
                return hour if hour == 12 else hour + 12
            else:  # AM
                hour = int(time_str.replace('AM', '').strip())
                return hour if hour != 12 else 0
        
        start_hour = to_24_hour(start_str)
        end_hour = to_24_hour(end_str)
        
        return (start_hour, end_hour)
    except:
        return None

def calculate_overlap(intern_slots, chef_slots):
    """
    Calculate overlap between intern and chef availability slots
    Returns total overlap duration in hours
    """
    if not intern_slots or not chef_slots:
        return 0
    
    total_overlap = 0
    
    for intern_slot in intern_slots:
        intern_time = parse_time_slot(intern_slot)
        if not intern_time:
            continue
        
        for chef_slot in chef_slots:
            chef_time = parse_time_slot(chef_slot)
            if not chef_time:
                continue
            
            # Calculate overlap
            overlap_start = max(intern_time[0], chef_time[0])
            overlap_end = min(intern_time[1], chef_time[1])
            
            if overlap_end > overlap_start:
                total_overlap += (overlap_end - overlap_start)
    
    return total_overlap

def run_matching_algorithm(intern_data, chef_data):
    """
    Run the matching algorithm on filtered data
    This preserves the original algorithm logic exactly
    """
    results = []
    
    # Parse intern data
    if len(intern_data) < 2:
        return results
    
    intern_header = intern_data[0]
    
    # Find column indices for interns
    first_name_col = find_column_index(intern_header, 'First Name')
    last_name_col = find_column_index(intern_header, 'Last Name')
    street_col = find_column_index(intern_header, 'Street Address')
    city_col = find_column_index(intern_header, 'City')
    zip_col = find_column_index(intern_header, 'Zip Code')
    over_18_col = find_column_index(intern_header, 'Are you over 18 years old?')
    
    # Day columns (assuming they're the last 7 columns)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_cols = {}
    for day in day_names:
        day_cols[day] = find_column_index(intern_header, day)
    
    # Parse chef data
    if len(chef_data) < 2:
        return results
    
    chef_header = chef_data[0]
    
    # Find column indices for chefs
    restaurant_name_col = find_column_index(chef_header, 'Restaurant Name')
    restaurant_address_col = find_column_index(chef_header, 'Restaurant Address')
    over_18_required_col = find_column_index(chef_header, 'Do interns need to be over 18 to work in your kitchen?')
    
    # Day columns for chefs
    chef_day_cols = {}
    for day in day_names:
        chef_day_cols[day] = find_column_index(chef_header, day)
    
    # Process each intern
    for intern_row in intern_data[1:]:
        if len(intern_row) < max(filter(None, [first_name_col, last_name_col])):
            continue
        
        intern_name = f"{intern_row[first_name_col]} {intern_row[last_name_col]}"
        intern_address = f"{intern_row[street_col]}, {intern_row[city_col]}, {intern_row[zip_col]}"
        intern_over_18 = intern_row[over_18_col] == 'Yes' if over_18_col and len(intern_row) > over_18_col else False
        
        # Get intern availability for each day
        intern_availability = {}
        for day in day_names:
            if day_cols[day] and len(intern_row) > day_cols[day]:
                intern_availability[day] = parse_availability(intern_row[day_cols[day]])
        
        # Find matches for each day
        intern_matches = {
            'intern_name': intern_name,
            'matches_by_day': {}
        }
        
        for day in day_names:
            intern_day_slots = intern_availability.get(day, [])
            if not intern_day_slots:
                intern_matches['matches_by_day'][day] = []
                continue
            
            day_matches = []
            
            # Check each restaurant
            for chef_row in chef_data[1:]:
                if len(chef_row) < max(filter(None, [restaurant_name_col, restaurant_address_col])):
                    continue
                
                restaurant_name = chef_row[restaurant_name_col]
                restaurant_address = chef_row[restaurant_address_col]
                requires_18 = chef_row[over_18_required_col] == 'Yes' if over_18_required_col and len(chef_row) > over_18_required_col else False
                
                # Check age restriction
                if requires_18 and not intern_over_18:
                    continue
                
                # Get chef availability for this day
                if chef_day_cols[day] and len(chef_row) > chef_day_cols[day]:
                    chef_day_slots = parse_availability(chef_row[chef_day_cols[day]])
                else:
                    chef_day_slots = []
                
                if not chef_day_slots:
                    continue
                
                # Calculate overlap
                overlap_hours = calculate_overlap(intern_day_slots, chef_day_slots)
                
                # Require at least 4 hours of overlap (original algorithm requirement)
                if overlap_hours < 4:
                    continue
                
                # Calculate commute
                commute = get_commute_time(intern_address, restaurant_address)
                
                # Skip if commute too long (50 minutes = 3000 seconds)
                if commute['value'] > 3000:
                    continue
                
                day_matches.append({
                    'restaurant': restaurant_name,
                    'commute_text': commute['text'],
                    'commute_minutes': commute['value'] // 60,
                    'overlap_hours': overlap_hours
                })
            
            # Sort by commute time (original algorithm behavior)
            day_matches.sort(key=lambda x: x['commute_minutes'])
            
            intern_matches['matches_by_day'][day] = day_matches
        
        results.append(intern_matches)
    
    return results

@app.route('/run-matching', methods=['POST'])
def run_matching():
    """
    Main endpoint for running the matching algorithm
    Expects JSON: {"cohort": "Spring 2026"}
    """
    try:
        data = request.get_json()
        cohort_name = data.get('cohort', 'Spring 2026')
        
        print(f"Running matching for cohort: {cohort_name}")
        
        # Load commute cache from GCS
        print("Loading commute cache from GCS...")
        load_commute_cache()
        
        # Read data from Google Sheets
        print("Reading Intern Availabilities...")
        intern_data = read_sheet_data('Intern Availabilities')
        
        print("Reading Chef Availabilities...")
        chef_data = read_sheet_data('Chef Availabilities')
        
        # Filter by cohort
        print(f"Filtering by cohort: {cohort_name}")
        filtered_interns = filter_by_cohort(intern_data, cohort_name)
        filtered_chefs = filter_by_cohort(chef_data, cohort_name)
        
        print(f"Found {len(filtered_interns)-1} interns and {len(filtered_chefs)-1} chefs")
        
        # Run matching algorithm
        print("Running matching algorithm...")
        results = run_matching_algorithm(filtered_interns, filtered_chefs)
        
        print(f"Generated matches for {len(results)} interns")
        
        # Save updated cache to GCS
        print("Saving commute cache to GCS...")
        save_commute_cache()
        
        return jsonify({
            'success': True,
            'cohort': cohort_name,
            'intern_count': len(filtered_interns) - 1,
            'chef_count': len(filtered_chefs) - 1,
            'results': results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

# Cloud Functions entry point (wraps Flask app)
def cloud_function_entry(request):
    """Entry point for Cloud Functions"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# For local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
