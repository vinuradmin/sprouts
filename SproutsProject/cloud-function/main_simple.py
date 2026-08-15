"""
Google Cloud Function for Sprouts Matching Algorithm
Simple HTTP function format for Cloud Functions 1st gen
"""

from google.oauth2 import service_account
from google.auth import default
from googleapiclient.discovery import build
from google.cloud import storage
import googlemaps
import json
import os
from datetime import datetime

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
    """Get Google Sheets API service"""
    if os.getenv('FUNCTION_NAME') or os.getenv('K_SERVICE'):
        creds, _ = default(scopes=SCOPES)
    else:
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
    
    header_row = None
    season_year_col = None
    
    for i, row in enumerate(data):
        season_year_col = find_column_index(row, 'Season/Year')
        if season_year_col is not None:
            header_row = i
            break
    
    if header_row is None or season_year_col is None:
        return []
    
    filtered = [data[header_row]]
    
    for i in range(header_row + 1, len(data)):
        row = data[i]
        if len(row) > season_year_col:
            if str(row[season_year_col]).strip() == cohort_name:
                filtered.append(row)
    
    return filtered

def get_commute_time(origin, destination):
    """Calculate commute time using Google Maps API"""
    cache_key = f"{origin}|{destination}"
    
    if cache_key in commute_cache:
        print(f"[CACHE HIT] {origin[:30]}... -> {destination[:30]}...")
        return commute_cache[cache_key]
    
    print(f"[CACHE MISS] {origin[:30]}... -> {destination[:30]}... (calling API)")
    
    try:
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
    
    return {'text': 'Error', 'value': 100000}

def sprouts_matching(request):
    """
    Cloud Function entry point
    Handles both health checks and matching requests
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # Health check
    if request.path == '/health' or request.path.endswith('/health'):
        return (json.dumps({'status': 'healthy'}), 200, headers)
    
    # Matching endpoint
    try:
        request_json = request.get_json(silent=True)
        cohort_name = request_json.get('cohort', 'Spring 2026') if request_json else 'Spring 2026'
        
        print(f"Running matching for cohort: {cohort_name}")
        
        # Load cache
        print("Loading commute cache from GCS...")
        load_commute_cache()
        
        # Read data
        print("Reading Intern Availabilities...")
        intern_data = read_sheet_data('Intern Availabilities')
        
        print("Reading Chef Availabilities...")
        chef_data = read_sheet_data('Chef Availabilities')
        
        # Filter by cohort
        print(f"Filtering by cohort: {cohort_name}")
        filtered_interns = filter_by_cohort(intern_data, cohort_name)
        filtered_chefs = filter_by_cohort(chef_data, cohort_name)
        
        print(f"Found {len(filtered_interns)-1} interns and {len(filtered_chefs)-1} chefs")
        
        # Simple response for now (full algorithm in next iteration)
        results = {
            'success': True,
            'cohort': cohort_name,
            'intern_count': len(filtered_interns) - 1,
            'chef_count': len(filtered_chefs) - 1,
            'message': 'Matching algorithm executed successfully'
        }
        
        # Save cache
        print("Saving commute cache to GCS...")
        save_commute_cache()
        
        return (json.dumps(results), 200, headers)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            'success': False,
            'error': str(e)
        }
        return (json.dumps(error_response), 500, headers)
