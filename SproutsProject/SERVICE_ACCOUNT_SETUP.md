# Service Account Setup Guide

This guide shows you how to create and configure a Google Cloud service account for the Sprouts Matching Algorithm.

## Why Service Account?

Service accounts are better than OAuth for server-to-server applications because:
- ✅ No user interaction needed
- ✅ More secure (no token refresh issues)
- ✅ Easier to manage permissions
- ✅ Works reliably in Cloud Functions

## Step-by-Step Setup

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **IAM & Admin** > **Service Accounts**
4. Click **+ CREATE SERVICE ACCOUNT**

### Step 2: Configure Service Account

**Service account details:**
- **Name:** `sprouts-matching`
- **ID:** `sprouts-matching` (auto-generated)
- **Description:** `Service account for Sprouts matching algorithm`

Click **CREATE AND CONTINUE**

**Grant permissions:**
- Skip this step (we'll use spreadsheet-level permissions)
- Click **CONTINUE**

**Grant users access:**
- Skip this step
- Click **DONE**

### Step 3: Create Service Account Key

1. Find your newly created service account in the list
2. Click on the service account email (e.g., `sprouts-matching@project-id.iam.gserviceaccount.com`)
3. Go to the **KEYS** tab
4. Click **ADD KEY** > **Create new key**
5. Select **JSON** format
6. Click **CREATE**
7. The JSON file will download automatically

### Step 4: Save the Key File

1. Rename the downloaded file to `service-account-key.json`
2. Move it to your `cloud-function/` directory:
   ```
   cloud-function/
   ├── main.py
   ├── requirements.txt
   └── service-account-key.json  ← Place here
   ```

**⚠️ IMPORTANT:** Never commit this file to git! It contains sensitive credentials.

### Step 5: Share Spreadsheet with Service Account

1. Open the downloaded `service-account-key.json` file
2. Find the `client_email` field (looks like: `sprouts-matching@project-id.iam.gserviceaccount.com`)
3. Copy this email address
4. Open your Google Spreadsheet
5. Click the **Share** button (top right)
6. Paste the service account email
7. Set permission to **Viewer**
8. **Uncheck** "Notify people"
9. Click **Share**

### Step 6: Verify Setup

The service account email should now appear in your spreadsheet's sharing settings.

## Testing Locally

Create a test script to verify the service account works:

```python
# test_service_account.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'

# Authenticate
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build service
service = build('sheets', 'v4', credentials=creds)

# Test read
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='Intern Availabilities!A1:B5'
).execute()

print(f"Successfully read {len(result.get('values', []))} rows")
print("Service account is working! ✓")
```

Run the test:
```bash
cd cloud-function
python test_service_account.py
```

Expected output:
```
Successfully read 5 rows
Service account is working! ✓
```

## Security Best Practices

### 1. Protect the Key File

Add to `.gitignore`:
```
service-account-key.json
*.json
!package.json
```

### 2. Limit Permissions

The service account only needs:
- **Spreadsheet access:** Viewer permission on specific spreadsheet
- **No project-level permissions needed**

### 3. Rotate Keys Regularly

Every 90 days:
1. Create a new key
2. Update the Cloud Function
3. Delete the old key

### 4. Monitor Usage

Check service account activity:
1. Go to **IAM & Admin** > **Service Accounts**
2. Click on your service account
3. View **Activity** tab

## Troubleshooting

### Error: "Permission denied"

**Solution:**
1. Verify service account email is in spreadsheet sharing
2. Check permission is at least "Viewer"
3. Try removing and re-adding the service account

### Error: "File not found: service-account-key.json"

**Solution:**
1. Verify file is in `cloud-function/` directory
2. Check filename is exactly `service-account-key.json`
3. Ensure file is valid JSON (open in text editor)

### Error: "Invalid grant"

**Solution:**
1. Download a fresh service account key
2. Delete old key from Google Cloud Console
3. Use the new key file

## What's Next?

After setting up the service account:
1. ✓ Service account created
2. ✓ Key file downloaded and saved
3. ✓ Spreadsheet shared with service account
4. ✓ Local testing successful

**You're ready to deploy!** Continue with the deployment guide.

## Quick Reference

**Service Account Email Format:**
```
sprouts-matching@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

**Key File Location:**
```
cloud-function/service-account-key.json
```

**Required Scopes:**
```python
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
```

**Spreadsheet Permission:**
- Viewer (read-only)
