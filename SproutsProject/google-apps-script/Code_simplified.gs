/**
 * Sprouts Matching Algorithm - Simplified Apps Script
 * Only triggers Cloud Function - no spreadsheet write permissions needed
 * Cloud Function handles all spreadsheet operations using service account
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
      label { display: block; margin-bottom: 5px; font-weight: 500; color: #5f6368; }
      select, button { width: 100%; padding: 12px; margin: 10px 0; font-size: 14px;
                       border: 1px solid #dadce0; border-radius: 4px; box-sizing: border-box; }
      select { background: white; cursor: pointer; }
      button { background: #1a73e8; color: white; border: none; cursor: pointer;
               font-weight: 500; transition: background 0.3s; }
      button:hover { background: #1557b0; }
      button:disabled { background: #dadce0; cursor: not-allowed; color: #80868b; }
      .status { padding: 12px; margin: 15px 0; border-radius: 4px; display: none;
                font-size: 14px; line-height: 1.5; }
      .status-running { background: #e8f0fe; color: #1967d2; display: block;
                        border-left: 4px solid #1967d2; }
      .status-success { background: #e6f4ea; color: #137333; display: block;
                        border-left: 4px solid #137333; }
      .status-error { background: #fce8e6; color: #c5221f; display: block;
                      border-left: 4px solid #c5221f; }
      .spinner { border: 2px solid #1967d2; border-top-color: transparent;
                 border-radius: 50%; width: 14px; height: 14px; display: inline-block;
                 animation: spin 1s linear infinite; vertical-align: middle; margin-right: 8px; }
      @keyframes spin { to { transform: rotate(360deg); } }
      .info { background: #f1f3f4; padding: 10px; border-radius: 4px;
              font-size: 12px; color: #5f6368; margin-top: 10px; }
    </style>
    
    <h3>Run Matching Algorithm</h3>
    <label for="cohort">Select Cohort:</label>
    <select id="cohort">
      <option value="Spring 2026">Spring 2026</option>
      <option value="Fall 2025">Fall 2025</option>
      <option value="Summer 2025">Summer 2025</option>
      <option value="Spring 2025">Spring 2025</option>
    </select>
    
    <button id="runButton" onclick="runMatching()">Run Matching Algorithm</button>
    <div id="status" class="status"></div>
    <div class="info">
      Results will be written to "{Cohort} Matches" tab by the Cloud Function.
      Existing tab will be overwritten with fresh results.
    </div>
    
    <script>
      function runMatching() {
        var cohort = document.getElementById('cohort').value;
        var button = document.getElementById('runButton');
        var status = document.getElementById('status');
        
        button.disabled = true;
        button.textContent = 'Running...';
        status.className = 'status status-running';
        status.innerHTML = '<span class="spinner"></span>Running matching for ' + cohort + '...<br>This may take 30-60 seconds.';
        
        google.script.run
          .withSuccessHandler(function(result) {
            status.className = 'status status-success';
            status.innerHTML = '✓ <strong>Success!</strong><br>Matched ' + result.intern_count + 
                               ' interns with ' + result.chef_count + ' chefs<br>Results in tab: <strong>' + 
                               result.tab_name + '</strong>';
            button.disabled = false;
            button.textContent = 'Run Matching Algorithm';
          })
          .withFailureHandler(function(error) {
            status.className = 'status status-error';
            status.innerHTML = '✗ <strong>Error:</strong><br>' + error.message;
            button.disabled = false;
            button.textContent = 'Run Matching Algorithm';
          })
          .callCloudFunction(cohort);
      }
    </script>
  `).setWidth(450).setHeight(400);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'Sprouts Matching Algorithm');
}

/**
 * Calls Cloud Function - that's it!
 * Cloud Function handles everything: reading, matching, and writing results
 */
function callCloudFunction(cohort) {
  try {
    var url = CLOUD_FUNCTION_URL;
    var payload = JSON.stringify({ cohort: cohort });
    var options = {
      method: 'post',
      contentType: 'application/json',
      payload: payload,
      muteHttpExceptions: true
    };
    
    var response = UrlFetchApp.fetch(url, options);
    var result = JSON.parse(response.getContentText());
    
    if (!result.success) {
      throw new Error(result.error || 'Matching failed');
    }
    
    return result;
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    throw error;
  }
}
