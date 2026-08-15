#!/usr/bin/env python3
"""
Upload Spring 2026 matching results to a NEW Google Sheet
"""

import csv
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def create_new_spreadsheet(service, title, data):
    """Create a new Google Spreadsheet with data"""
    try:
        # Create the spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [{
                'properties': {
                    'title': 'Intern to Restaurant Matches',
                    'gridProperties': {
                        'frozenRowCount': 1  # Freeze header row
                    }
                }
            }]
        }
        
        spreadsheet = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')
        
        print(f"Created new spreadsheet: {title}")
        print(f"   ID: {spreadsheet_id}")
        print(f"   URL: {spreadsheet_url}")
        
        # Add data to the sheet
        body = {
            'values': data
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Intern to Restaurant Matches!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"\nUploaded {result.get('updatedCells')} cells")
        
        # Format the header row (bold)
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        print(f"Formatted header row")
        
        return spreadsheet_id, spreadsheet_url
        
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None, None

def main():
    """Main function"""
    print("="*80)
    print("UPLOADING SPRING 2026 MATCHING RESULTS TO GOOGLE SHEETS")
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
    
    # Create new spreadsheet
    print("\n3. Creating new Google Sheet...")
    title = "Spring 2026 Intern Restaurant Matches"
    spreadsheet_id, spreadsheet_url = create_new_spreadsheet(service, title, data)
    
    if spreadsheet_id:
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"\nYour Spring 2026 matching results have been uploaded!")
        print(f"\nView your spreadsheet:")
        print(f"   {spreadsheet_url}")
        print(f"\nYou can now:")
        print(f"   - Share this spreadsheet with others")
        print(f"   - Copy data to the original spreadsheet if you have edit access")
        print(f"   - Download as Excel or other formats")
    else:
        print("\nFailed to create spreadsheet")

if __name__ == '__main__':
    main()
