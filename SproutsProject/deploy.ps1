# Deployment script for Sprouts Matching Cloud Function

Write-Host "=" * 80
Write-Host "DEPLOYING SPROUTS MATCHING CLOUD FUNCTION"
Write-Host "=" * 80
Write-Host ""

# Add gcloud to PATH
$env:Path += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

# Change to cloud-function directory
Set-Location cloud-function

Write-Host "Project: sprouts-446222"
Write-Host "Function: sprouts-matching"
Write-Host "Region: us-central1"
Write-Host "Runtime: python312"
Write-Host ""

Write-Host "Deploying... (this takes 2-3 minutes)"
Write-Host ""

# Deploy
gcloud functions deploy sprouts-matching `
  --runtime python312 `
  --trigger-http `
  --allow-unauthenticated `
  --entry-point app `
  --env-vars-file .env.yaml `
  --memory 512MB `
  --timeout 540s `
  --region us-central1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 80
    Write-Host "DEPLOYMENT SUCCESSFUL!"
    Write-Host "=" * 80
    Write-Host ""
    Write-Host "Getting function URL..."
    $url = gcloud functions describe sprouts-matching --region us-central1 --format="value(httpsTrigger.url)"
    Write-Host ""
    Write-Host "Cloud Function URL:"
    Write-Host "  $url"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Copy the URL above"
    Write-Host "  2. Update Google Apps Script Code.gs with this URL"
    Write-Host "  3. Test the function from your spreadsheet"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=" * 80
    Write-Host "DEPLOYMENT FAILED"
    Write-Host "=" * 80
    Write-Host ""
    Write-Host "Check the error messages above for details."
    Write-Host ""
}
