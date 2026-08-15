#!/bin/bash
# Setup script for GCS cache bucket

echo "=========================================="
echo "Setting up GCS Cache Bucket"
echo "=========================================="
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="sprouts-commute-cache"

echo "Project ID: $PROJECT_ID"
echo "Bucket name: gs://$BUCKET_NAME"
echo ""

# Create bucket
echo "Creating GCS bucket..."
gsutil mb -l us-central1 gs://$BUCKET_NAME

if [ $? -eq 0 ]; then
    echo "[OK] Bucket created successfully"
else
    echo "[INFO] Bucket may already exist"
fi

# Set bucket to be private
echo ""
echo "Setting bucket permissions..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME -d 2>/dev/null

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Bucket: gs://$BUCKET_NAME"
echo "Region: us-central1"
echo ""
echo "The Cloud Function will automatically:"
echo "  - Load cache from this bucket at start"
echo "  - Save cache to this bucket at end"
echo ""
