"""
Google Cloud Function for Sprouts Matching Algorithm
Integrates existing matching algorithm with Google Sheets output
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
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Commute cache
commute_cache = {}

# ============================================================================
# SLOT CLASS (from Slot.py)
# ============================================================================

class Slot:
    start = 0
    end = 0

    def __init__(self, string="Unavailable"):
        self.fromString(string)

    def __str__(self):
        return str(self.start) + "-" + str(self.end)

    def __repr__(self):
        return str(self.start) + "-" + str(self.end)

    @staticmethod
    def to24(stringAmPm):
        if 'AM' in stringAmPm:
            return int(stringAmPm.replace('AM', ''))
        elif stringAmPm.strip() == '12PM':
            return 12
        else:
            return 12 + int(stringAmPm.replace('PM', ''))

    @staticmethod
    def combineSlots(daySlots):
        slots = []
        individualSlots = daySlots.split(',')
        prevSlot = Slot()
        for slot in individualSlots:
            newSlot = Slot(slot)
            if newSlot.isAllDay():
                slots.append(newSlot)
                break
            if (prevSlot.isAdjacent(newSlot)):
                prevSlot.addAndCombine(newSlot)
                continue
            if prevSlot.duration() < 4:
                prevSlot = newSlot
                continue
            slots.append(prevSlot)
            prevSlot = newSlot
        if prevSlot.duration() >= 4:
            slots.append(prevSlot)
        return slots

    def fromString(self, string):
        if string == 'All Day (9AM-9PM)':
            self.start = 9
            self.end = 21
        elif string == '' or string.strip() == 'Unavailable':
            return
        else:
            startEnd = string.split('-')
            self.start = Slot.to24(startEnd[0])
            self.end = Slot.to24(startEnd[1])

    def isAdjacent(self, other):
        return self.start == other.end or self.end == other.start

    def addAndCombine(self, other):
        if not self.isAdjacent(other):
            raise ValueError("can't combine slots that are not adjacent")
        elif self.start == other.end:
            self.start = other.start
        else:
            self.end = other.end

    def duration(self):
        return self.end - self.start

    def isAllDay(self):
        return self.start == 9 and self.end == 21

    def getOverlap(self, otherslot):
        overlap = Slot('')
        overlap.start = max(self.start, otherslot.start)
        overlap.end = min(self.end, otherslot.end)
        return overlap

# ============================================================================
# COMMUTE CLASS (from commute.py)
# ============================================================================

class Commute:
    def __init__(self, text, value):
        self.text = text
        self.value = value
    
    def to_dict(self):
        return {'text': self.text, 'value': self.value}
    
    @staticmethod
    def from_dict(d):
        return Commute(d['text'], d['value'])
    
    @staticmethod
    def getCommuteTime(transportationType, origin, destination):
        """Always use transit mode (public transportation)"""
        try:
            result = gmaps.distance_matrix(origin, destination, mode='transit')
            
            if result['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                if 'duration' in element:
                    return Commute(element['duration']['text'], element['duration']['value'])
        except Exception as e:
            print(f"Error calculating commute: {e}")
        
        return Commute('Error', 100000)
    
    def __str__(self):
        return str(self.text)
    
    def __repr__(self):
        return str(self.text)

# ============================================================================
# CHEF CLASS (from chef.py)
# ============================================================================

class Chef:
    timestamp = ''
    restaurantName = ''
    restaurantLocation = ''
    restaurantAddress = ''
    chefFullName = ''
    chefCell = ''
    chefEmail = ''
    chefOver18Only = True
    availability = {}

    def __init__(self, row={}):
        self.timestamp = row.get('Timestamp', '')
        self.restaurantName = row.get('Restaurant Name', '')
        self.restaurantLocation = row.get('Restaurant Location', '')
        self.restaurantAddress = row.get('Restaurant Address', '')
        self.chefFullName = row.get("Primary Mentor's Full Name (First and Last)", '')
        self.chefCell = row.get("Primary Mentor's Cell Phone Number", '')
        self.chefEmail = row.get("Primary Mentor's Email Address", '')
        self.chefOver18Only = False if row.get('Do interns need to be over 18 to work in your kitchen?', '') == 'No' else True
        print('Processing chef: ' + str(self))
        self.availability = self.getChefAvailability(row)

    def getChefAvailability(self, rowObject):
        avail = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_avail = rowObject.get(day, '')
            print(f"{day} - {day_avail}")
            avail[day] = Slot.combineSlots(day_avail)
        return avail

    def getFullAddress(self):
        return self.restaurantAddress + ', ' + self.restaurantLocation

    def __str__(self):
        return str(self.chefFullName) + " - from - " + str(self.restaurantName)

# ============================================================================
# INTERN CLASS (from intern.py)
# ============================================================================

class Intern:
    internFirstName = ''
    internLastName = ''
    internFullName = ''
    internPhone = ''
    internAddress = ''
    internCity = ''
    internZip = ''
    internOver18 = True
    internAge = 0
    internTransportation = ''
    internCommutePreference = ''
    availability = {}

    def __init__(self, row={}):
        self.internFirstName = row.get('First Name', '')
        self.internLastName = row.get('Last Name', '')
        self.internFullName = self.internFirstName + ' ' + self.internLastName
        self.internPhone = row.get('intern phone', '')
        self.internAddress = row.get('Street Address', '')
        self.internCity = row.get('City', '')
        self.internZip = row.get('Zip Code', '')
        self.internOver18 = True if row.get('Are you over 18 years old?', '') == 'Yes' else False
        self.internAge = row.get('Age', 0)
        self.internTransportation = row.get('What transportation will you use?', '')
        self.internCommutePreference = row.get('How long are you willing to commute to your internship?', '')
        print('Processing intern: ' + str(self))
        self.availability = self.getInternAvailability(row)

    def getInternAvailability(self, rowObject):
        avail = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_avail = rowObject.get(day, '')
            print(f"{day} - {day_avail}")
            avail[day] = Slot.combineSlots(day_avail)
        return avail

    def getFullAddress(self):
        return self.internAddress + ', ' + self.internCity + ', ' + self.internZip

    def __str__(self):
        return str(self.internFullName)

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

def rows_to_dict_list(rows):
    """Convert rows (with header) to list of dictionaries"""
    if not rows or len(rows) < 2:
        return []
    
    headers = rows[0]
    dict_list = []
    
    for row in rows[1:]:
        row_dict = {}
        for i, header in enumerate(headers):
            row_dict[header] = row[i] if i < len(row) else ''
        dict_list.append(row_dict)
    
    return dict_list

# ============================================================================
# MATCHING ALGORITHM (from matching_algo.py)
# ============================================================================

def findInternsToRestaurantOverlap(chefsAvail, intern, day, listOfInternsAvail):
    """Find restaurant matches for an intern on a specific day"""
    global commute_cache
    overlaps = {}
    
    for chefAvail in chefsAvail:
        chefDayAvail = chefsAvail[chefAvail].availability[day]
        for chefSlot in chefDayAvail:
            for internSlot in listOfInternsAvail:
                # Check age requirement
                if (chefsAvail[chefAvail].chefOver18Only and not intern.internOver18):
                    print(intern.internFullName + ' skipped ' + chefsAvail[chefAvail].restaurantName + " because of age")
                    continue
                
                # Calculate overlap
                overlap = chefSlot.getOverlap(internSlot)
                if (overlap.duration() >= 4):
                    # Get or calculate commute
                    com_key = intern.getFullAddress() + "|" + chefsAvail[chefAvail].getFullAddress()
                    
                    if com_key in commute_cache:
                        print("Commute found in cache")
                        commute = Commute.from_dict(commute_cache[com_key]) if isinstance(commute_cache[com_key], dict) else commute_cache[com_key]
                    else:
                        print("New call to Google API")
                        commute = Commute.getCommuteTime(intern.internTransportation, intern.getFullAddress(), chefsAvail[chefAvail].getFullAddress())
                        commute_cache[com_key] = commute.to_dict()
                    
                    # Skip if commute too long (180 minutes = 10800 seconds)
                    if (commute.value > 10800):
                        continue
                    
                    # Add to overlaps
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

def run_matching_algorithm(intern_rows, chef_rows):
    """Run the matching algorithm and return results"""
    
    # Convert rows to dictionaries
    intern_dicts = rows_to_dict_list(intern_rows)
    chef_dicts = rows_to_dict_list(chef_rows)
    
    # Create Intern and Chef objects
    interns = {}
    for row_dict in intern_dicts:
        try:
            intern = Intern(row_dict)
            interns[intern.internFullName] = intern
        except Exception as e:
            print(f"Error processing intern: {e}")
    
    chefs = {}
    for row_dict in chef_dicts:
        try:
            chef = Chef(row_dict)
            chefs[chef.restaurantName] = chef
        except Exception as e:
            print(f"Error processing chef: {e}")
    
    print(f"Loaded {len(chefs)} chefs/restaurants")
    print(f"Loaded {len(interns)} interns")
    
    # Run matching for each intern
    results = []
    
    for intern_name in interns:
        intern = interns[intern_name]
        days = intern.availability
        
        intern_result = {
            'intern_name': intern_name,
            'days': {}
        }
        
        for day in days:
            overlaps = findInternsToRestaurantOverlap(chefs, intern, day, days[day])
            
            day_matches = []
            for restaurant in overlaps:
                match_info = {
                    'restaurant': restaurant,
                    'commute': overlaps[restaurant]['commute'].text,
                    'time_slots': str(overlaps[restaurant][day])
                }
                day_matches.append(match_info)
            
            intern_result['days'][day] = day_matches
        
        results.append(intern_result)
    
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
        
        # Prepare data
        data = [['Intern Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
        
        for intern_result in results:
            row = [intern_result['intern_name']]
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                day_matches = intern_result['days'].get(day, [])
                
                cell_text = ""
                for match in day_matches:
                    cell_text += f"{match['restaurant']} ({match['commute']}): {match['time_slots']}\n"
                
                row.append(cell_text.strip())
            
            data.append(row)
        
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
        request_json = request.get_json(silent=True)
        cohort_name = request_json.get('cohort', 'Spring 2026') if request_json else 'Spring 2026'
        
        print(f"Running matching for cohort: {cohort_name}")
        
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
        results = run_matching_algorithm(filtered_interns, filtered_chefs)
        
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
