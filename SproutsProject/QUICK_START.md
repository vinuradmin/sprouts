# Quick Start Guide - Sprouts Matching Algorithm

## For Users (Running the Algorithm)

### Step 1: Open Your Spreadsheet
Open the Google Spreadsheet with Intern and Chef Availabilities

### Step 2: Run Matching
1. Click **🌱 Sprouts Matching** in the menu bar
2. Select **Run Matching Algorithm**
3. Choose your cohort (e.g., "Spring 2026")
4. Click **Run Matching Algorithm**
5. Wait 30-60 seconds

### Step 3: View Results
- A new tab will appear with the cohort name (e.g., "Spring 2026 Matches")
- Each row shows an intern's restaurant options
- Restaurants are sorted by commute time (shortest first)

## For Developers (Deployment)

### Prerequisites
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### Quick Deploy

```bash
# 1. Navigate to cloud-function directory
cd cloud-function

# 2. Make sure service-account-key.json is in this directory

# 3. Create .env.yaml with your API key
echo "GOOGLE_MAPS_API_KEY: 'YOUR_API_KEY'" > .env.yaml

# 4. Deploy
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app \
  --env-vars-file .env.yaml \
  --memory 512MB \
  --timeout 540s \
  --region us-central1

# 5. Copy the URL from output
# Example: https://us-central1-project.cloudfunctions.net/sprouts-matching
```

### Add to Spreadsheet

1. Open spreadsheet → **Extensions** → **Apps Script**
2. Copy code from `google-apps-script/Code.gs`
3. Update `CLOUD_FUNCTION_URL` with your URL
4. Save and reload spreadsheet

## Testing Locally

```bash
cd cloud-function
python test_local.py
```

## Key Features

✅ **Season/Year Filtering** - Automatically filters data by cohort
✅ **Public Transportation** - Always uses transit mode for commutes
✅ **4-Hour Minimum** - Requires at least 4 hours of overlap
✅ **50-Minute Max** - Filters restaurants over 50 minutes away
✅ **Age Restrictions** - Respects 18+ requirements
✅ **Sorted Results** - Restaurants sorted by commute time

## File Structure

```
cloud-function/
├── main.py                    # Cloud Function code
├── requirements.txt           # Python dependencies
├── service-account-key.json   # Google Sheets access (you create)
├── .env.yaml                  # Environment variables (you create)
└── test_local.py             # Local testing script

google-apps-script/
└── Code.gs                    # Apps Script code (paste in spreadsheet)
```

## Common Issues

### "Cloud Function URL not set"
- Update `CLOUD_FUNCTION_URL` in Apps Script Code.gs

### "Permission denied"
- Share spreadsheet with service account email
- Email is in service-account-key.json as `client_email`

### "No matches found"
- Check Season/Year column has correct cohort name
- Verify availability data is populated
- Ensure addresses are complete

## Support Commands

```bash
# View logs
gcloud functions logs read sprouts-matching --limit 50

# Test endpoint
curl -X POST YOUR_URL/run-matching \
  -H "Content-Type: application/json" \
  -d '{"cohort":"Spring 2026"}'

# Update function
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app
```

## What Changed from Original Python Script

### ✅ Updates Made:
1. **Always uses public transportation** - Changed from checking intern's transport preference
2. **Filters by Season/Year column** - Instead of delimiter rows
3. **In-memory processing** - No CSV files created
4. **Cloud-based** - Runs on Google Cloud Functions
5. **UI in spreadsheet** - Custom menu for easy access

### ✅ Preserved:
- Core matching algorithm logic (unchanged)
- 4-hour minimum overlap requirement
- 50-minute maximum commute
- Age restriction checking
- Commute time sorting
- All original calculation methods

---

**Ready to go!** Follow the deployment steps and you'll have the matching algorithm running from your spreadsheet in minutes.
