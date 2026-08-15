# Deployment Checklist - Secure Cloud Function Deployment

## Pre-Deployment Security Check

### ✅ Files to NEVER Commit to Git

Check that these are in `.gitignore`:
- [ ] `service-account-key.json`
- [ ] `.env.yaml`
- [ ] `.env`
- [ ] Any files with API keys

### ✅ Verify .gitignore

```bash
cd cloud-function
cat .gitignore
```

Should contain:
```
service-account-key.json
*-key.json
*.json
!package.json
.env
.env.yaml
.env.local
```

### ✅ Check Git Status

```bash
git status
```

**Make sure these are NOT listed:**
- service-account-key.json
- .env.yaml

## Deployment Steps

### Step 1: Get Cloud Function Service Account

```bash
# Get your project ID
PROJECT_ID=$(gcloud config get-value project)

# This is your Cloud Function's service account
echo "${PROJECT_ID}@appspot.gserviceaccount.com"
```

**Copy this email!** You'll need it in Step 2.

### Step 2: Share Spreadsheet

1. Open: https://docs.google.com/spreadsheets/d/1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M
2. Click **Share**
3. Paste the service account email from Step 1
4. Set permission: **Viewer**
5. Uncheck "Notify people"
6. Click **Share**

### Step 3: Verify .env.yaml Exists

```bash
cd cloud-function
cat .env.yaml
```

Should show:
```yaml
GOOGLE_MAPS_API_KEY: "AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg"
```

### Step 4: Deploy

```bash
cd cloud-function

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

**Wait 2-3 minutes for deployment to complete.**

### Step 5: Get Cloud Function URL

After deployment, copy the URL from the output:
```
httpsTrigger:
  url: https://us-central1-PROJECT-ID.cloudfunctions.net/sprouts-matching
```

### Step 6: Test Deployed Function

```bash
# Test health endpoint
curl https://YOUR-FUNCTION-URL/health

# Test matching endpoint
curl -X POST https://YOUR-FUNCTION-URL/run-matching \
  -H "Content-Type: application/json" \
  -d '{"cohort":"Spring 2026"}'
```

### Step 7: Update Google Apps Script

1. Open your spreadsheet
2. Go to: **Extensions** > **Apps Script**
3. Find this line in `Code.gs`:
   ```javascript
   const CLOUD_FUNCTION_URL = 'YOUR_CLOUD_FUNCTION_URL_HERE';
   ```
4. Replace with your actual URL:
   ```javascript
   const CLOUD_FUNCTION_URL = 'https://us-central1-PROJECT-ID.cloudfunctions.net/sprouts-matching';
   ```
5. Save (Ctrl+S or Cmd+S)

### Step 8: Test End-to-End

1. Reload your spreadsheet
2. Click **🌱 Sprouts Matching** > **Run Matching Algorithm**
3. Select cohort: "Spring 2026"
4. Click **Run Matching Algorithm**
5. Wait 30-60 seconds
6. Verify new tab appears with results

## Security Verification

### ✅ What Should Be Deployed

Files deployed to Cloud Function:
- ✅ `main.py` (code)
- ✅ `requirements.txt` (dependencies)
- ✅ Environment variables (encrypted)

### ❌ What Should NOT Be Deployed

Files that stay local:
- ❌ `service-account-key.json` (stays on your machine)
- ❌ `.env.yaml` (not uploaded, only values used)
- ❌ Test files
- ❌ `.gitignore`

### ✅ Verify No Secrets in Code

```bash
# Check that API keys are not hardcoded
grep -r "AIzaSy" cloud-function/main.py
```

Should show:
```python
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', ...)
```

NOT:
```python
GOOGLE_MAPS_API_KEY = "AIzaSy..."  # ❌ WRONG
```

## Post-Deployment

### Monitor Function

```bash
# View logs
gcloud functions logs read sprouts-matching --limit 50

# View real-time logs
gcloud functions logs read sprouts-matching --limit 10 --follow
```

### Check Permissions

```bash
# Verify function service account
gcloud functions describe sprouts-matching --format="value(serviceAccountEmail)"
```

### Update Function (After Code Changes)

```bash
cd cloud-function

gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app
```

## Troubleshooting

### "Permission denied" Error

**Check:**
1. Spreadsheet is shared with Cloud Function service account
2. Service account has "Viewer" permission
3. Correct spreadsheet ID in `main.py`

**Fix:**
```bash
# Get service account
PROJECT_ID=$(gcloud config get-value project)
echo "Share with: ${PROJECT_ID}@appspot.gserviceaccount.com"
```

### "Invalid API key" Error

**Check:**
1. `.env.yaml` exists in `cloud-function/` directory
2. API key is correct
3. Google Maps API is enabled

**Fix:**
```bash
# Verify .env.yaml
cat cloud-function/.env.yaml

# Update if needed
echo 'GOOGLE_MAPS_API_KEY: "YOUR_KEY"' > cloud-function/.env.yaml

# Redeploy
gcloud functions deploy sprouts-matching --env-vars-file .env.yaml
```

### Function Times Out

**Increase timeout:**
```bash
gcloud functions deploy sprouts-matching --timeout 540s
```

## Security Best Practices

### Regular Maintenance

- [ ] Rotate Google Maps API key every 90 days
- [ ] Review Cloud Function logs monthly
- [ ] Check for unused service accounts
- [ ] Update dependencies quarterly

### Access Control

- [ ] Only share spreadsheet with necessary accounts
- [ ] Use "Viewer" permission (not "Editor")
- [ ] Review spreadsheet sharing settings monthly

### Monitoring

```bash
# Check who has access to spreadsheet
# (Do this manually in Google Sheets)

# View function invocations
gcloud functions logs read sprouts-matching \
  --format="value(timestamp,severity,textPayload)" \
  --limit 100
```

## Quick Reference

### Deployment Command

```bash
cd cloud-function && \
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

### Service Account Email

```bash
echo "$(gcloud config get-value project)@appspot.gserviceaccount.com"
```

### View Logs

```bash
gcloud functions logs read sprouts-matching --limit 50
```

### Delete Function

```bash
gcloud functions delete sprouts-matching
```

## Summary

**Secure Deployment Approach:**

1. ✅ Service account key stays local (never uploaded)
2. ✅ Cloud Function uses built-in service account
3. ✅ API key in environment variables (encrypted)
4. ✅ No secrets in source code
5. ✅ All secrets in `.gitignore`

**Result:** Your deployment is secure! 🔒

The service account key file never leaves your machine, and the Cloud Function uses Google's built-in authentication. API keys are passed as encrypted environment variables, not stored in code.
