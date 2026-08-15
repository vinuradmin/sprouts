# GitHub Secrets Setup Guide

GitHub provides secure ways to store credentials that can be accessed across devices and in CI/CD workflows.

## Option 1: GitHub Secrets (For CI/CD & Actions)

GitHub Secrets are encrypted environment variables available to GitHub Actions workflows.

### Setup Steps:

1. Go to your repository: **https://github.com/vinuradmin/sprouts**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

#### Secret 1: `GOOGLE_CREDENTIALS`
- **Name**: `GOOGLE_CREDENTIALS`
- **Value**: Paste the entire contents of `credentials.json`

#### Secret 2: `GOOGLE_SERVICE_ACCOUNT_KEY`
- **Name**: `GOOGLE_SERVICE_ACCOUNT_KEY`
- **Value**: Paste the entire contents of `service-account-key.json`

### Using Secrets in GitHub Actions:

Create `.github/workflows/setup.yml`:

```yaml
name: Setup Credentials

on: [push, pull_request]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create credentials files
        run: |
          echo '${{ secrets.GOOGLE_CREDENTIALS }}' > SproutsProject/credentials.json
          echo '${{ secrets.GOOGLE_SERVICE_ACCOUNT_KEY }}' > SproutsProject/service-account-key.json
      
      - name: Run application
        run: |
          cd SproutsProject
          pip install -r requirements.txt
          python run.py
```

**Note**: GitHub Secrets are only available in GitHub Actions, not for local development.

---

## Option 2: GitHub Codespaces Secrets (For Cloud Development)

If you use GitHub Codespaces, you can store secrets that are automatically available in your cloud environment.

### Setup Steps:

1. Go to **https://github.com/settings/codespaces**
2. Scroll to **Codespaces secrets**
3. Click **New secret**
4. Add secrets (same as above)
5. Select which repositories can access them

### Access in Codespaces:

Secrets are available as environment variables. Create a setup script:

```bash
#!/bin/bash
# setup-credentials.sh

echo "$GOOGLE_CREDENTIALS" > SproutsProject/credentials.json
echo "$GOOGLE_SERVICE_ACCOUNT_KEY" > SproutsProject/service-account-key.json
```

---

## Option 3: Encrypted Files in Repository (For Team Access)

You can commit encrypted credential files that team members can decrypt.

### Using Git-Crypt (Recommended):

1. **Install git-crypt**:
   ```bash
   # Windows (using Chocolatey)
   choco install git-crypt
   
   # macOS
   brew install git-crypt
   
   # Linux
   sudo apt-get install git-crypt
   ```

2. **Initialize in your repo**:
   ```bash
   cd /path/to/windsurf-project
   git-crypt init
   ```

3. **Create `.gitattributes`**:
   ```
   SproutsProject/credentials.json filter=git-crypt diff=git-crypt
   SproutsProject/service-account-key.json filter=git-crypt diff=git-crypt
   ```

4. **Add GPG keys for team members**:
   ```bash
   git-crypt add-gpg-user USER_GPG_KEY_ID
   ```

5. **Commit the encrypted files**:
   ```bash
   git add SproutsProject/credentials.json SproutsProject/service-account-key.json
   git commit -m "Add encrypted credentials"
   git push
   ```

6. **Team members unlock**:
   ```bash
   git clone https://github.com/vinuradmin/sprouts.git
   cd sprouts
   git-crypt unlock
   ```

### Using SOPS (Alternative):

```bash
# Install SOPS
brew install sops  # macOS
choco install sops  # Windows

# Encrypt file
sops -e SproutsProject/credentials.json > SproutsProject/credentials.enc.json

# Decrypt file
sops -d SproutsProject/credentials.enc.json > SproutsProject/credentials.json
```

---

## Option 4: GitHub Gists (Private, Simple Sharing)

For simple credential sharing with team members:

1. Go to **https://gist.github.com/**
2. Create a **Secret Gist** (not public)
3. Add your credential files
4. Share the gist URL with team members
5. Team members download and place files locally

**Setup script for team**:
```bash
#!/bin/bash
# download-credentials.sh

# Replace with your actual gist ID
GIST_ID="your-gist-id-here"

curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://gist.githubusercontent.com/vinuradmin/$GIST_ID/raw/credentials.json \
  -o SproutsProject/credentials.json

curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://gist.githubusercontent.com/vinuradmin/$GIST_ID/raw/service-account-key.json \
  -o SproutsProject/service-account-key.json
```

---

## Comparison Table

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **GitHub Secrets** | CI/CD, GitHub Actions | Secure, built-in | Only for Actions |
| **Codespaces Secrets** | Cloud development | Easy, automatic | Only for Codespaces |
| **Git-Crypt** | Team collaboration | In-repo, versioned | Requires GPG setup |
| **Private Gist** | Simple sharing | Easy, quick | Manual download |

---

## Recommended Setup for Your Project

**For Development Team**:
1. Use **git-crypt** to encrypt credentials in the repo
2. Team members unlock with GPG keys
3. Credentials are automatically available after clone

**For CI/CD**:
1. Use **GitHub Secrets** for automated workflows
2. Workflows create credential files from secrets

**For Quick Sharing**:
1. Use **Private Gist** for immediate access
2. Provide download script to team

---

## Security Best Practices

✅ **DO:**
- Use GitHub Secrets for CI/CD workflows
- Encrypt files if committing to repo
- Rotate credentials regularly
- Limit access to authorized users
- Use separate credentials for dev/staging/prod

❌ **DON'T:**
- Store credentials in public gists
- Share credentials in issues/PRs
- Use production credentials in development
- Commit unencrypted credentials

---

## Quick Start: GitHub Secrets (Easiest)

1. **Add secrets to GitHub**:
   - Go to repo Settings → Secrets → New secret
   - Add `GOOGLE_CREDENTIALS` and `GOOGLE_SERVICE_ACCOUNT_KEY`

2. **Create download script** (`.github/scripts/setup-credentials.sh`):
   ```bash
   #!/bin/bash
   echo "$GOOGLE_CREDENTIALS" > SproutsProject/credentials.json
   echo "$GOOGLE_SERVICE_ACCOUNT_KEY" > SproutsProject/service-account-key.json
   chmod 600 SproutsProject/*.json
   ```

3. **Team members run locally**:
   ```bash
   # Set environment variables from GitHub Secrets (manual copy)
   export GOOGLE_CREDENTIALS='<paste from GitHub Secrets>'
   export GOOGLE_SERVICE_ACCOUNT_KEY='<paste from GitHub Secrets>'
   
   # Run setup script
   bash .github/scripts/setup-credentials.sh
   ```

**Note**: GitHub Secrets can't be read directly by team members, but you can share them via secure channels and team members can set them as local environment variables.

---

## Need Help?

Contact the repository administrator for:
- Access to GitHub Secrets
- GPG key setup for git-crypt
- Private gist access
