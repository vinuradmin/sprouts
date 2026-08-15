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
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # Read and write access

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

def get_html_form():
    """Return HTML form for web interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Sprouts Matching Algorithm</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               min-height: 100vh; display: flex; align-items: center; justify-content: center;
               padding: 20px; }
        .container { background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                     max-width: 500px; width: 100%; padding: 40px; }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 6px;
                 font-size: 16px; margin-bottom: 20px; background: white; cursor: pointer; }
        select:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 14px; background: #667eea; color: white; border: none;
                 border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer;
                 transition: background 0.3s; }
        button:hover { background: #5568d3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { margin-top: 20px; padding: 15px; border-radius: 6px; display: none; }
        .status.running { background: #e3f2fd; color: #1976d2; display: block; }
        .status.success { background: #e8f5e9; color: #388e3c; display: block; }
        .status.error { background: #ffebee; color: #c62828; display: block; }
        .spinner { border: 3px solid #1976d2; border-top-color: transparent; border-radius: 50%;
                   width: 20px; height: 20px; display: inline-block; animation: spin 1s linear infinite;
                   vertical-align: middle; margin-right: 10px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .info { background: #f5f5f5; padding: 15px; border-radius: 6px; margin-top: 20px;
                font-size: 13px; color: #666; }
        .link { color: #667eea; text-decoration: none; font-weight: 500; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Sprouts Matching</h1>
        <p class="subtitle">Match interns with restaurant opportunities</p>
        
        <form id="matchingForm">
            <label for="cohort">Select Cohort:</label>
            <select id="cohort" name="cohort">
                <option value="Spring 2026">Spring 2026</option>
                <option value="Fall 2025">Fall 2025</option>
                <option value="Summer 2025">Summer 2025</option>
                <option value="Spring 2025">Spring 2025</option>
                <option value="Fall 2024">Fall 2024</option>
            </select>
            
            <button type="submit" id="runButton">Run Matching Algorithm</button>
        </form>
        
        <div id="status" class="status"></div>
        
        <div class="info">
            Results will be written to a new tab in your 
            <a href="https://docs.google.com/spreadsheets/d/1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M" 
               target="_blank" class="link">Google Spreadsheet</a>.
            Tab name: "{Cohort} Matches"
        </div>
    </div>
    
    <script>
        document.getElementById('matchingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const cohort = document.getElementById('cohort').value;
            const button = document.getElementById('runButton');
            const status = document.getElementById('status');
            
            button.disabled = true;
            button.textContent = 'Running...';
            status.className = 'status running';
            status.innerHTML = '<span class="spinner"></span>Running matching for ' + cohort + 
                               '...<br>This may take 30-60 seconds.';
            
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cohort: cohort })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    status.className = 'status success';
                    status.innerHTML = '✓ <strong>Success!</strong><br>' +
                                     'Matched ' + result.intern_count + ' interns with ' + 
                                     result.chef_count + ' chefs<br>' +
                                     'Results written to tab: <strong>' + result.tab_name + '</strong><br>' +
                                     '<a href="https://docs.google.com/spreadsheets/d/1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M" ' +
                                     'target="_blank" class="link">View Spreadsheet →</a>';
                } else {
                    throw new Error(result.error || 'Matching failed');
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = '✗ <strong>Error:</strong><br>' + error.message;
            } finally {
                button.disabled = false;
                button.textContent = 'Run Matching Algorithm';
            }
        });
    </script>
</body>
</html>
'''

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

def write_results_to_sheet(cohort_name, results_data):
    """Write matching results to spreadsheet using service account"""
    try:
        service = get_sheets_service()
        
        # Tab name format: "Spring 2026 Matches"
        tab_name = f"{cohort_name} Matches"
        
        # Get spreadsheet
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        
        # Check if sheet exists
        sheet_id = None
        for sheet in sheets:
            if sheet['properties']['title'] == tab_name:
                sheet_id = sheet['properties']['sheetId']
                break
        
        # If sheet exists, clear it; otherwise create it
        if sheet_id is not None:
            # Clear existing sheet
            service.spreadsheets().values().clear(
                spreadsheetId=SPREADSHEET_ID,
                range=tab_name
            ).execute()
            print(f"Cleared existing sheet: {tab_name}")
        else:
            # Create new sheet
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': tab_name
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=request_body
            ).execute()
            print(f"Created new sheet: {tab_name}")
        
        # Prepare data
        data = [
            ['Cohort', 'Intern Count', 'Chef Count', 'Status', 'Timestamp'],
            [
                cohort_name,
                results_data.get('intern_count', 0),
                results_data.get('chef_count', 0),
                'Completed',
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            ]
        ]
        
        # Write data
        body = {'values': data}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{tab_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format header row
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id if sheet_id else 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
                            'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': requests}
        ).execute()
        
        print(f"Successfully wrote results to {tab_name}")
        return tab_name
        
    except Exception as e:
        print(f"Error writing to sheet: {e}")
        raise

def sprouts_matching(request):
    """
    Cloud Function entry point
    Handles web UI, health checks, and matching requests
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
    
    # Serve HTML form for GET requests
    if request.method == 'GET':
        html = get_html_form()
        return (html, 200, {'Content-Type': 'text/html'})
    
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
        
        # Prepare results
        results_data = {
            'success': True,
            'cohort': cohort_name,
            'intern_count': len(filtered_interns) - 1,
            'chef_count': len(filtered_chefs) - 1
        }
        
        # Write results to spreadsheet
        print("Writing results to spreadsheet...")
        tab_name = write_results_to_sheet(cohort_name, results_data)
        
        # Save cache
        print("Saving commute cache to GCS...")
        save_commute_cache()
        
        # Return response
        response_data = {
            'success': True,
            'cohort': cohort_name,
            'intern_count': results_data['intern_count'],
            'chef_count': results_data['chef_count'],
            'tab_name': tab_name,
            'message': 'Matching completed and results written to spreadsheet'
        }
        
        return (json.dumps(response_data), 200, headers)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            'success': False,
            'error': str(e)
        }
        return (json.dumps(error_response), 500, headers)
