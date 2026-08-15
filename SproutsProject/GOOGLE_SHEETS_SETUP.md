# Google Sheets API Setup Instructions

Follow these steps to set up Google Sheets API access for reading your spreadsheet.

## Step 1: Install Required Libraries

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Create Google Cloud Project and Enable API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (App name, User support email, Developer contact)
   - Add your email as a test user
   - Save and continue
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Google Sheets Reader" (or any name)
   - Click "Create"
5. Download the credentials:
   - Click the download icon (⬇) next to your newly created OAuth client
   - Save the file as `credentials.json` in the SproutsProject directory

## Step 4: Place credentials.json

Make sure `credentials.json` is in the same directory as `google_sheets_reader.py`:

```
SproutsProject/
├── google_sheets_reader.py
└── credentials.json  <-- Place it here
```

## Step 5: Run the Script

```bash
cd c:/Users/pierr/CascadeProjects/windsurf-project/SproutsProject
python google_sheets_reader.py
```

### First Run:
- A browser window will open
- Sign in with your Google account
- Grant permission to access Google Sheets
- The script will save a `token.pickle` file for future use

### Subsequent Runs:
- The script will use the saved token
- No browser authentication needed

## What the Script Does

1. Authenticates with Google Sheets API
2. Reads your spreadsheet: `1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M`
3. Finds the sheet with GID: `977712289`
4. Downloads all data from that sheet
5. Saves it as a CSV file: `google_sheet_data_977712289.csv`
6. Displays the first 5 rows in the console

## Troubleshooting

### Error: "credentials.json not found"
- Make sure you downloaded the OAuth credentials
- Rename the file to exactly `credentials.json`
- Place it in the SproutsProject directory

### Error: "Access blocked"
- Make sure you added yourself as a test user in the OAuth consent screen
- The app must be in "Testing" mode to work with external users

### Error: "Invalid grant"
- Delete `token.pickle`
- Run the script again to re-authenticate

### Error: "Permission denied"
- Make sure the Google account you're using has access to the spreadsheet
- Check the spreadsheet sharing settings

## Files Created

After running the script, you'll have:
- `token.pickle` - Stores your authentication token (don't share this!)
- `google_sheet_data_977712289.csv` - The downloaded spreadsheet data

## Security Notes

- Keep `credentials.json` and `token.pickle` private
- Add them to `.gitignore` if using version control
- Never commit these files to a public repository

## Next Steps

Once the data is downloaded as CSV, you can:
- Analyze it with pandas
- Import it into your database
- Process it with your existing scripts
- Use it for the Sprouts intern matching algorithm
