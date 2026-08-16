"""
Google Cloud Function for Sprouts Matching Algorithm
Integrates existing matching algorithm with Google Sheets output
"""

from google.oauth2 import service_account
from google.auth import default
from googleapiclient.discovery import build
from google.cloud import storage
import json
import os
import sys
from datetime import datetime

# Shares the same tested matching engine as the local CLI runner (language
# constraint, pre-matched interns, capacity cap, weekly recommendations,
# duplicate-row handling) instead of a second, drifted copy of the same
# logic living in this file.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_local import (
    filter_by_cohort,
    rows_to_dicts,
    run_matching as run_local_matching,
    build_result_row,
    RESULT_HEADER,
)

# Configuration
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
CACHE_BUCKET = os.environ.get('CACHE_BUCKET', 'sprouts-commute-cache')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Commute cache
commute_cache = {}

# ============================================================================
# CACHE FUNCTIONS
# ============================================================================

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

# ============================================================================
# GOOGLE SHEETS FUNCTIONS
# ============================================================================

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

# filter_by_cohort and rows_to_dicts are imported from run_local — same
# logic, one source of truth.

# ============================================================================
# MATCHING ALGORITHM
# ============================================================================

def run_matching_algorithm(intern_rows, chef_rows, enable_language_matching=True,
                            enable_respect_prior_matches=True):
    """Run the matching algorithm and return results.

    Delegates to run_local.run_matching — the same engine used by the local
    CLI runner, covering the language constraint, pre-matched interns,
    restaurant capacity cap, and weekly schedule recommendations.
    """
    global commute_cache

    intern_dicts = rows_to_dicts(intern_rows)
    chef_dicts = rows_to_dicts(chef_rows)

    results, cache_dirty = run_local_matching(
        intern_dicts, chef_dicts, commute_cache,
        enable_language_matching=enable_language_matching,
        enable_respect_prior_matches=enable_respect_prior_matches,
    )

    return results

def write_results_to_sheet(cohort_name, results):
    """Write matching results to spreadsheet"""
    try:
        service = get_sheets_service()
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
            service.spreadsheets().values().clear(
                spreadsheetId=SPREADSHEET_ID,
                range=tab_name
            ).execute()
            print(f"Cleared existing sheet: {tab_name}")
        else:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': tab_name
                        }
                    }
                }]
            }
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=request_body
            ).execute()
            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            print(f"Created new sheet: {tab_name}")
        
        # Prepare data — same row shape as the local CSV output, so the
        # production sheet and local iteration stay visually consistent.
        data = [RESULT_HEADER] + [build_result_row(r) for r in results]
        
        # Write data
        body = {'values': data}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{tab_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format header row
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
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
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': requests}
        ).execute()
        
        print(f"Successfully wrote {len(results)} intern results to {tab_name}")
        return tab_name
        
    except Exception as e:
        print(f"Error writing to sheet: {e}")
        raise

