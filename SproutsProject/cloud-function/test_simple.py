"""
Simple test for service account - no unicode characters
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'

print("="*80)
print("SERVICE ACCOUNT TEST")
print("="*80)
print()

# Step 1: Load credentials
print("Step 1: Loading service account credentials...")
try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    print("[OK] Credentials loaded")
    print(f"     Service account: {creds.service_account_email}")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Step 2: Create Sheets service
print("\nStep 2: Creating Google Sheets API service...")
try:
    service = build('sheets', 'v4', credentials=creds)
    print("[OK] Service created")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Step 3: Test reading spreadsheet
print("\nStep 3: Testing spreadsheet access...")
try:
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Intern Availabilities!A1:E5'
    ).execute()
    
    values = result.get('values', [])
    print(f"[OK] Successfully read {len(values)} rows")
    
    if values:
        print(f"     First row: {values[0][:3]}...")
    
except Exception as e:
    print(f"[ERROR] {e}")
    print("\nMake sure you've shared the spreadsheet with:")
    print(f"  {creds.service_account_email}")
    exit(1)

# Step 4: Check for Season/Year column
print("\nStep 4: Looking for Season/Year column...")
try:
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Intern Availabilities'
    ).execute()
    
    values = result.get('values', [])
    
    if values:
        header = values[0]
        season_col = None
        
        for i, cell in enumerate(header):
            if str(cell).strip() == 'Season/Year':
                season_col = i
                print(f"[OK] Found 'Season/Year' at column {i}")
                break
        
        if season_col is not None:
            # Count cohorts
            cohorts = {}
            for row in values[1:]:
                if len(row) > season_col:
                    cohort = str(row[season_col]).strip()
                    if cohort:
                        cohorts[cohort] = cohorts.get(cohort, 0) + 1
            
            print("\n     Cohorts found:")
            for cohort, count in cohorts.items():
                print(f"       - {cohort}: {count} rows")
        else:
            print("[WARNING] Season/Year column not found")
            print(f"           Header: {header[:10]}...")
    
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("\nService account is working correctly!")
print("You can now deploy to Google Cloud Functions.")
