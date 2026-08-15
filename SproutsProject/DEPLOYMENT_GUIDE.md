# Sprouts Matching Algorithm - Deployment Guide

## Overview

This guide will help you deploy the Sprouts Matching Algorithm as a Google Cloud Function with a Google Apps Script UI in your spreadsheet.

## Architecture

```
Google Spreadsheet (UI)
    ↓
Google Apps Script (Menu & Dialog)
    ↓
Google Cloud Function (Python Matching Algorithm)
    ↓
Google Sheets API (Read Data)
    ↓
Google Maps API (Calculate Commutes)
    ↓
Return Results to Spreadsheet
```

## Prerequisites

1. Google Cloud Platform account
2. Google Cloud SDK (gcloud CLI) installed
3. Google Maps API key
4. Google Sheets with Intern and Chef Availabilities

## Part 1: Set Up Google Cloud Project

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID

### Step 2: Enable Required APIs

Enable these APIs in your project:
- Google Sheets API
- Cloud Functions API
- Cloud Build API

```bash
gcloud services enable sheets.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Create Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name: `sprouts-matching-sa`
4. Grant role: "Editor" (or minimum: Sheets API access)
5. Click "Create Key" → JSON
6. Download the JSON file
7. Rename it to `service-account-key.json`
8. Place it in the `cloud-function/` directory

### Step 4: Share Spreadsheet with Service Account

1. Open the downloaded `service-account-key.json`
2. Copy the `client_email` value (looks like: `sprouts-matching-sa@project-id.iam.gserviceaccount.com`)
3. Open your Google Spreadsheet
4. Click "Share"
5. Add the service account email with "Viewer" access
6. Click "Send"

## Part 2: Deploy Cloud Function

### Step 1: Prepare Files

Navigate to the cloud-function directory:
```bash
cd cloud-function
```

Make sure you have these files:
- `main.py` ✓
- `requirements.txt` ✓
- `service-account-key.json` ✓ (you created this)
- `.gcloudignore` ✓

### Step 2: Set Environment Variables

Create a `.env.yaml` file:
```yaml
GOOGLE_MAPS_API_KEY: "AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg"
```

### Step 3: Deploy to Google Cloud

```bash
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app \
  --env-vars-file .env.yaml \
  --memory 512MB \
  --timeout 540s \
  --region us-central1
```

**Note:** Deployment takes 2-3 minutes.

### Step 4: Get Cloud Function URL

After deployment completes, you'll see output like:
```
httpsTrigger:
  url: https://us-central1-YOUR-PROJECT.cloudfunctions.net/sprouts-matching
```

**Copy this URL!** You'll need it for the Apps Script.

### Step 5: Test Cloud Function

Test the health endpoint:
```bash
curl https://YOUR-CLOUD-FUNCTION-URL/health
```

Should return: `{"status":"healthy"}`

Test the matching endpoint:
```bash
curl -X POST https://YOUR-CLOUD-FUNCTION-URL/run-matching \
  -H "Content-Type: application/json" \
  -d '{"cohort":"Spring 2026"}'
