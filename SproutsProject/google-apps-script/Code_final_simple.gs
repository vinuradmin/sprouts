/**
 * Sprouts Matching Algorithm - Apps Script UI
 * The dialog calls the Cloud Function directly via client-side fetch()
 * (the CF has CORS enabled) instead of routing through google.script.run.
 * This avoids a known failure mode: google.script.run from an HtmlService
 * dialog depends on third-party cookies between the googleusercontent.com
 * iframe and script.google.com, which browsers with strict cross-site
 * tracking protection (e.g. Safari's default ITP) block outright, causing
 * "a server error occurred while reading from storage. PERMISSION_DENIED"
 * regardless of any Apps Script OAuth scope.
 */

const CLOUD_FUNCTION_URL = 'https://us-central1-sprouts-446222.cloudfunctions.net/sprouts-matching';
// Gates the Cloud Function against bare/scanned-URL callers (it's invoked via
// unauthenticated client-side fetch(), so this is the access check). Visible
// to anyone with edit access to this spreadsheet, same as the underlying data.
// NOTE: this repo file is a template — it does NOT hold the real secret.
// Set the actual value directly in the deployed Apps Script (via the
// script editor or `clasp push`), matching the SPROUTS_SHARED_SECRET
// environment variable on the Cloud Function. Never commit the real value.
const SPROUTS_SHARED_SECRET = 'REPLACE_WITH_REAL_SECRET_IN_DEPLOYED_SCRIPT_ONLY';

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
 * Shows dialog for selecting cohort and running matching.
 * The dialog talks to the Cloud Function directly (fetch), not via
 * google.script.run, so it works the same in every browser.
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
      .options-section { margin-bottom: 15px; }
      .options-title { font-weight: 500; margin-bottom: 8px; color: #444; font-size: 13px; }
      .checkbox-row { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; }
      .checkbox-row input[type="checkbox"] { width: 16px; height: 16px; margin-top: 2px; flex-shrink: 0; cursor: pointer; }
      .checkbox-row label { margin: 0; font-weight: 400; font-size: 13px; cursor: pointer; }
      .checkbox-row .hint { display: block; color: #888; font-size: 11px; margin-top: 2px; }
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

    <div class="options-section">
      <div class="options-title">Matching Options:</div>
      <div class="checkbox-row">
        <input type="checkbox" id="languageMatching" checked>
        <label for="languageMatching">
          Language matching
          <span class="hint">Prefer restaurants where spoken languages match the intern</span>
        </label>
      </div>
      <div class="checkbox-row">
        <input type="checkbox" id="respectPriorMatches" checked>
        <label for="respectPriorMatches">
          Respect prior matches
          <span class="hint">Keep interns already placed from a previous run</span>
        </label>
      </div>
    </div>

    <button id="runButton" onclick="runMatching()">Run Matching Algorithm</button>
    <div id="status" class="status"></div>
    <div class="info">Results will be written to a new tab: "{Season Year} Matches"</div>

    <script>
      function initializeForm() {
        var now = new Date();
        var currentYear = now.getFullYear();
        var currentMonth = now.getMonth();

        var yearSelect = document.getElementById('year');
        for (var year = 2024; year <= currentYear + 1; year++) {
          var option = document.createElement('option');
          option.value = year;
          option.textContent = year;
          if (year === currentYear) option.selected = true;
          yearSelect.appendChild(option);
        }

        var seasonSelect = document.getElementById('season');
        var defaultSeason, defaultYear = currentYear;
        if (currentMonth >= 0 && currentMonth <= 1)       { defaultSeason = 'Spring'; }
        else if (currentMonth >= 2 && currentMonth <= 4)  { defaultSeason = 'Summer'; }
        else if (currentMonth >= 5 && currentMonth <= 7)  { defaultSeason = 'Fall'; }
        else if (currentMonth >= 8 && currentMonth <= 10) { defaultSeason = 'Winter'; }
        else { defaultSeason = 'Spring'; defaultYear = currentYear + 1; }

        if (defaultSeason === 'Spring' && (currentMonth === 11 || currentMonth === 0 || currentMonth === 1)) {
          defaultYear = currentYear + 1;
        }
        seasonSelect.value = defaultSeason;
        yearSelect.value = defaultYear;
      }
      initializeForm();

      async function runMatching() {
        var season   = document.getElementById('season').value;
        var year     = document.getElementById('year').value;
        var cohort   = season + ' ' + year;
        var langMatch  = document.getElementById('languageMatching').checked;
        var priorMatch = document.getElementById('respectPriorMatches').checked;

        var button = document.getElementById('runButton');
        var status = document.getElementById('status');

        button.disabled = true;
        button.textContent = 'Running...';
        status.className = 'status status-running';
        status.innerHTML = '<span class="spinner"></span>Running matching for ' + cohort +
                           '...<br>This may take 1-2 minutes.';

        try {
          const response = await fetch('${CLOUD_FUNCTION_URL}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              cohort: cohort,
              enable_language_matching: langMatch,
              enable_respect_prior_matches: priorMatch,
              secret: '${SPROUTS_SHARED_SECRET}'
            })
          });
          const result = await response.json();

          if (!result.success) {
            throw new Error(result.error || ('Matching failed (HTTP ' + response.status + ')'));
          }

          status.className = 'status status-success';
          status.innerHTML = '<strong>Success!</strong><br>Matched ' + result.intern_count +
                             ' interns with ' + result.chef_count + ' chefs<br>' +
                             'Results in tab: <strong>' + result.tab_name + '</strong>';
        } catch (error) {
          status.className = 'status status-error';
          status.innerHTML = '<strong>Error:</strong><br>' + error.message;
        } finally {
          button.disabled = false;
          button.textContent = 'Run Matching Algorithm';
        }
      }
    </script>
  `).setWidth(450).setHeight(460);

  SpreadsheetApp.getUi().showModalDialog(html, 'Sprouts Matching Algorithm');
}
