/**
 * Sprouts Matching Algorithm - Apps Script UI
 * Calls Cloud Function endpoint - no spreadsheet write permissions needed
 */

const CLOUD_FUNCTION_URL = 'https://us-central1-sprouts-446222.cloudfunctions.net/sprouts-matching';

/**
 * Creates custom menu when spreadsheet opens
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🌱 Sprouts Matching')
    .addItem('Run Matching Algorithm', 'showMatchingDialog')
    .addToUi();
}

/**
 * Shows dialog for selecting cohort and running matching
 */
function showMatchingDialog() {
  var html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }
      h3 { margin-top: 0; color: #1a73e8; }
      label { display: block; margin-bottom: 8px; font-weight: 500; }
      .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
      .form-group { display: flex; flex-direction: column; }
      select, button { width: 100%; padding: 12px; margin: 5px 0; font-size: 14px;
                       border: 1px solid #dadce0; border-radius: 4px; }
      button { background: #1a73e8; color: white; border: none; cursor: pointer; font-weight: 500; }
      button:hover { background: #1557b0; }
      button:disabled { background: #dadce0; cursor: not-allowed; }
      .status { padding: 12px; margin: 15px 0; border-radius: 4px; display: none; }
      .status-running { background: #e8f0fe; color: #1967d2; display: block; border-left: 4px solid #1967d2; }
      .status-success { background: #e6f4ea; color: #137333; display: block; border-left: 4px solid #137333; }
      .status-error { background: #fce8e6; color: #c5221f; display: block; border-left: 4px solid #c5221f; }
      .spinner { border: 2px solid #1967d2; border-top-color: transparent; border-radius: 50%;
                 width: 14px; height: 14px; display: inline-block; animation: spin 1s linear infinite;
                 vertical-align: middle; margin-right: 8px; }
      @keyframes spin { to { transform: rotate(360deg); } }
      .info { background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px; margin-top: 10px; }
    </style>
    
    <h3>Run Matching Algorithm</h3>
    
    <div class="form-row">
      <div class="form-group">
        <label for="season">Season:</label>
        <select id="season">
          <option value="Spring">Spring</option>
          <option value="Summer">Summer</option>
          <option value="Fall">Fall</option>
          <option value="Winter">Winter</option>
        </select>
      </div>
      <div class="form-group">
        <label for="year">Year:</label>
        <select id="year"></select>
      </div>
    </div>
    
    <button id="runButton" onclick="runMatching()">Run Matching Algorithm</button>
    <div id="status" class="status"></div>
    <div class="info">Results will be written to a new tab: "{Season Year} Matches"</div>
    
    <script>
      // Initialize form with smart defaults
      function initializeForm() {
        var now = new Date();
        var currentYear = now.getFullYear();
        var currentMonth = now.getMonth(); // 0-11
        
        // Populate year dropdown (2024 to next year)
        var yearSelect = document.getElementById('year');
        var startYear = 2024;
        var endYear = currentYear + 1;
        
        for (var year = startYear; year <= endYear; year++) {
          var option = document.createElement('option');
          option.value = year;
          option.textContent = year;
          if (year === currentYear) {
            option.selected = true;
          }
          yearSelect.appendChild(option);
        }
        
        // Set default season to upcoming season
        var seasonSelect = document.getElementById('season');
        var defaultSeason;
        var defaultYear = currentYear;
        
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
      
      function runMatching() {
        var season = document.getElementById('season').value;
        var year = document.getElementById('year').value;
        var cohort = season + ' ' + year;
        
        var button = document.getElementById('runButton');
        var status = document.getElementById('status');
        
        button.disabled = true;
        button.textContent = 'Running...';
        status.className = 'status status-running';
        status.innerHTML = '<span class="spinner"></span>Running matching for ' + cohort + 
                           '...<br>This may take 1-2 minutes.';
        
        google.script.run
          .withSuccessHandler(function(result) {
            status.className = 'status status-success';
            status.innerHTML = '<strong>Success!</strong><br>Matched ' + result.intern_count + 
                               ' interns with ' + result.chef_count + ' chefs<br>Results in tab: <strong>' + 
                               result.tab_name + '</strong>';
            button.disabled = false;
            button.textContent = 'Run Matching Algorithm';
          })
          .withFailureHandler(function(error) {
            status.className = 'status status-error';
            status.innerHTML = '<strong>Error:</strong><br>' + error.message;
            button.disabled = false;
            button.textContent = 'Run Matching Algorithm';
          })
          .callCloudFunction(cohort);
      }
    </script>
  `).setWidth(450).setHeight(380);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'Sprouts Matching Algorithm');
}

/**
 * Calls Cloud Function endpoint
 * Cloud Function handles everything: reading, matching, and writing results
 */
function callCloudFunction(cohort) {
  var url = CLOUD_FUNCTION_URL;
  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ cohort: cohort }),
    muteHttpExceptions: true
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var result = JSON.parse(response.getContentText());
  
  if (!result.success) {
    throw new Error(result.error || 'Matching failed');
  }
  
  return result;
}
