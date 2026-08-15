#!/usr/bin/env python3
"""
Google Sheets API Reader
Reads data from Google Sheets using the Google Sheets API
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of the spreadsheet
SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
SHEET_GID = '977712289'

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
            if not os.path.exists('credentials.json'):
                print("ERROR: credentials.json not found!")
                print("Please follow the setup instructions to create credentials.json")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def read_google_sheet(spreadsheet_id, range_name='Sheet1'):
    """
    Read data from a Google Sheet
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation of the range to retrieve
    
    Returns:
        List of rows from the sheet
    """
    try:
        creds = get_credentials()
        if not creds:
            return None
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return None
        
        return values
        
    except HttpError as err:
        print(f'An error occurred: {err}')
        return None

def get_sheet_names(spreadsheet_id):
    """Get all sheet names from the spreadsheet"""
    try:
        creds = get_credentials()
        if not creds:
            return None
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = sheet_metadata.get('sheets', [])
        sheet_names = []
        
        for sheet in sheets:
            title = sheet.get('properties', {}).get('title', '')
            gid = sheet.get('properties', {}).get('sheetId', '')
            sheet_names.append({
                'title': title,
                'gid': str(gid)
            })
        
        return sheet_names
        
    except HttpError as err:
        print(f'An error occurred: {err}')
        return None

def main():
    """Main function to read the Google Sheet"""
    print("="*80)
    print("GOOGLE SHEETS API READER")
    print("="*80)
    
    # Get all sheet names
    print("\n1. Getting sheet names...")
    sheet_names = get_sheet_names(SPREADSHEET_ID)
    
    if sheet_names:
        print(f"Found {len(sheet_names)} sheets:")
        for sheet in sheet_names:
            marker = " <-- TARGET" if sheet['gid'] == SHEET_GID else ""
            print(f"  - {sheet['title']} (GID: {sheet['gid']}){marker}")
        
        # Find the target sheet name
        target_sheet = None
        for sheet in sheet_names:
            if sheet['gid'] == SHEET_GID:
                target_sheet = sheet['title']
                break
        
        if target_sheet:
            print(f"\n2. Reading data from sheet: {target_sheet}")
            values = read_google_sheet(SPREADSHEET_ID, target_sheet)
            
            if values:
                print(f"\nFound {len(values)} rows")
                print(f"\nFirst 5 rows:")
                for i, row in enumerate(values[:5]):
                    print(f"  Row {i+1}: {row}")
                
                # Save to CSV
                import csv
                csv_filename = f'google_sheet_data_{SHEET_GID}.csv'
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(values)
                
                print(f"\n3. Saved data to: {csv_filename}")
                return values
        else:
            print(f"\nERROR: Could not find sheet with GID {SHEET_GID}")
    else:
        print("ERROR: Could not retrieve sheet names")
    
    return None

if __name__ == '__main__':
    main()
