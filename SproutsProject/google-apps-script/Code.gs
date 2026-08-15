/**
 * Google Apps Script for Sprouts Matching Algorithm
 * This code runs in the Google Spreadsheet and provides the UI
 */

// Configuration - UPDATE THIS after deploying Cloud Function
const CLOUD_FUNCTION_URL = 'YOUR_CLOUD_FUNCTION_URL_HERE';
const SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M';

/**
 * Creates custom menu when spreadsheet opens
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🌱 Sprouts Matching')
    .addItem('Run Matching Algorithm', 'showMatchingDialog')
    .addSeparator()
    .addItem('About', 'showAbout')
    .addToUi();
}

/**
 * Shows the matching dialog with cohort selection
 */
function showMatchingDialog() {
  var html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
      <head>
        <base target="_top">
        <style>
          body {
            font-family: 'Google Sans', Arial, sans-serif;
            padding: 20px;
            margin: 0;
          }
          h2 {
            color: #1a73e8;
            margin-top: 0;
          }
          .form-group {
            margin-bottom: 20px;
          }
          label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #5f6368;
          }
          select, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
          }
          select:focus, input:focus {
            outline: none;
            border-color: #1a73e8;
          }
          button {
            background: #1a73e8;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            width: 100%;
            margin-top: 10px;
          }
          button:hover {
            background: #1557b0;
          }
          button:disabled {
            background: #dadce0;
            cursor: not-allowed;
          }
          #status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 4px;
            display: none;
          }
          .status-running {
            background: #e8f0fe;
            color: #1967d2;
            border-left: 4px solid #1967d2;
          }
          .status-success {
            background: #e6f4ea;
            color: #137333;
            border-left: 4px solid #137333;
          }
          .status-error {
            background: #fce8e6;
            color: #c5221f;
            border-left: 4px solid #c5221f;
          }
          .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #1967d2;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        </style>
      </head>
      <body>
        <h2>Run Matching Algorithm</h2>
        
        <div class="form-group">
          <label for="cohort">Select Cohort:</label>
          <select id="cohort">
            <option value="Spring 2026">Spring 2026</option>
            <option value="Fall 2025">Fall 2025</option>
            <option value="Summer 2026">Summer 2026</option>
            <option value="Fall 2026">Fall 2026</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="tabName">Output Tab Name (optional):</label>
          <input type="text" id="tabName" placeholder="Leave blank to auto-generate">
        </div>
        
        <button id="runButton" onclick="runMatching()">Run Matching Algorithm</button>
        
        <div id="status"></div>
        
        <script>
          function runMatching() {
            var cohort = document.getElementById('cohort').value;
            var tabName = document.getElementById('tabName').value || cohort + ' Matches';
            var button = document.getElementById('runButton');
            var status = document.getElementById('status');
            
            // Disable button and show running status
            button.disabled = true;
            button.textContent = 'Running...';
            status.className = 'status-running';
            status.style.display = 'block';
            status.innerHTML = '<span class="spinner"></span>Running matching algorithm for ' + cohort + '...';
            
            // Call Apps Script function
            google.script.run
              .withSuccessHandler(function(result) {
                status.className = 'status-success';
                status.innerHTML = '✓ Success! Results written to tab: <strong>' + result.tabName + '</strong><br>' +
                                   'Matched ' + result.internCount + ' interns with restaurants.';
                button.disabled = false;
                button.textContent = 'Run Matching Algorithm';
              })
              .withFailureHandler(function(error) {
                status.className = 'status-error';
                status.innerHTML = '✗ Error: ' + error.message;
                button.disabled = false;
                button.textContent = 'Run Matching Algorithm';
              })
              .callMatchingAPI(cohort, tabName);
          }
        </script>
      </body>
    </html>
  `)
  .setWidth(450)
  .setHeight(400);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'Sprouts Matching Algorithm');
}

/**
 * Calls the Cloud Function and writes results to spreadsheet
 */
function callMatchingAPI(cohort, tabName) {
  try {
    // Call Cloud Function
    var url = CLOUD_FUNCTION_URL + '/run-matching';
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify({
        'cohort': cohort
      }),
      'muteHttpExceptions': true
    };
    
    Logger.log('Calling Cloud Function: ' + url);
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    Logger.log('Response code: ' + responseCode);
    
    if (responseCode !== 200) {
      throw new Error('Cloud Function returned error: ' + responseText);
    }
    
    var result = JSON.parse(responseText);
    
    if (!result.success) {
      throw new Error(result.error || 'Unknown error from Cloud Function');
    }
    
    Logger.log('Received results for ' + result.results.length + ' interns');
    
    // Write results to spreadsheet
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(tabName);
    
    // Create new sheet if it doesn't exist
    if (!sheet) {
      sheet = ss.insertSheet(tabName);
    } else {
      // Clear existing data
      sheet.clear();
    }
    
    // Format results for spreadsheet
    var data = formatResultsForSheet(result.results);
    
    // Write to sheet
    if (data.length > 0) {
      sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
      
      // Format header row
      var headerRange = sheet.getRange(1, 1, 1, data[0].length);
      headerRange.setFontWeight('bold');
      headerRange.setBackground('#1a73e8');
      headerRange.setFontColor('#ffffff');
      
      // Freeze header row
      sheet.setFrozenRows(1);
      
      // Auto-resize columns
      for (var i = 1; i <= data[0].length; i++) {
        sheet.autoResizeColumn(i);
      }
    }
    
    return {
      success: true,
      tabName: tabName,
      internCount: result.intern_count
    };
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    throw error;
  }
}

/**
 * Formats matching results for spreadsheet display
 */
function formatResultsForSheet(results) {
  var data = [];
  
  // Header row
  var header = ['Intern Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  data.push(header);
  
  // Process each intern
  for (var i = 0; i < results.length; i++) {
    var intern = results[i];
    var row = [intern.intern_name];
    
    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    for (var d = 0; d < days.length; d++) {
      var day = days[d];
      var matches = intern.matches_by_day[day] || [];
      
      // Format matches for this day
      var cellText = '';
      for (var m = 0; m < matches.length; m++) {
        var match = matches[m];
        cellText += match.restaurant + ' (' + match.commute_text + ')';
        if (m < matches.length - 1) {
          cellText += '\n';
        }
      }
      
      row.push(cellText);
    }
    
    data.push(row);
  }
  
  return data;
}

/**
 * Shows about dialog
 */
function showAbout() {
  var html = HtmlService.createHtmlOutput(`
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h2 style="color: #1a73e8;">Sprouts Matching Algorithm</h2>
      <p>This tool matches interns with restaurant opportunities based on:</p>
      <ul>
        <li>Schedule availability overlap (minimum 4 hours)</li>
        <li>Commute time via public transportation (maximum 50 minutes)</li>
        <li>Age restrictions (18+ requirements)</li>
      </ul>
      <p><strong>How to use:</strong></p>
      <ol>
        <li>Select a cohort (e.g., Spring 2026)</li>
        <li>Click "Run Matching Algorithm"</li>
        <li>Results will appear in a new tab</li>
      </ol>
      <p style="color: #5f6368; font-size: 12px; margin-top: 20px;">
        Powered by Google Cloud Functions
      </p>
    </div>
  `).setWidth(400).setHeight(350);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'About');
}
