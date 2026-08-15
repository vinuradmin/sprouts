# Security Guide - Credential Management for Cloud Deployment

## Overview

When deploying to Google Cloud Functions, you need to handle two types of credentials securely:
1. **Service Account Key** (for Google Sheets access)
2. **Google Maps API Key** (for commute calculations)

## Security Options (Best to Worst)

### ⭐ Option 1: Google Secret Manager (RECOMMENDED)

**Best for production.** Secrets are encrypted and managed by Google Cloud.

**Pros:**
- ✅ Secrets encrypted at rest and in transit
- ✅ Automatic rotation support
- ✅ Audit logging of secret access
- ✅ Fine-grained access control
- ✅ No secrets in code or config files

**Cons:**
- Slightly more complex setup
- Small cost (free tier: 6 secrets, 10,000 accesses/month)

### Option 2: Environment Variables (SIMPLE)

**Good for development/testing.** Secrets passed as environment variables.

**Pros:**
- ✅ Simple to set up
- ✅ Secrets not in code
- ✅ Free

**Cons:**
- ⚠️ Visible in Cloud Console
- ⚠️ Logged in deployment history
- ⚠️ No encryption at rest

### Option 3: Hardcoded (NEVER DO THIS)

**Never use in production.**

**Cons:**
- ❌ Secrets in source code
- ❌ Visible in git history
- ❌ Security risk

## Recommended Approach: Secret Manager + Service Account

### Architecture

```
Cloud Function
    ↓
Service Account (built-in, no key needed!)
    ↓
Google Sheets API
    ↓
Secret Manager (for Google Maps API key)
```

**Key insight:** Cloud Functions have a **built-in service account** - you don't need to upload the key file!

## Implementation

### Step 1: Use Built-in Service Account (No Key Upload!)

When you deploy a Cloud Function, it automatically gets a service account:
```
PROJECT_ID@appspot.gserviceaccount.com
```

**You don't need to upload `service-account-key.json` to the cloud!**

Instead:
1. Share your spreadsheet with the Cloud Function's service account
2. The function uses the built-in credentials automatically

### Step 2: Store Google Maps API Key in Secret Manager

#### Create Secret

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secret for Google Maps API key
echo -n "AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg" | \
  gcloud secrets create google-maps-api-key --data-file=-

# Verify
gcloud secrets versions access latest --secret="google-maps-api-key"
```

#### Grant Access to Cloud Function

```bash
# Get the Cloud Function's service account
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

# Grant access to the secret
gcloud secrets add-iam-policy-binding google-maps-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 3: Update Cloud Function Code

Update `main.py` to use Secret Manager:

```python
from google.cloud import secretmanager
import os

def get_secret(secret_id):
    """Retrieve secret from Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('GCP_PROJECT') or os.environ.get('GOOGLE_CLOUD_PROJECT')
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Get API key from Secret Manager
GOOGLE_MAPS_API_KEY = get_secret('google-maps-api-key')
```

### Step 4: Update requirements.txt

Add Secret Manager client:
```txt
google-cloud-secret-manager==2.16.4
```

### Step 5: Deploy Without Secrets in Config

```bash
gcloud functions deploy sprouts-matching \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app \
  --memory 512MB \
  --timeout 540s \
  --region us-central1
  # No --env-vars-file needed!
```

## Alternative: Environment Variables (Simpler)

If you want to keep it simple for now:

### Create .env.yaml (NEVER COMMIT THIS)

```yaml
GOOGLE_MAPS_API_KEY: "AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg"
```

### Add to .gitignore

```
.env.yaml
.env
*.env
service-account-key.json
```

### Deploy with Environment Variables

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

## Service Account Key Handling

### For Local Development

**Keep the key file locally:**
```
cloud-function/
├── service-account-key.json  ← Only on your machine
├── .gitignore                ← Blocks key from git
└── main.py
```

### For Cloud Deployment

**Don't upload the key!** Instead:

1. **Find your Cloud Function's service account:**
   ```bash
   PROJECT_ID=$(gcloud config get-value project)
   echo "${PROJECT_ID}@appspot.gserviceaccount.com"
   ```

2. **Share spreadsheet with that email**

