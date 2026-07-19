from google_sheets import get_sheet
from repository.service_repository import get_active_services


# ====================================
# Sync All Services
# ====================================
def sync_all_services():

    sheet = get_sheet("Services")

    services = get_active_services()

    # Clear all rows except header
    sheet.resize(rows=1)

    rows = []

    for service in services:

        rows.append(
            [
                service.name,
                service.average_time,
                service.price,
            ]
        )

    if rows:

        sheet.append_rows(rows)