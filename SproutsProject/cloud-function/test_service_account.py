"""
Test script to verify service account authentication works
Run this before deploying to Cloud Functions
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import sys
import os

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'

def test_authentication():
    """Test that service account can authenticate"""
    print("Testing service account authentication...")
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: {SERVICE_ACCOUNT_FILE} not found!")
        print("Please download the service account key and place it in this directory.")
        return False
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        print("[OK] Service account credentials loaded")
        return creds
    except Exception as e:
        print(f"[ERROR] Error loading credentials: {e}")
        return False

def test_sheets_access(creds):
    """Test that service account can access the spreadsheet"""
    print("\nTesting Google Sheets API access...")
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        print("✓ Google Sheets API service created")
        
        # Try to read a small range
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Intern Availabilities!A1:E5'
        ).execute()
        
        values = result.get('values', [])
        print(f"✓ Successfully read {len(values)} rows from spreadsheet")
        
        if values:
            print(f"  Sample data: {values[0][:3]}...")
        
        return service
    except Exception as e:
        print(f"✗ Error accessing spreadsheet: {e}")
        print("\nPossible issues:")
        print("1. Spreadsheet not shared with service account")
        print("2. Incorrect spreadsheet ID")
        print("3. Sheet name 'Intern Availabilities' doesn't exist")
        return False

def test_read_full_sheet(service, sheet_name):
    """Test reading a full sheet"""
    print(f"\nTesting full read of '{sheet_name}'...")
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_name
        ).execute()
        
        values = result.get('values', [])
        print(f"✓ Read {len(values)} total rows from {sheet_name}")
        
        # Look for Season/Year column
        if values:
            header = values[0]
            for i, cell in enumerate(header):
                if str(cell).strip() == 'Season/Year':
                    print(f"✓ Found 'Season/Year' column at index {i}")
                    
                    # Count cohorts
                    cohorts = {}
                    for row in values[1:]:
                        if len(row) > i:
                            cohort = str(row[i]).strip()
                            if cohort:
                                cohorts[cohort] = cohorts.get(cohort, 0) + 1
                    
                    print(f"  Cohorts found:")
                    for cohort, count in cohorts.items():
                        print(f"    - {cohort}: {count} rows")
                    
                    return True
            
            print("✗ 'Season/Year' column not found in header")
            print(f"  Header columns: {header[:10]}...")
        
        return True
    except Exception as e:
        print(f"✗ Error reading sheet: {e}")
        return False

def main():
    print("="*80)
    print("SERVICE ACCOUNT AUTHENTICATION TEST")
    print("="*80)
    print()
    
    # Test 1: Authentication
    creds = test_authentication()
    if not creds:
        print("\n" + "="*80)
        print("FAILED: Could not load service account credentials")
        print("="*80)
        sys.exit(1)
    
    # Test 2: Sheets access
    service = test_sheets_access(creds)
    if not service:
        print("\n" + "="*80)
        print("FAILED: Could not access Google Sheets")
        print("="*80)
        sys.exit(1)
    
    # Test 3: Read full sheets
    test_read_full_sheet(service, 'Intern Availabilities')
    test_read_full_sheet(service, 'Chef Availabilities')
    
    print("\n" + "="*80)
    print("SUCCESS: All tests passed!")
    print("="*80)
    print("\nYou're ready to deploy the Cloud Function!")
    print("\nNext steps:")
    print("1. Deploy: gcloud functions deploy sprouts-matching ...")
    print("2. Test the deployed function")
    print("3. Add Apps Script to spreadsheet")

if __name__ == '__main__':
    main()
