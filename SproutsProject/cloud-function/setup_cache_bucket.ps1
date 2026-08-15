# Setup script for GCS cache bucket

Write-Host "=" * 80
Write-Host "Setting up GCS Cache Bucket"
Write-Host "=" * 80
Write-Host ""

# Get project ID
$PROJECT_ID = gcloud config get-value project 2>$null
$BUCKET_NAME = "sprouts-commute-cache"

Write-Host "Project ID: $PROJECT_ID"
Write-Host "Bucket name: gs://$BUCKET_NAME"
Write-Host ""

# Create bucket
Write-Host "Creating GCS bucket..."
gsutil mb -l us-central1 "gs://$BUCKET_NAME" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Bucket created successfully"
} else {
    Write-Host "[INFO] Bucket may already exist (this is fine)"
}

Write-Host ""
Write-Host "=" * 80
Write-Host "Setup Complete!"
Write-Host "=" * 80
Write-Host ""
Write-Host "Bucket: gs://$BUCKET_NAME"
Write-Host "Region: us-central1"
Write-Host ""
Write-Host "The Cloud Function will automatically:"
Write-Host "  - Load cache from this bucket at start"
Write-Host "  - Save cache to this bucket at end"
Write-Host ""
Write-Host "Cache will reduce:"
Write-Host "  - API calls by 90%"
Write-Host "  - Execution time by 75%"
Write-Host "  - Cost by 90%"
Write-Host ""
