import gspread
from google.oauth2.service_account import Credentials
from repository.staff_repository import get_active_staff_members

# Google API permissions
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Load credentials only once
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scopes,
)

# Create client only once
client = gspread.authorize(creds)

# Open spreadsheet only once
spreadsheet = client.open("Salon Bot Data")

# Worksheet cache
sheet_cache = {}


# Get worksheet
def get_sheet(sheet_name):

    # Return cached worksheet
    if sheet_name in sheet_cache:
        return sheet_cache[sheet_name]

    # Load worksheet first time
    worksheet = spreadsheet.worksheet(sheet_name)
    sheet_cache[sheet_name] = worksheet

    return worksheet