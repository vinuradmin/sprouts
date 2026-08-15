#!/usr/bin/env python3
"""
Test service account credentials and permissions
"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load service account info
with open('service-account-key.json', 'r') as f:
    sa_info = json.load(f)

print("="*80)
print("SERVICE ACCOUNT DIAGNOSTICS")
print("="*80)

print("\n1. Service Account Info:")
print(f"   Email: {sa_info['client_email']}")
print(f"   Project ID: {sa_info['project_id']}")
print(f"   Type: {sa_info['type']}")

print("\n2. Testing Credentials:")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

try:
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=SCOPES)
    print("   Credentials loaded successfully")
    
    print("\n3. Testing API Access:")
    service = build('sheets', 'v4', credentials=credentials)
    print("   Sheets API service created successfully")
    
    print("\n4. Attempting to access spreadsheet:")
    SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
    
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        print("   SUCCESS! Can access spreadsheet")
        print(f"   Spreadsheet title: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
        
        sheets = sheet_metadata.get('sheets', [])
        print(f"\n5. Found {len(sheets)} sheets:")
        for sheet in sheets:
            title = sheet.get('properties', {}).get('title', '')
            gid = sheet.get('properties', {}).get('sheetId', '')
            print(f"   - {title} (GID: {gid})")
            
    except Exception as e:
        print(f"   FAILED: {e}")
        print("\n   Troubleshooting:")
        print("   1. Make sure you shared the sheet with: " + sa_info['client_email'])
        print("   2. Check that you gave 'Viewer' or 'Editor' permission")
        print("   3. Verify the spreadsheet ID is correct")
        print("   4. Make sure Google Sheets API is enabled in your project")
        print("      Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com")
        
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*80)
