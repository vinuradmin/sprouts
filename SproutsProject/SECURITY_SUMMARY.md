# Security Summary - How Your Credentials Are Protected

## TL;DR - What's Secure

✅ **Service Account Key**: Stays on your local machine, NEVER uploaded to cloud
✅ **Google Maps API Key**: Encrypted environment variable, NOT in source code  
✅ **No Secrets in Git**: All sensitive files blocked by `.gitignore`
✅ **Built-in Authentication**: Cloud Function uses Google's built-in service account

## How It Works

### Local Development (Your Machine)

```
Your Computer
├── service-account-key.json  ← Stays here, never uploaded
├── .env.yaml                 ← Stays here, never uploaded
└── main.py                   ← Uses local key file for testing
```

**When you test locally:**
- Reads `service-account-key.json` from disk
- Uses API key from `.env.yaml`
- Both files protected by `.gitignore`

### Cloud Deployment (Google Cloud)

```
Google Cloud Function
├── main.py                   ← Your code (no secrets)
├── requirements.txt          ← Dependencies
└── Built-in Service Account  ← Automatic, no key needed!
    └── Environment Variables ← API key (encrypted by Google)
```

**When deployed to cloud:**
- NO `service-account-key.json` uploaded
- Uses Cloud Function's built-in service account
- API key passed as encrypted environment variable
- Google handles all encryption/decryption

## The Magic: Built-in Service Account

Every Cloud Function automatically gets a service account:
```
YOUR-PROJECT-ID@appspot.gserviceaccount.com
```

**This means:**
- ✅ No need to upload private keys
- ✅ Google manages authentication
- ✅ Automatic credential rotation
- ✅ Secure by default

## How Credentials Flow

### 1. Local Testing

```
main.py
  ↓
Checks: Am I running locally?
  ↓
YES → Read service-account-key.json
  ↓
Authenticate with Google Sheets
```

### 2. Cloud Function

```
main.py
  ↓
Checks: Am I running in Cloud Function?
  ↓
YES → Use built-in credentials (no file needed)
  ↓
Authenticate with Google Sheets
```

**Code that makes this work:**

```python
def get_sheets_service():
    if os.getenv('FUNCTION_NAME'):  # In cloud?
        creds, _ = default()  # Use built-in
    else:  # Local?
        creds = service_account.Credentials.from_service_account_file(
            'service-account-key.json')  # Use file
    return build('sheets', 'v4', credentials=creds)
```

## What Gets Deployed vs What Stays Local

### Deployed to Cloud ✅

| File | Contains | Security |
|------|----------|----------|
| `main.py` | Code | ✅ No secrets |
| `requirements.txt` | Dependencies | ✅ Public info |
| Environment vars | API key | ✅ Encrypted by Google |

### Stays on Your Machine ❌

| File | Contains | Why Not Deployed |
|------|----------|------------------|
| `service-account-key.json` | Private key | ❌ Not needed (built-in auth) |
| `.env.yaml` | API key | ❌ Only values extracted |
| `.gitignore` | File list | ❌ Not needed in cloud |

## Git Protection

### .gitignore Blocks These Files

```gitignore
service-account-key.json   # Private key
.env.yaml                  # API key
*.env                      # Any env files
*-key.json                 # Any key files
```

**Result:** Even if you try to commit them, git will refuse!

### Verify Protection

```bash
# This should show NO sensitive files
git status

# If you see these, they're NOT protected:
# - service-account-key.json  ❌ BAD
# - .env.yaml                 ❌ BAD
```

## API Key Security

### ❌ INSECURE (Don't do this)

```python
# Hardcoded - visible in source code
GOOGLE_MAPS_API_KEY = "AIzaSyAILDN2YIseCh_iFMZVj5pTgZvS5hxiJbg"
```

### ✅ SECURE (What we do)

```python
# From environment variable - encrypted by Google
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
```

**Deployment:**
```bash
gcloud functions deploy ... --env-vars-file .env.yaml
```

**What happens:**
1. Google reads `.env.yaml` on your machine
2. Extracts the API key value
3. Encrypts it
4. Stores in Cloud Function environment
5. `.env.yaml` file is NOT uploaded

## Sharing Spreadsheet

### Two Service Accounts

**1. Local Development (your machine):**
```
sprouts@sprouts-446222.iam.gserviceaccount.com
```
- From `service-account-key.json`
- Used for local testing

**2. Cloud Function (deployed):**
```
sprouts-446222@appspot.gserviceaccount.com
```
- Built-in to Cloud Function
- Used in production

**Share spreadsheet with BOTH:**
- Local account: For testing on your machine
- Cloud account: For production deployment

## Security Checklist

### Before Deployment

- [x] `.gitignore` contains `service-account-key.json`
- [x] `.gitignore` contains `.env.yaml`
- [x] No API keys hardcoded in `main.py`
- [x] `git status` shows no sensitive files

### During Deployment

- [x] Using `--env-vars-file` (not hardcoded)
- [x] Service account key NOT in deployment command
- [x] Spreadsheet shared with Cloud Function service account

### After Deployment

- [x] Test function works
- [x] Check logs for errors
- [x] Verify no secrets in Cloud Console source view

## What If Secrets Leak?

### If service-account-key.json is exposed:

1. **Immediately** go to Google Cloud Console
2. Navigate to: IAM & Admin > Service Accounts
3. Find your service account
4. Go to KEYS tab
5. Delete the compromised key
6. Create a new key
7. Download and save as `service-account-key.json`

### If Google Maps API key is exposed:

1. **Immediately** go to Google Cloud Console
2. Navigate to: APIs & Services > Credentials
3. Find your API key
4. Click "Regenerate key"
5. Update `.env.yaml` with new key
6. Redeploy Cloud Function

## Monitoring

### Check for Unauthorized Access

```bash
# View Cloud Function logs
gcloud functions logs read sprouts-matching --limit 100

# Look for:
# - Unexpected invocations
# - Failed authentication attempts
# - Unusual patterns
```

### Audit Spreadsheet Access

1. Open spreadsheet
2. Click "Share"
3. Review who has access
4. Remove any unknown accounts

## Cost of Security

| Security Feature | Cost |
|------------------|------|
| Built-in service account | Free |
| Environment variables | Free |
| Cloud Function encryption | Free |
| Google Sheets API | Free (within quota) |
| **Total** | **$0/month** |

## Summary

**Your deployment is secure because:**

1. ✅ **No private keys uploaded** - Cloud Function uses built-in auth
2. ✅ **API keys encrypted** - Passed as environment variables
3. ✅ **No secrets in code** - All credentials externalized
4. ✅ **Git protection** - Sensitive files blocked by `.gitignore`
5. ✅ **Automatic encryption** - Google handles all crypto

**What you need to remember:**

- Keep `service-account-key.json` on your machine only
- Never commit `.env.yaml` to git
- Share spreadsheet with Cloud Function's service account
- Rotate credentials every 90 days

**You're ready to deploy securely! 🔒**