3. **Update main.py to use default credentials:**
   ```python
   from google.auth import default
   
   # In Cloud Function, use default credentials
   if os.getenv('FUNCTION_NAME'):  # Running in Cloud Function
       creds, project = default()
   else:  # Running locally
       creds = service_account.Credentials.from_service_account_file(
           'service-account-key.json', scopes=SCOPES)
   ```

## Security Checklist

### Before Deployment

- [ ] Service account key is in `.gitignore`
- [ ] `.env.yaml` is in `.gitignore`
- [ ] No API keys in source code
- [ ] No secrets committed to git

### After Deployment

- [ ] Spreadsheet shared with Cloud Function service account
- [ ] Google Maps API key in Secret Manager (or env vars)
- [ ] Service account key NOT uploaded to cloud
- [ ] Cloud Function has minimal permissions

### Regular Maintenance

- [ ] Rotate API keys every 90 days
- [ ] Review service account permissions
- [ ] Check Secret Manager access logs
- [ ] Update dependencies regularly

## Git Security

### .gitignore Template

```gitignore
# Secrets and credentials
service-account-key.json
*-key.json
*.json
!package.json
!requirements.txt

# Environment files
.env
.env.*
.env.yaml
*.env

# Python
__pycache__/
*.pyc

# IDE
.vscode/
.idea/
```

### Check for Leaked Secrets

```bash
# Before committing
git status

# Make sure these are NOT listed:
# - service-account-key.json
# - .env.yaml
# - Any files with API keys
```

### If You Accidentally Commit Secrets

1. **Immediately rotate the credentials**
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch service-account-key.json" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if remote)
4. **Notify team** to re-clone

## Monitoring

### View Secret Access

```bash
# Check who accessed secrets
gcloud logging read "resource.type=secretmanager.googleapis.com/Secret" \
  --limit 50 \
  --format json
```

### Audit Cloud Function Access

```bash
# View function invocations
gcloud functions logs read sprouts-matching --limit 100
```

## Cost Optimization

### Secret Manager Pricing

- **Free tier:** 6 secrets, 10,000 accesses/month
- **After free tier:** $0.06 per secret/month, $0.03 per 10,000 accesses

**Your usage:** 1 secret, ~20 accesses/month = **$0/month** (within free tier)

### Environment Variables Pricing

- **Free** (no additional cost)

## Comparison Table

| Feature | Secret Manager | Environment Variables | Hardcoded |
|---------|---------------|----------------------|-----------|
| **Security** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ |
| **Ease of Setup** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Rotation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ |
| **Audit Logging** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ |
| **Cost** | Free tier | Free | Free |
| **Production Ready** | ✅ | ⚠️ | ❌ |

## Recommendation

### For Your Use Case

**Start with Environment Variables**, then migrate to Secret Manager:

**Phase 1 (Now):**
- Use `.env.yaml` for Google Maps API key
- Use built-in service account (no key upload)
- Deploy and test

**Phase 2 (Later):**
- Migrate API key to Secret Manager
- Set up secret rotation
- Enable audit logging

This gives you good security now, with a path to excellent security later.

## Quick Start Commands

### Setup (One-time)

```bash
# 1. Create .env.yaml
echo "GOOGLE_MAPS_API_KEY: 'YOUR_KEY'" > cloud-function/.env.yaml

# 2. Add to .gitignore
echo ".env.yaml" >> cloud-function/.gitignore
echo "service-account-key.json" >> cloud-function/.gitignore

# 3. Get Cloud Function service account
PROJECT_ID=$(gcloud config get-value project)
echo "Share spreadsheet with: ${PROJECT_ID}@appspot.gserviceaccount.com"
```

### Deploy

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

## Summary

**What's Secure:**
✅ Service account key stays local (not uploaded to cloud)
✅ Cloud Function uses built-in service account
✅ API key in environment variables (not in code)
✅ All secrets in `.gitignore`

**What's Not Committed:**
- `service-account-key.json`
- `.env.yaml`
- Any files with API keys

**What Gets Deployed:**
- Python code (`main.py`)
- Dependencies (`requirements.txt`)
- Environment variables (encrypted by Google)

**Result:** Your credentials are secure and never exposed in source code or git history! 🔒
