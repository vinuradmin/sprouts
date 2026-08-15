#!/bin/bash
# Setup script to create credential files from environment variables
# These environment variables should be set from GitHub Secrets or manually

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CREDS_DIR="$PROJECT_ROOT/SproutsProject"

echo "Setting up credentials in $CREDS_DIR..."

# Check if environment variables are set
if [ -z "$GOOGLE_CREDENTIALS" ]; then
    echo "❌ Error: GOOGLE_CREDENTIALS environment variable is not set"
    echo "Please set it with: export GOOGLE_CREDENTIALS='<json content>'"
    exit 1
fi

if [ -z "$GOOGLE_SERVICE_ACCOUNT_KEY" ]; then
    echo "❌ Error: GOOGLE_SERVICE_ACCOUNT_KEY environment variable is not set"
    echo "Please set it with: export GOOGLE_SERVICE_ACCOUNT_KEY='<json content>'"
    exit 1
fi

# Create credentials directory if it doesn't exist
mkdir -p "$CREDS_DIR"

# Write credentials to files
echo "$GOOGLE_CREDENTIALS" > "$CREDS_DIR/credentials.json"
echo "$GOOGLE_SERVICE_ACCOUNT_KEY" > "$CREDS_DIR/service-account-key.json"

# Set restrictive permissions
chmod 600 "$CREDS_DIR/credentials.json"
chmod 600 "$CREDS_DIR/service-account-key.json"

echo "✅ Credentials successfully created:"
echo "   - $CREDS_DIR/credentials.json"
echo "   - $CREDS_DIR/service-account-key.json"
echo ""
echo "⚠️  Remember: These files are gitignored and won't be committed"
