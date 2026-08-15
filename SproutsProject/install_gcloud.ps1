# Google Cloud SDK Installation Script for Windows

Write-Host "=" * 80
Write-Host "GOOGLE CLOUD SDK INSTALLATION"
Write-Host "=" * 80
Write-Host ""

# Check if gcloud is already installed
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue

if ($gcloudPath) {
    Write-Host "[OK] Google Cloud SDK is already installed!"
    Write-Host "     Location: $($gcloudPath.Source)"
    Write-Host ""
    & gcloud --version
    Write-Host ""
    Write-Host "You're ready to deploy!"
    exit 0
}

Write-Host "[INFO] Google Cloud SDK not found. Installing..."
Write-Host ""

# Download URL
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

Write-Host "Downloading Google Cloud SDK installer..."
Write-Host "URL: $installerUrl"
Write-Host "Saving to: $installerPath"
Write-Host ""

try {
    # Download installer
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Write-Host "[OK] Download complete!"
    Write-Host ""
    
    # Run installer
    Write-Host "Starting installer..."
    Write-Host ""
    Write-Host "IMPORTANT: During installation:"
    Write-Host "  1. Accept the default installation path"
    Write-Host "  2. Check 'Run gcloud init' at the end"
    Write-Host "  3. Follow the authentication prompts"
    Write-Host ""
    
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "[OK] Installation complete!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Close and reopen PowerShell"
    Write-Host "  2. Run: gcloud init"
    Write-Host "  3. Authenticate with your Google account"
    Write-Host "  4. Select your project: sprouts-446222"
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to download installer: $_"
    Write-Host ""
    Write-Host "Manual installation:"
    Write-Host "  1. Go to: https://cloud.google.com/sdk/docs/install"
    Write-Host "  2. Download the Windows installer"
    Write-Host "  3. Run the installer"
    Write-Host ""
}

Write-Host "=" * 80
