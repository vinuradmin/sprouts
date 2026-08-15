"""
Quick test to verify service account is set up correctly
This is a simplified version for immediate testing
"""

import os
import json

print("="*80)
print("QUICK SERVICE ACCOUNT CHECK")
print("="*80)
print()

# Check if service account key exists
key_file = 'cloud-function/service-account-key.json'

if os.path.exists(key_file):
    print(f"[OK] Found service account key: {key_file}")
    
    # Read and validate
    try:
        with open(key_file, 'r') as f:
            data = json.load(f)
        
        print(f"[OK] Valid JSON file")
        print(f"\n  Project ID: {data.get('project_id', 'N/A')}")
        print(f"  Service Account Email: {data.get('client_email', 'N/A')}")
        print()
        print("NEXT STEP:")
        print(f"Share your Google Spreadsheet with this email:")
        print(f"  {data.get('client_email', 'N/A')}")
        print()
        print("Then run: cd cloud-function && python test_service_account.py")
        
    except Exception as e:
        print(f"[ERROR] Error reading key file: {e}")
else:
    print(f"[NOT FOUND] Service account key not found: {key_file}")
    print()
    print("TO CREATE SERVICE ACCOUNT KEY:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project (or create new)")
    print("3. Navigate to: IAM & Admin > Service Accounts")
    print("4. Click: + CREATE SERVICE ACCOUNT")
    print("5. Name: sprouts-matching")
    print("6. Click: CREATE AND CONTINUE (skip permissions)")
    print("7. Click: DONE")
    print("8. Click on the service account you just created")
    print("9. Go to: KEYS tab")
    print("10. Click: ADD KEY > Create new key")
    print("11. Select: JSON")
    print("12. Click: CREATE")
    print("13. Save the downloaded file as: cloud-function/service-account-key.json")
    print()

print("="*80)