# ============================================================================
# HTML FORM
# ============================================================================

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
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 6px;
                 font-size: 16px; background: white; cursor: pointer; }
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
        .checkbox-group { margin-bottom: 20px; }
        .checkbox-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 12px; }
        .checkbox-row input[type="checkbox"] { width: 18px; height: 18px; margin-top: 2px; cursor: pointer; flex-shrink: 0; }
        .checkbox-row label { margin-bottom: 0; font-weight: 500; cursor: pointer; }
        .checkbox-row .hint { display: block; font-weight: 400; color: #888; font-size: 12px; margin-top: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Sprouts Matching</h1>
        <p class="subtitle">Match interns with restaurant opportunities</p>
        
        <form id="matchingForm">
            <div class="form-row">
                <div class="form-group">
                    <label for="season">Season:</label>
                    <select id="season" name="season">
                        <option value="Spring">Spring</option>
                        <option value="Summer">Summer</option>
                        <option value="Fall">Fall</option>
                        <option value="Winter">Winter</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="year">Year:</label>
                    <select id="year" name="year"></select>
                </div>
            </div>

            <div class="checkbox-group">
                <div class="checkbox-row">
                    <input type="checkbox" id="languageMatching" name="languageMatching" checked>
                    <label for="languageMatching">Language matching
                        <span class="hint">Spanish-only kitchens are only offered to Spanish-speaking interns</span>
                    </label>
                </div>
                <div class="checkbox-row">
                    <input type="checkbox" id="respectPriorMatches" name="respectPriorMatches" checked>
                    <label for="respectPriorMatches">Respect Prior Matches
                        <span class="hint">Interns already placed at a restaurant are kept fixed, not re-matched</span>
                    </label>
                </div>
            </div>

            <button type="submit" id="runButton">Run Matching Algorithm</button>
        </form>
        
        <div id="status" class="status"></div>
        
        <div class="info">
            Results will be written to a new tab in your 
            <a href="https://docs.google.com/spreadsheets/d/1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M" 
               target="_blank" class="link">Google Spreadsheet</a>.
            Tab name: "{Season Year} Matches"
        </div>
    </div>
    
    <script>
        // Initialize form with smart defaults
        function initializeForm() {
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth(); // 0-11
            
            // Populate year dropdown (2024 to next year)
            const yearSelect = document.getElementById('year');
            const startYear = 2024;
            const endYear = currentYear + 1;
            
            for (let year = startYear; year <= endYear; year++) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === currentYear) {
                    option.selected = true;
                }
                yearSelect.appendChild(option);
            }
            
            // Set default season to upcoming season
            const seasonSelect = document.getElementById('season');
            let defaultSeason;
            let defaultYear = currentYear;
            
            // Determine upcoming season based on current month
            if (currentMonth >= 0 && currentMonth <= 1) {
                defaultSeason = 'Spring'; // Jan-Feb -> Spring (current year)
            } else if (currentMonth >= 2 && currentMonth <= 4) {
                defaultSeason = 'Summer'; // Mar-May -> Summer
            } else if (currentMonth >= 5 && currentMonth <= 7) {
                defaultSeason = 'Fall'; // Jun-Aug -> Fall
            } else if (currentMonth >= 8 && currentMonth <= 10) {
                defaultSeason = 'Winter'; // Sep-Nov -> Winter
            } else {
                defaultSeason = 'Spring'; // Dec -> Spring (next year)
                defaultYear = currentYear + 1;
            }
            
            // If upcoming season is Spring (Jan-Feb or Dec), use next year
            if (defaultSeason === 'Spring' && (currentMonth === 11 || currentMonth === 0 || currentMonth === 1)) {
                defaultYear = currentYear + 1;
            }
            
            seasonSelect.value = defaultSeason;
            yearSelect.value = defaultYear;
        }
        
        // Initialize on page load
        initializeForm();
        
        // Handle form submission
        document.getElementById('matchingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const season = document.getElementById('season').value;
            const year = document.getElementById('year').value;
            const cohort = season + ' ' + year;
            const languageMatching = document.getElementById('languageMatching').checked;
            const respectPriorMatches = document.getElementById('respectPriorMatches').checked;

            const button = document.getElementById('runButton');
            const status = document.getElementById('status');

            button.disabled = true;
            button.textContent = 'Running...';
            status.className = 'status running';
            status.innerHTML = '<span class="spinner"></span>Running matching for ' + cohort +
                               '...<br>This may take 1-2 minutes.';

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        cohort: cohort,
                        enable_language_matching: languageMatching,
                        enable_respect_prior_matches: respectPriorMatches
                    })
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

# ============================================================================
# CLOUD FUNCTION ENTRY POINT
# ============================================================================

def sprouts_matching(request):
    """Cloud Function entry point"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    # Health check
    if request.path == '/health' or request.path.endswith('/health'):
        return (json.dumps({'status': 'healthy'}), 200, headers)
    
    # Serve HTML form for GET requests
    if request.method == 'GET':
        html = get_html_form()
        return (html, 200, {'Content-Type': 'text/html'})
    
    # Matching endpoint (POST)
    try:
        request_json = request.get_json(silent=True) or {}
        cohort_name = request_json.get('cohort', 'Spring 2026')
        enable_language_matching = request_json.get('enable_language_matching', True)
        enable_respect_prior_matches = request_json.get('enable_respect_prior_matches', True)

        print(f"Running matching for cohort: {cohort_name}")
        print(f"  Language matching: {'ON' if enable_language_matching else 'OFF'}")
        print(f"  Respect prior matches: {'ON' if enable_respect_prior_matches else 'OFF'}")

        # Load cache
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
        results = run_matching_algorithm(
            filtered_interns, filtered_chefs,
            enable_language_matching=enable_language_matching,
            enable_respect_prior_matches=enable_respect_prior_matches,
        )

        # Write results to spreadsheet
        print("Writing results to spreadsheet...")
        tab_name = write_results_to_sheet(cohort_name, results)

        # Save cache
        print("Saving commute cache to GCS...")
        save_commute_cache()

        # Return response
        response_data = {
            'success': True,
            'cohort': cohort_name,
            'intern_count': len(filtered_interns) - 1,
            'chef_count': len(filtered_chefs) - 1,
            'tab_name': tab_name,
            'enable_language_matching': enable_language_matching,
            'enable_respect_prior_matches': enable_respect_prior_matches,
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
