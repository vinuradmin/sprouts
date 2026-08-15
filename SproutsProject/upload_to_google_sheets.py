#!/usr/bin/env python3
"""
Upload Spring 2026 restaurant options CSV to Google Sheets as a new sheet
"""

import csv
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The ID of the spreadsheet
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get valid user credentials from storage or run OAuth flow."""
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
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

def create_new_sheet(service, spreadsheet_id, sheet_name):
    """Create a new sheet in the spreadsheet"""
    try:
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
        }
        
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        print(f"Created new sheet: {sheet_name} (ID: {sheet_id})")
        return sheet_id
        
    except HttpError as err:
        if 'already exists' in str(err):
            print(f"Sheet '{sheet_name}' already exists. Will update it instead.")
            return None
        else:
            raise

def upload_data_to_sheet(service, spreadsheet_id, sheet_name, data):
    """Upload data to the specified sheet"""
    try:
        # Clear existing data first
        range_name = f"{sheet_name}!A1:Z10000"
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        # Upload new data
        body = {
            'values': data
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Updated {result.get('updatedCells')} cells in sheet '{sheet_name}'")
        return result
        
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None

def main():
    """Main function to upload CSV to Google Sheets"""
    print("="*80)
    print("UPLOADING SPRING 2026 RESTAURANT OPTIONS TO GOOGLE SHEETS")
    print("="*80)
    
    # Get credentials
    print("\n1. Authenticating with Google...")
    creds = get_credentials()
    
    # Build the service
    service = build('sheets', 'v4', credentials=creds)
    
    # Read CSV data
    print("\n2. Reading CSV data...")
    csv_filename = 'spring_2026_intern_restaurant_options_with_overlaps.csv'
    data = read_csv_data(csv_filename)
    print(f"   Read {len(data)} rows from {csv_filename}")
    
    # Create new sheet
    print("\n3. Creating new sheet...")
    sheet_name = "Spring 2026 Restaurant Options"
    create_new_sheet(service, SPREADSHEET_ID, sheet_name)
    
    # Upload data
    print("\n4. Uploading data to Google Sheets...")
    result = upload_data_to_sheet(service, SPREADSHEET_ID, sheet_name, data)
    
    if result:
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"\nData uploaded to Google Sheets:")
        print(f"  Spreadsheet ID: {SPREADSHEET_ID}")
        print(f"  Sheet Name: {sheet_name}")
        print(f"  Rows uploaded: {len(data)}")
        print(f"\nView at: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    else:
        print("\nFailed to upload data")

if __name__ == '__main__':
    main()
