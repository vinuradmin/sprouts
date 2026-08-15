"""
Interactive script to help set up service account
Guides you through the process step-by-step
"""

import os
import json
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def validate_service_account_key(filepath):
    """Validate that the service account key file is valid JSON"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        if data['type'] != 'service_account':
            return False, "Not a service account key file"
        
        return True, data
    except json.JSONDecodeError:
        return False, "Invalid JSON file"
    except Exception as e:
        return False, str(e)

def main():
    print("="*80)
    print("SERVICE ACCOUNT SETUP WIZARD")
    print("="*80)
    print()
    
    print("This wizard will help you set up the service account for the Cloud Function.")
    print()
    
    # Step 1: Check for service account key
    print("Step 1: Service Account Key File")
    print("-" * 40)
    
    key_file = 'cloud-function/service-account-key.json'
    
    if check_file_exists(key_file):
        print(f"✓ Found: {key_file}")
        
        # Validate the file
        valid, result = validate_service_account_key(key_file)
        
        if valid:
            data = result
            print(f"✓ Valid service account key")
            print(f"\n  Project ID: {data['project_id']}")
            print(f"  Service Account Email: {data['client_email']}")
            print()
        else:
            print(f"✗ Invalid key file: {result}")
            print("\nPlease download a valid service account key from Google Cloud Console.")
            sys.exit(1)
    else:
        print(f"✗ Not found: {key_file}")
        print("\nTo create a service account key:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Navigate to: IAM & Admin > Service Accounts")
        print("3. Create a new service account (or use existing)")
        print("4. Click on the service account")
        print("5. Go to KEYS tab > ADD KEY > Create new key")
        print("6. Choose JSON format")
        print("7. Save as: cloud-function/service-account-key.json")
        print()
        sys.exit(1)
    
    # Step 2: Share spreadsheet
    print("Step 2: Share Spreadsheet with Service Account")
    print("-" * 40)
    print(f"\nService Account Email:")
    print(f"  {data['client_email']}")
    print()
    print("To share the spreadsheet:")
    print("1. Open your Google Spreadsheet")
    print("2. Click the 'Share' button (top right)")
    print("3. Paste the service account email above")
    print("4. Set permission to 'Viewer'")
    print("5. Uncheck 'Notify people'")
    print("6. Click 'Share'")
    print()
    
    response = input("Have you shared the spreadsheet? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nPlease share the spreadsheet first, then run this script again.")
        sys.exit(1)
    
    # Step 3: Test connection
    print("\nStep 3: Test Connection")
    print("-" * 40)
    print("\nTesting service account access...")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
        
        creds = service_account.Credentials.from_service_account_file(
            key_file, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Intern Availabilities!A1:B5'
        ).execute()
        
        values = result.get('values', [])
        
        print(f"✓ Successfully connected to Google Sheets")
        print(f"✓ Read {len(values)} rows from spreadsheet")
        print()
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. Spreadsheet not shared with service account")
        print("2. Service account doesn't have Viewer permission")
        print("3. Spreadsheet ID is incorrect")
        print()
        sys.exit(1)
    
    # Step 4: Summary
    print("="*80)
    print("✓ SETUP COMPLETE!")
    print("="*80)
    print()
    print("Your service account is configured and working!")
    print()
    print("Next steps:")
    print("1. Test locally: cd cloud-function && python test_service_account.py")
    print("2. Deploy to Cloud: gcloud functions deploy sprouts-matching ...")
    print("3. Add Apps Script to spreadsheet")
    print()
    print("See DEPLOYMENT_GUIDE.md for detailed deployment instructions.")
    print()

if __name__ == '__main__':
    main()
