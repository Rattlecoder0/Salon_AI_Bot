from google_sheets import get_sheet


# ====================================
# Find History Row
# ====================================
def find_history_row(phone_number, stylist):

    sheet = get_sheet("Customer History")
    rows = sheet.get_all_records()
    row_number = 2

    for row in rows:
        if (
            str(row["Phone Number"]) == str(phone_number)
            and row["Stylist"] == stylist
        ):
            return row_number
        row_number += 1

    return None

# ====================================
# Update History Sheet Row
# ====================================
def update_history_sheet_row(customer):

    row = find_history_row(
        customer.phone_number,
        customer.stylist,
    )
    if not row:

        sync_new_customer_history(customer)
        return

    sheet = get_sheet("Customer History")

    sheet.update_cell(row, 3, customer.total_visits)
    sheet.update_cell(row, 4, customer.last_visit)

# ====================================
# Sync Customer History
# ====================================
def sync_customer_history(customer):
    update_history_sheet_row(customer)

# ====================================
# Sync New Customer History
# ====================================
def sync_new_customer_history(customer):
    sheet = get_sheet("Customer History")

    sheet.append_row(
        [
            customer.phone_number,
            customer.customer_name,
            customer.total_visits,
            customer.last_visit,
            customer.stylist,
        ]
    )