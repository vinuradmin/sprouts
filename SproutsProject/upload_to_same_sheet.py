#!/usr/bin/env python3
"""
Upload Spring 2026 matching results to the SAME Google Sheet as a new tab
"""

import csv
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The ID of the existing spreadsheet
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get valid user credentials from storage or run OAuth flow."""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def read_csv_data(filename):
    """Read CSV file and return data as list of lists"""
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def add_sheet_to_spreadsheet(service, spreadsheet_id, sheet_name, data):
    """Add a new sheet to existing spreadsheet and populate with data"""
    try:
        # First, try to create the new sheet
        print(f"\nCreating new tab '{sheet_name}'...")
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'frozenRowCount': 1  # Freeze header row
                        }
                    }
                }
            }]
        }
        
        try:
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            print(f"Created new tab: {sheet_name} (ID: {sheet_id})")
            
        except HttpError as err:
            error_msg = str(err)
            if 'already exists' in error_msg:
                print(f"Tab '{sheet_name}' already exists. Will update it instead.")
            else:
                raise
        
        # Upload data to the sheet
        print(f"\nUploading data to '{sheet_name}'...")
        body = {
            'values': data
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Uploaded {result.get('updatedCells')} cells")
        
        return True
        
    except HttpError as err:
        error_msg = str(err)
        if 'does not have permission' in error_msg or 'PERMISSION_DENIED' in error_msg:
            print(f"\nERROR: You don't have edit permission for this spreadsheet.")
            print(f"Please ask the spreadsheet owner to grant you 'Editor' access.")
            print(f"Spreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            return False
        else:
            print(f"An error occurred: {err}")
            return False

def main():
    """Main function"""
    print("="*80)
    print("UPLOADING SPRING 2026 RESULTS TO EXISTING GOOGLE SHEET")
    print("="*80)
    
    # Get credentials
    print("\n1. Authenticating with Google...")
    creds = get_credentials()
    
    # Build the service
    service = build('sheets', 'v4', credentials=creds)
    
    # Read CSV data
    print("\n2. Reading CSV data...")
    csv_filename = 'C:/Users/pierr/OneDrive/Documents/intern_to_restaurant_spring_2026.csv'
    data = read_csv_data(csv_filename)
    print(f"   Read {len(data)} rows from {csv_filename}")
    
    # Add new sheet to existing spreadsheet
    print("\n3. Adding new tab to existing Google Sheet...")
    sheet_name = "Spring 2026 Matches"
    success = add_sheet_to_spreadsheet(service, SPREADSHEET_ID, sheet_name, data)
    
    if success:
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"\nSpring 2026 matching results uploaded to new tab!")
        print(f"\nView your spreadsheet:")
        print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        print(f"\nTab name: {sheet_name}")
        print(f"Rows uploaded: {len(data)}")
    else:
        print("\n" + "="*80)
        print("FAILED")
        print("="*80)
        print("\nCould not upload to the spreadsheet.")
        print("This is likely due to permission issues.")

if __name__ == '__main__':
    main()
