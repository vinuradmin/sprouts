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

# Shared secret the caller (Apps Script dialog) must present. The function is
# invoked unauthenticated (allUsers) because the dialog calls it via
# client-side fetch() with no way to attach IAM credentials, so this is the
# only gate against random internet callers burning Maps API quota.
SHARED_SECRET = os.environ.get('SPROUTS_SHARED_SECRET')

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

def _build_format_requests(sheet_id, results):
    """Return batchUpdate requests for rich sheet formatting."""
    num_rows = len(results) + 1  # +1 for header
    requests = []

    # Freeze header row
    requests.append({
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {'frozenRowCount': 1}
            },
            'fields': 'gridProperties.frozenRowCount'
        }
    })

    # Wrap text + align top for all cells
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': num_rows},
            'cell': {
                'userEnteredFormat': {
                    'wrapStrategy': 'WRAP',
                    'verticalAlignment': 'TOP'
                }
            },
            'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)'
        }
    })

    # Header: blue background, white bold text, center-aligned
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
                    'textFormat': {
                        'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                        'bold': True,
                        'fontSize': 10
                    },
                    'horizontalAlignment': 'CENTER'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
        }
    })

    # Row shading: light green for pre-matched, alternating white/light-gray for others
    WHITE = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    LIGHT_GRAY = {'red': 0.95, 'green': 0.96, 'blue': 0.98}
    LIGHT_GREEN = {'red': 0.88, 'green': 0.96, 'blue': 0.88}
    alt_idx = 0
    for i, r in enumerate(results):
        row_idx = i + 1
        is_pre_matched = any(
            'Already matched' in rec
            for rec in r.get('weekly_recommendations', [])
        )
        if is_pre_matched:
            bg = LIGHT_GREEN
        else:
            bg = WHITE if alt_idx % 2 == 0 else LIGHT_GRAY
            alt_idx += 1
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': row_idx,
                    'endRowIndex': row_idx + 1
                },
                'cell': {'userEnteredFormat': {'backgroundColor': bg}},
                'fields': 'userEnteredFormat.backgroundColor'
            }
        })

    # Column widths: Name, Top3, Mon–Sun, Notes
    col_widths = [180, 340, 210, 210, 210, 210, 210, 210, 210, 200]
    for i, width in enumerate(col_widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': i,
                    'endIndex': i + 1
                },
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })

    return requests


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
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': _build_format_requests(sheet_id, results)}
        ).execute()
        
        print(f"Successfully wrote {len(results)} intern results to {tab_name}")
        return tab_name
        
    except Exception as e:
        print(f"Error writing to sheet: {e}")
        raise

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
    
    # The standalone GET form has been disabled: it had no access gate at all
    # (unlike the Apps Script dialog, which requires spreadsheet access), so
    # it was the one truly public, zero-barrier way to trigger paid API calls.
    if request.method == 'GET':
        return (
            json.dumps({'status': 'ok', 'message': 'Use the 🌱 Sprouts Matching menu in the spreadsheet.'}),
            200, headers
        )

    # Matching endpoint (POST) — requires the shared secret the Apps Script
    # dialog sends, so bare/scanned URLs can't trigger a run.
    try:
        request_json = request.get_json(silent=True) or {}

        if not SHARED_SECRET or request_json.get('secret') != SHARED_SECRET:
            return (json.dumps({'success': False, 'error': 'Unauthorized'}), 403, headers)

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
