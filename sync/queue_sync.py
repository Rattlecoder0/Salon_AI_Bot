from google_sheets import get_sheet


# ====================================
# Sync New Customer
# ====================================
def sync_new_customer(customer):

    sheet = get_sheet("Queue")

    sheet.append_row(
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
            (
                customer.started_at.strftime("%Y-%m-%d %H:%M:%S")
                if customer.started_at
                else ""
            ),
            (
                customer.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if customer.completed_at
                else ""
            ),
            customer.id,
        ]
    )

# ====================================
# Find Sheet Row By DB ID
# ====================================
def find_sheet_row(db_id):

    sheet = get_sheet("Queue")

    db_ids = sheet.col_values(12)

    for index, value in enumerate(db_ids[1:], start=2):

        if str(value) == str(db_id):
            return index

    return None

# ====================================
# Update Queue Row
# ====================================
def update_queue_sheet_row(customer):

    sheet = get_sheet("Queue")

    row = find_sheet_row(customer.id)

    if not row:
        return

    sheet.update_cell(row, 8, customer.status)

    sheet.update_cell(
        row,
        10,
        customer.started_at.strftime("%Y-%m-%d %H:%M:%S")
        if customer.started_at
        else "",
    )

    sheet.update_cell(
        row,
        11,
        customer.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        if customer.completed_at
        else "",
    )


# ====================================
# Sync Queue Row
# ====================================
def sync_queue_row(customer):

    row = find_sheet_row(customer.id)

    # Self-healing
    if not row:
        sync_new_customer(customer)
        return

    sheet = get_sheet("Queue")

    sheet.update(
        f"A{row}:L{row}",
        [[
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
            if customer.started_at else "",
            customer.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            if customer.completed_at else "",
            customer.id,
        ]]
    )