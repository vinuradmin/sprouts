# Google Apps Script Integration Plan

## Objective
Port the Python matching algorithm to be invoked from Google Apps Script, allowing users to run the matching algorithm directly from the Google Spreadsheet with a simple UI.

## Updates Made to Python Script

### 1. ✅ Always Use Public Transportation
**File:** `C:/Users/pierr/OneDrive/Documents/commute.py`

**Change:** Modified `getCommuteTime()` to always use `'transit'` mode instead of checking transportation type.

```python
# Before:
googleMode = 'driving' if transportationType.startswith('Car') else 'transit'

# After:
googleMode = 'transit'  # Always use public transportation
```

### 2. ✅ Filter by Season/Year Column
**File:** `download_cohort_data.py`

**Change:** Instead of looking for delimiter rows like "Spring 2026", the script now:
- Finds the "Season/Year" column in both Intern and Chef Availabilities sheets
- Filters rows where the Season/Year column matches the requested cohort (e.g., "Spring 2026")

**Key Logic:**
```python
# Find Season/Year column
for j, cell in enumerate(row):
    if str(cell).strip() == "Season/Year":
        season_year_col = j
        
# Filter rows by cohort
for row in data:
    if str(row[season_year_col]).strip() == cohort_name:
        # Include this row
```

## Python Scripts Created

### 1. `download_cohort_data.py`
Downloads intern and chef data filtered by Season/Year column for a specific cohort.

**Usage:**
```bash
python download_cohort_data.py "Spring 2026"
```

### 2. `run_matching_for_cohort.py`
Complete end-to-end workflow:
1. Downloads data filtered by Season/Year
2. Maps data to format expected by original algorithm
3. Runs matching algorithm (using transit mode)
4. Saves results to CSV

**Usage:**
```bash
python run_matching_for_cohort.py "Spring 2026"
```

## Next Steps: Google Apps Script Integration

### Architecture Options

#### Option A: Hybrid (Python Backend + Apps Script UI) ⭐ RECOMMENDED
```
Google Sheet → Apps Script UI → Cloud Function (Python) → Update Google Sheet
```

**Pros:**
- Keep all Python code intact (no rewriting)
- No execution time limits
- Easy to maintain (one codebase)

**Implementation:**
1. Deploy Python script as Google Cloud Function
2. Create Apps Script UI in spreadsheet
3. Apps Script calls Cloud Function via HTTP
4. Cloud Function runs matching and returns results
5. Apps Script writes results to new tab

#### Option B: Pure JavaScript Port
```
Google Sheet → Apps Script (JavaScript) → Update Google Sheet
```

**Pros:**
- Fully integrated, no external dependencies
- No hosting costs

**Cons:**
- Must port all Python logic to JavaScript
- 6-minute execution limit
- Need to rewrite Slot, Chef, Intern, Commute classes in JS

### Recommended Implementation (Option A)

#### Step 1: Create Cloud Function
Deploy Python matching script as Google Cloud Function:

```python
# cloud_function.py
from flask import Flask, request, jsonify
from run_matching_for_cohort import run_matching_algorithm

app = Flask(__name__)

@app.route('/run-matching', methods=['POST'])
def run_matching():
    data = request.get_json()
    cohort_name = data.get('cohort')
    
    # Run matching algorithm
    result = run_matching_algorithm(cohort_name)
    
    return jsonify({
        'success': True,
        'cohort': cohort_name,
        'results': result
    })
```

#### Step 2: Create Apps Script UI

```javascript
// In Google Sheets: Extensions > Apps Script

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Sprouts Matching')
    .addItem('Run Matching Algorithm', 'showMatchingDialog')
    .addToUi();
}

function showMatchingDialog() {
  var html = HtmlService.createHtmlOutput(`
    <h2>Run Matching Algorithm</h2>
    <label>Select Cohort:</label>
    <select id="cohort">
      <option value="Spring 2026">Spring 2026</option>
      <option value="Fall 2025">Fall 2025</option>
      <option value="Summer 2026">Summer 2026</option>
    </select>
    <br><br>
    <button onclick="runMatching()">Run Matching</button>
    <div id="status"></div>
    
    <script>
      function runMatching() {
        var cohort = document.getElementById('cohort').value;
        document.getElementById('status').innerHTML = 'Running...';
        
        google.script.run
          .withSuccessHandler(onSuccess)
          .withFailureHandler(onFailure)
          .callMatchingAPI(cohort);
      }
      
      function onSuccess(result) {
        document.getElementById('status').innerHTML = 
          'Success! Results in tab: ' + result;
      }
      
      function onFailure(error) {
        document.getElementById('status').innerHTML = 
          'Error: ' + error;
      }
    </script>
  `).setWidth(400).setHeight(300);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'Sprouts Matching');
}

function callMatchingAPI(cohort) {
  var url = 'YOUR_CLOUD_FUNCTION_URL/run-matching';
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify({
      'cohort': cohort
    })
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var result = JSON.parse(response.getContentText());
  
  // Write results to new tab
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = cohort + ' Matches';
  
  // Create or get sheet
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }
  
  // Write results
  // ... (write result data to sheet)
  
  return sheetName;
}
```

## Core Algorithm Logic (DO NOT MODIFY)

The following logic from the original `matching_algo.py` must remain **EXACTLY THE SAME** when porting:

### Key Functions:
1. `readInternsAvailability()` - Read intern CSV and create Intern objects
2. `readChefsAvailability()` - Read chef CSV and create Chef objects
3. `findInternsToRestaurantOverlap()` - Find overlapping availability
4. `writeToCSVInternsToRestaurant()` - Write results to CSV

### Critical Logic to Preserve:
- Overlap calculation: `overlap.duration() >= 4`
- Commute filtering: `commute.value > 3000` (50 minutes)
- Age restriction check: `chefOver18Only and not intern.internOver18`
- Sorting: `sorted(overlaps.items(), key=lambda item: item[1]['commute'].value)`

**Any changes to this core logic require user approval!**

## Testing Checklist

- [ ] Test Season/Year filtering with "Spring 2026"
- [ ] Verify transit mode is always used for commute calculations
- [ ] Confirm results match previous output format
- [ ] Test with different cohorts (Fall 2025, Summer 2026)
- [ ] Verify Google Apps Script UI works
- [ ] Test end-to-end workflow from spreadsheet

## Files Modified

1. `C:/Users/pierr/OneDrive/Documents/commute.py` - Always use transit mode
2. `download_cohort_data.py` - Filter by Season/Year column
3. `run_matching_for_cohort.py` - Complete workflow script

## Next Action Required

**User needs to decide:**
1. Deploy as Cloud Function (Option A) - keeps Python code
2. Port to pure JavaScript (Option B) - fully integrated but requires rewrite

**Recommendation:** Option A (Cloud Function) because:
- No code rewriting needed
- Preserves exact algorithm logic
- No execution time limits
- Easier to maintain and update
