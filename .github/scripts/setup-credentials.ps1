# PowerShell script to create credential files from environment variables
# These environment variables should be set from GitHub Secrets or manually

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptDir\..\.." -Force).FullName
$CredsDir = Join-Path $ProjectRoot "SproutsProject"

Write-Host "Setting up credentials in $CredsDir..." -ForegroundColor Cyan

# Check if environment variables are set
if (-not $env:GOOGLE_CREDENTIALS) {
    Write-Host "❌ Error: GOOGLE_CREDENTIALS environment variable is not set" -ForegroundColor Red
    Write-Host "Please set it with: `$env:GOOGLE_CREDENTIALS='<json content>'" -ForegroundColor Yellow
    exit 1
}

if (-not $env:GOOGLE_SERVICE_ACCOUNT_KEY) {
    Write-Host "❌ Error: GOOGLE_SERVICE_ACCOUNT_KEY environment variable is not set" -ForegroundColor Red
    Write-Host "Please set it with: `$env:GOOGLE_SERVICE_ACCOUNT_KEY='<json content>'" -ForegroundColor Yellow
    exit 1
}

# Create credentials directory if it doesn't exist
if (-not (Test-Path $CredsDir)) {
    New-Item -ItemType Directory -Path $CredsDir -Force | Out-Null
}

# Write credentials to files
$env:GOOGLE_CREDENTIALS | Out-File -FilePath "$CredsDir\credentials.json" -Encoding UTF8 -NoNewline
$env:GOOGLE_SERVICE_ACCOUNT_KEY | Out-File -FilePath "$CredsDir\service-account-key.json" -Encoding UTF8 -NoNewline

Write-Host "✅ Credentials successfully created:" -ForegroundColor Green
Write-Host "   - $CredsDir\credentials.json"
Write-Host "   - $CredsDir\service-account-key.json"
Write-Host ""
Write-Host "⚠️  Remember: These files are gitignored and won't be committed" -ForegroundColor Yellow
