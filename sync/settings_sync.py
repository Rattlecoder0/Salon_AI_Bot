from google_sheets import get_sheet
from repository.settings_repository import get_setting, get_all_settings

# ====================================
# Find Setting Row
# ====================================
def find_setting_row(key):

    sheet = get_sheet("Settings")

    rows = sheet.get_all_records()

    row_number = 2

    for row in rows:

        if row["Key"] == key:
            return row_number

        row_number += 1

    return None

# ====================================
# Sync Setting
# ====================================
def sync_setting(setting):

    update_setting_sheet_row(
        setting.key,
        setting.value,
    )

# ====================================
# Update Setting Sheet Row
# ====================================
def update_setting_sheet_row(key, value):

    row = find_setting_row(key)    
    if not row:
        return

    sheet = get_sheet("Settings")

    sheet.update_cell(row, 2, value)

# ====================================
# Sync All Settings
# ====================================
def sync_all_settings():
    settings = get_all_settings()

    for setting in settings:        

        update_setting_sheet_row(
            setting.key,
            setting.value,
        )