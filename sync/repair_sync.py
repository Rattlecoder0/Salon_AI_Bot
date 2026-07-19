from constants import HISTORY_CLEAR_RANGE, QUEUE_CLEAR_RANGE, SERVICES_CLEAR_RANGE, SETTINGS_CLEAR_RANGE
from google_sheets import get_sheet
from repository.customer_history_repository import get_all_customer_history
from repository.queue_repository import get_all_queue
from repository.service_repository import get_all_services
from repository.settings_repository import get_all_settings

# ====================================
# Rebuild Sheet
# ====================================
def rebuild_sheet(
    sheet_name,
    clear_range,
    rows,
):

    sheet = get_sheet(sheet_name)

    sheet.batch_clear(
        [f"{clear_range}{sheet.row_count}"]
    )

    if rows:

        sheet.append_rows(
            rows,
            value_input_option="USER_ENTERED",
        )

# ====================================
# Repair Queue Sheet
# ====================================
def repair_queue_sheet():

    customers = get_all_queue()
    rows = []

    for customer in customers:

        rows.append(
            [
                customer.global_token,
                customer.customer_name,
                customer.phone_number,
                customer.stylist,
                customer.stylist_token,
                customer.service,
                customer.customer_type,
                customer.status,
                customer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                customer.started_at.strftime("%Y-%m-%d %H:%M:%S")
                if customer.started_at
                else "",
                customer.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if customer.completed_at
                else "",
                customer.id,
            ]
        )

    rebuild_sheet(
        "Queue",
        QUEUE_CLEAR_RANGE,
        rows,
    )

    print("✅ Queue repaired")

# ====================================
# Repair Customer History Sheet
# ====================================
def repair_customer_history_sheet():

    customers = get_all_customer_history()
    rows = []

    for customer in customers:

        rows.append(
            [
                customer.phone_number,
                customer.customer_name,
                customer.total_visits,
                customer.last_visit,
                customer.stylist,
            ]
        )

    rebuild_sheet(
        "Customer History",
        HISTORY_CLEAR_RANGE,
        rows,
    )

    print("✅ Customer History repaired")

# ====================================
# Repair Services Sheet
# ====================================
def repair_services_sheet():

    services = get_all_services()
    rows = []

    for service in services:

        rows.append(
            [
                service.name,
                service.average_time,
                service.price,
            ]
        )

    rebuild_sheet(
        "Services",
        SERVICES_CLEAR_RANGE,
        rows,
    )

    print("✅ Services repaired")

# ====================================
# Repair Settings Sheet
# ====================================
def repair_settings_sheet():

    settings = get_all_settings()
    rows = []

    for setting in settings:

        rows.append(
            [
                setting.key,
                setting.value,
            ]
        )

    rebuild_sheet(
        "Settings",
        SETTINGS_CLEAR_RANGE,
        rows,
    )

    print("✅ Settings repaired")


# ====================================
# Repair All Sheets
# ====================================
def repair_all():

    repair_queue_sheet()

    repair_customer_history_sheet()

    repair_services_sheet()

    repair_settings_sheet()

    print("🎉 All sheets repaired successfully")


if __name__ == "__main__":

    repair_all()