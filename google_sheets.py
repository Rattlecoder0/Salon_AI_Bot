import gspread
from google.oauth2.service_account import Credentials

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


def get_active_staff():

    # Staff worksheet kholo
    sheet = get_sheet("Staff")

    # Saare records read karo
    rows = sheet.get_all_records()

    active_staff = []

    for row in rows:

        # Sirf active staff add karo
        if row["Active"].strip().lower() == "yes":
            active_staff.append(row["Name"])

    return active_staff


def save_booking(customer_name, phone_number, service, stylist, date="", time=""):

    # Open bookings sheet
    sheet = get_sheet("Bookings")

    # Add new row
    sheet.append_row([customer_name, phone_number, service, stylist, date, time])


# Settings cache
settings_cache = None


# Get setting value
def get_setting(setting_name):

    global settings_cache

    # Load settings only once
    if settings_cache is None:

        sheet = get_sheet("Settings")
        settings_cache = sheet.get_all_records()

    # Search in cache
    for row in settings_cache:

        if row["Key"] == setting_name:
            return row["Value"]

    return None
