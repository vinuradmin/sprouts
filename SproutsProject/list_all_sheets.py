#!/usr/bin/env python3
"""
List all sheets in the Google Sheets document
"""

from google_sheets_reader import get_sheet_names, SPREADSHEET_ID

print("="*80)
print("ALL SHEETS IN GOOGLE SHEETS DOCUMENT")
print("="*80)

sheets = get_sheet_names(SPREADSHEET_ID)

if sheets:
    print(f"\nFound {len(sheets)} sheets:\n")
    for i, sheet in enumerate(sheets):
        marker = " <-- TARGET (GID 977712289)" if sheet['gid'] == '977712289' else ""
        print(f"  {i+1}. {sheet['title']}")
        print(f"     GID: {sheet['gid']}{marker}")
        print()
else:
    print("No sheets found")