```

## Part 3: Set Up Google Apps Script

### Step 1: Open Apps Script Editor

1. Open your Google Spreadsheet
2. Go to: **Extensions** > **Apps Script**
3. Delete any existing code in `Code.gs`

### Step 2: Add the Code

1. Copy the contents of `google-apps-script/Code.gs`
2. Paste into the Apps Script editor

### Step 3: Update Configuration

Find this line near the top:
```javascript
const CLOUD_FUNCTION_URL = 'YOUR_CLOUD_FUNCTION_URL_HERE';
```

Replace with your actual Cloud Function URL (from Part 2, Step 4):
```javascript
const CLOUD_FUNCTION_URL = 'https://us-central1-YOUR-PROJECT.cloudfunctions.net/sprouts-matching';
```

### Step 4: Save and Deploy

1. Click the disk icon or **File** > **Save**
2. Name your project: "Sprouts Matching"
3. Click **Run** > **Run function** > **onOpen**
4. Authorize the script when prompted:
   - Click "Review Permissions"
   - Choose your Google account
   - Click "Advanced" > "Go to Sprouts Matching (unsafe)"
   - Click "Allow"

### Step 5: Reload Spreadsheet

1. Close and reopen your Google Spreadsheet
2. You should see a new menu: **🌱 Sprouts Matching**

## Part 4: Test the Integration

### Test Run

1. Click **🌱 Sprouts Matching** > **Run Matching Algorithm**
2. Select cohort: "Spring 2026"
3. Click "Run Matching Algorithm"
4. Wait for completion (30-60 seconds)
5. Check for new tab: "Spring 2026 Matches"

### Expected Output

The new tab should contain:
- Header row: Intern Name, Monday, Tuesday, ..., Sunday
- One row per intern
- Each cell shows restaurant matches sorted by commute time
- Format: `Restaurant Name (commute time)`

## Troubleshooting

### Error: "Cloud Function returned error"

**Check:**
1. Cloud Function URL is correct in Apps Script
2. Service account has access to spreadsheet
3. Cloud Function logs: `gcloud functions logs read sprouts-matching`

### Error: "Permission denied"

**Fix:**
1. Verify service account email is shared with spreadsheet
2. Check service account has "Viewer" access
3. Re-share spreadsheet if needed

### Error: "Season/Year column not found"

**Fix:**
1. Verify both sheets have "Season/Year" column
2. Check column header spelling exactly matches
3. Ensure data rows have values in Season/Year column

### No matches found

**Check:**
1. Season/Year column has correct cohort name (e.g., "Spring 2026")
2. Intern and chef availability columns are populated
3. Addresses are valid (Street Address, City, Zip Code)
4. At least 4 hours of overlap exists

### Slow performance

**Optimize:**
1. Increase Cloud Function memory: `--memory 1024MB`
2. Check commute cache is working (logs should show "Commute found in cache")
3. Consider increasing timeout: `--timeout 540s`

## Updating the Algorithm

### Update Cloud Function

1. Edit `cloud-function/main.py`
2. Redeploy:
```bash
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app \
  --env-vars-file .env.yaml
```

### Update Apps Script

1. Open **Extensions** > **Apps Script**
2. Edit `Code.gs`
3. Save (no redeployment needed)
4. Reload spreadsheet

## Monitoring

### View Logs

```bash
# Cloud Function logs
gcloud functions logs read sprouts-matching --limit 50

# Real-time logs
gcloud functions logs read sprouts-matching --limit 10 --follow
```

### Check Metrics

1. Go to [Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Functions**
3. Click on `sprouts-matching`
4. View metrics: invocations, execution time, errors

## Cost Estimate

### Google Cloud Functions
- **Free tier:** 2M invocations/month
- **Your usage:** ~10-20 runs/month
- **Cost:** $0/month (well within free tier)

### Google Maps API
- **Free tier:** $200 credit/month (~40,000 requests)
- **Your usage:** ~50-100 requests per run
- **Cost:** $0/month (within free tier)

**Total estimated cost: $0/month**

## Security Notes

1. **Service Account Key:** Keep `service-account-key.json` secure, never commit to git
2. **API Keys:** Store in environment variables, not in code
3. **Cloud Function:** Set `--allow-unauthenticated` only if needed, consider authentication
4. **Spreadsheet:** Only share with necessary users

## Support

### Common Commands

```bash
# View function details
gcloud functions describe sprouts-matching

# Delete function
gcloud functions delete sprouts-matching

# Update environment variables
gcloud functions deploy sprouts-matching --update-env-vars GOOGLE_MAPS_API_KEY=new_key

# View service account
gcloud iam service-accounts list
```

### Getting Help

1. Check Cloud Function logs first
2. Test endpoints with curl
3. Verify Apps Script permissions
4. Check spreadsheet sharing settings

## Next Steps

After successful deployment:
1. ✓ Test with different cohorts
2. ✓ Verify results accuracy
3. ✓ Train users on the UI
4. ✓ Set up monitoring alerts (optional)
5. ✓ Document any custom modifications

---

**Deployment Complete!** 🎉

Your matching algorithm is now accessible directly from the Google Spreadsheet with a simple menu click.
