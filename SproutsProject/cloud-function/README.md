# Cloud Function - Sprouts Matching Algorithm

This directory contains the Google Cloud Function implementation of the Sprouts matching algorithm.

## Quick Start

### 1. Set Up Service Account

```bash
# Run the setup wizard
python ../setup_service_account.py
```

Or manually:
1. Create service account in Google Cloud Console
2. Download JSON key as `service-account-key.json`
3. Place in this directory
4. Share spreadsheet with service account email

### 2. Test Locally

```bash
# Test service account authentication
python test_service_account.py

# Test the full matching algorithm locally
python test_local.py
```

### 3. Deploy to Google Cloud

```bash
# Create environment file
echo "GOOGLE_MAPS_API_KEY: 'YOUR_API_KEY'" > .env.yaml

# Deploy
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

## Files

- **`main.py`** - Cloud Function code (matching algorithm)
- **`requirements.txt`** - Python dependencies
- **`service-account-key.json`** - Service account credentials (you create this)
- **`.env.yaml`** - Environment variables (you create this)
- **`test_service_account.py`** - Test service account setup
- **`test_local.py`** - Test matching algorithm locally
- **`.gitignore`** - Prevents committing sensitive files

## Environment Variables

Create `.env.yaml`:
```yaml
GOOGLE_MAPS_API_KEY: "your_api_key_here"
```

## Testing

### Test Service Account
```bash
python test_service_account.py
```

Expected output:
```
✓ Service account credentials loaded
✓ Google Sheets API service created
✓ Successfully read 5 rows from spreadsheet
✓ Found 'Season/Year' column at index 0
  Cohorts found:
    - Spring 2026: 34 rows
    - Fall 2025: 28 rows
```

### Test Matching Algorithm
```bash
python test_local.py
```

This will:
1. Read data from Google Sheets
2. Filter by cohort
3. Run matching algorithm
4. Display results

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{"status": "healthy"}
```

### Run Matching
```bash
POST /run-matching
Content-Type: application/json

{
  "cohort": "Spring 2026"
}
```

Response:
```json
{
  "success": true,
  "cohort": "Spring 2026",
  "intern_count": 34,
  "chef_count": 42,
  "results": [...]
}
```

## Deployment

### First Time Deploy
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

### Update Existing Function
```bash
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app
```

### View Logs
```bash
gcloud functions logs read sprouts-matching --limit 50
```

### Delete Function
```bash
gcloud functions delete sprouts-matching
```

## Troubleshooting

### "Permission denied" error
- Verify spreadsheet is shared with service account email
- Check service account has at least "Viewer" permission
- Service account email is in `service-account-key.json` as `client_email`

### "File not found: service-account-key.json"
- Download service account key from Google Cloud Console
- Save as `service-account-key.json` in this directory
- Verify filename is exactly correct (case-sensitive)

### "Invalid grant" error
- Service account key may be expired or revoked
- Download a fresh key from Google Cloud Console
- Delete old keys from Google Cloud Console

### "Season/Year column not found"
- Verify both sheets have "Season/Year" column header
- Check spelling and capitalization exactly match
- Ensure column header is in the first row

## Security

**NEVER commit these files:**
- `service-account-key.json`
- `.env.yaml`
- Any files containing API keys

These are protected by `.gitignore`.

## Local Development

Run the Cloud Function locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

The function will be available at `http://localhost:8080`

Test with curl:
```bash
curl -X POST http://localhost:8080/run-matching \
  -H "Content-Type: application/json" \
  -d '{"cohort":"Spring 2026"}'
```

## Algorithm Details

The matching algorithm:
1. Reads data from Google Sheets via API
2. Filters by Season/Year column
3. Calculates schedule overlaps (minimum 4 hours required)
4. Calculates commute times using Google Maps API (transit mode)
5. Filters by maximum commute (50 minutes)
6. Checks age restrictions (18+ requirements)
7. Sorts results by commute time
8. Returns JSON results

All processing happens in-memory - no files are created.

## Cost

**Google Cloud Functions:**
- Free tier: 2M invocations/month
- Your usage: ~10-20 runs/month
- Cost: $0/month

**Google Maps API:**
- Free tier: $200 credit/month
- Your usage: ~50-100 requests/run
- Cost: $0/month

**Total: $0/month** (within free tiers)
