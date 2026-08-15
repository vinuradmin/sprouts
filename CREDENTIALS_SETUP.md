# Credentials Setup Guide

This project requires Google Cloud credentials to function properly. These credentials are **NOT** stored in the repository for security reasons.

## Required Credentials

### 1. Google OAuth Credentials (`credentials.json`)
- **Location**: `SproutsProject/credentials.json`
- **Template**: See `SproutsProject/credentials.example.json`

### 2. Google Service Account Key (`service-account-key.json`)
- **Location**: `SproutsProject/service-account-key.json`
- **Template**: See `SproutsProject/service-account-key.example.json`

## Setup Instructions

### Option 1: Secure Credential Storage (Recommended)

Use a secure credential management system:

1. **Store credentials in a password manager** (1Password, LastPass, Bitwarden, etc.)
2. **Share with team members** through the password manager's secure sharing feature
3. **Download and place** the files in the correct locations when setting up a new device

### Option 2: Private Cloud Storage

1. Store credentials in a **private cloud storage** (Google Drive, Dropbox, OneDrive)
2. Set up **restricted access** (only share with authorized team members)
3. Download credentials when setting up a new device
4. Place files in the correct locations

### Option 3: Environment Variables (For Production)

For production deployments, use environment variables instead of JSON files:

```python
import os
import json

# For service account
service_account_info = {
    "type": "service_account",
    "project_id": os.getenv("GCP_PROJECT_ID"),
    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GCP_CLIENT_EMAIL"),
    # ... other fields
}
```

### Option 4: Secret Management Service (For Teams)

For larger teams, consider using:
- **AWS Secrets Manager**
- **Google Cloud Secret Manager**
- **Azure Key Vault**
- **HashiCorp Vault**

## Quick Setup Steps

After cloning the repository on a new device:

1. Copy your credential files to the project:
   ```bash
   # Navigate to project directory
   cd SproutsProject
   
   # Copy credentials from your secure storage
   cp /path/to/your/credentials.json ./credentials.json
   cp /path/to/your/service-account-key.json ./service-account-key.json
   ```

2. Verify the files are in place:
   ```bash
   ls -la *.json
   ```

3. Ensure they are ignored by git:
   ```bash
   git status
   # Should NOT show credentials.json or service-account-key.json
   ```

## Security Best Practices

✅ **DO:**
- Keep credentials in a secure password manager
- Use environment variables in production
- Rotate credentials regularly
- Limit access to authorized team members only
- Use service accounts with minimal required permissions

❌ **DON'T:**
- Commit credentials to git (already prevented by `.gitignore`)
- Share credentials via email or chat
- Store credentials in public locations
- Use the same credentials across environments

## Getting Credentials

### For Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Create or download **OAuth 2.0 Client ID** credentials

### For Service Account Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **IAM & Admin** > **Service Accounts**
4. Select your service account
5. Go to **Keys** tab
6. Click **Add Key** > **Create new key** > **JSON**

## Troubleshooting

**Issue**: Application can't find credentials
- **Solution**: Verify files are in `SproutsProject/` directory with exact names

**Issue**: Permission denied errors
- **Solution**: Check that service account has necessary Google Sheets/Maps API permissions

**Issue**: Invalid credentials
- **Solution**: Re-download fresh credentials from Google Cloud Console

## Contact

For credential access, contact the project administrator.
