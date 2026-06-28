from google_sheets import get_sheet, get_setting
from datetime import datetime, timedelta

# Settings cache
settings_cache = None
services_cache = None


def get_next_stylist_token(stylist_name):

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Existing queue data
    rows = sheet.get_all_records()

    stylist_tokens = []

    for row in rows:

        if row["Stylist"] == stylist_name:

            try:
                stylist_tokens.append(int(row["Stylist Token"]))

            except:
                pass

    # Agar pehla token hai
    if len(stylist_tokens) == 0:
        return 1

    return max(stylist_tokens) + 1


# Check if online joining is allowed
def is_joining_allowed():

    close_time = get_setting("CLOSE_TIME")
    buffer_minutes = int(get_setting("BUFFER_MINUTES"))

    now = datetime.now()

    close_dt = datetime.strptime(close_time, "%H:%M")

    close_dt = now.replace(
        hour=close_dt.hour,
        minute=close_dt.minute,
        second=0,
        microsecond=0,
    )

    # Joining deadline
    join_deadline = close_dt - timedelta(minutes=buffer_minutes)

    print(f"NOW: {now}")
    print(f"CLOSE: {close_dt}")
    print(f"DEADLINE: {join_deadline}")
    print(f"ALLOWED: {now < join_deadline}")

    return now < join_deadline


def join_queue(customer_name, phone_number, stylist, service, customer_type):

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Queue data read karo
    rows = sheet.get_all_records()

    # Global Token
    global_token = len(rows) + 1

    # Stylist specific token
    stylist_token = get_next_stylist_token(stylist)

    # Default status
    status = "WAITING"

    # Walk-in customer aur stylist free hai
    if customer_type == "WALKIN" and not has_active_customer(stylist):
        status = "IN_PROGRESS"

    # Status decide karo
    if has_active_customer(stylist):
        status = "WAITING"

    else:
        status = "IN_PROGRESS"

    # New row add karo
    sheet.append_row(
        [
            global_token,
            customer_name,
            phone_number,
            stylist,
            stylist_token,
            service,
            customer_type,
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
    )

    return {
        "global_token": global_token,
        "stylist_token": stylist_token,
        "status": status,
    }


def get_service_time(service_name):

    # Services sheet kholo
    sheet = get_sheet("Services")

    rows = sheet.get_all_records()

    for row in rows:

        if row["Service"] == service_name:

            return int(row["Average Time"])

    return 20


def get_queue_info(stylist, stylist_token):

    sheet = get_sheet("Queue")

    rows = sheet.get_all_records()

    waiting_rows = []

    for row in rows:

        if row["Stylist"] == stylist and row["Status"] in ["WAITING", "IN_PROGRESS"]:

            waiting_rows.append(row)

    people_ahead = 0
    estimated_wait = 0

    for row in waiting_rows:

        row_token = int(row["Stylist Token"])

        if row_token < stylist_token:

            people_ahead += 1

            estimated_wait += get_service_time(row["Service"])

    return {"people_ahead": people_ahead, "estimated_wait": estimated_wait}


def is_customer_already_in_queue(phone_number):

    sheet = get_sheet("Queue")

    rows = sheet.get_all_records()

    for row in rows:

        if str(row["Phone Number"]) == str(phone_number) and row["Status"] == "WAITING":

            return True

    return False


def get_customer_queue_info(phone_number):

    sheet = get_sheet("Queue")

    rows = sheet.get_all_records()

    for row in rows:

        if str(row["Phone Number"]) == str(phone_number) and row["Status"] in [
            "WAITING",
            "IN_PROGRESS",
        ]:

            queue_info = get_queue_info(
                stylist=row["Stylist"], stylist_token=int(row["Stylist Token"])
            )

            return {
                "stylist": row["Stylist"],
                "service": row["Service"],
                "token": int(row["Stylist Token"]),
                "people_ahead": queue_info["people_ahead"],
                "estimated_wait": queue_info["estimated_wait"],
                "status": row["Status"],
            }

    return None


def is_queue_open():

    # Auto close based on shop closing time
    if should_auto_close_queue():

        return False

    sheet = get_sheet("Settings")
    rows = sheet.get_all_records()

    for row in rows:
        if row["Key"] == "Queue Status":
            return row["Value"].strip().upper() == "OPEN"

    return False


def can_join_queue(phone_number):

    # Check salon closing buffer
    if not is_joining_allowed():

        return {
            "allowed": False,
            "message": (
                "⚠️ Cannot Join Queue\n\n"
                "Salon is about to close.\n\n"
                "Please visit the salon directly."
            ),
        }

    # Check karo queue open hai ya nahi
    if not is_queue_open():

        return {"allowed": False, "message": ("Online queue abhi band hai.")}

    # Check karo customer pehle se queue me hai ya nahi
    if is_customer_already_in_queue(phone_number):

        return {"allowed": False, "message": ("Aap pehle se queue me hain.")}

    # Customer queue join kar sakta hai
    return {"allowed": True, "message": ""}


# Next customer ko complete karo
def complete_next_customer(stylist):

    second_waiting_row = None
    second_waiting_sheet_row = None

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Saari rows lao
    rows = sheet.get_all_records()

    # Google Sheet row numbering
    sheet_row_number = 2

    inprogress_row = None
    inprogress_sheet_row = None

    waiting_row = None
    waiting_sheet_row = None

    # =========================
    # IN_PROGRESS aur next WAITING dhundo
    # =========================
    for row in rows:
        # Current customer
        if row["Stylist"] == stylist and row["Status"] == "IN_PROGRESS":

            inprogress_row = row
            inprogress_sheet_row = sheet_row_number

        # First waiting customer
        elif (
            row["Stylist"] == stylist
            and row["Status"] == "WAITING"
            and waiting_row is None
        ):

            waiting_row = row
            waiting_sheet_row = sheet_row_number

        # Second waiting customer
        elif (
            row["Stylist"] == stylist
            and row["Status"] == "WAITING"
            and waiting_row is not None
            and second_waiting_row is None
        ):

            second_waiting_row = row
            second_waiting_sheet_row = sheet_row_number

        sheet_row_number += 1

    # =========================
    # Current customer complete karo
    # =========================
    if inprogress_row:

        sheet.update_cell(inprogress_sheet_row, 8, "COMPLETED")

        # Completed At
        sheet.update_cell(
            inprogress_sheet_row,
            11,  # Completed At column
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        )

    # =========================
    # Next waiting customer ko
    # IN_PROGRESS karo
    # =========================
    if waiting_row:

        sheet.update_cell(waiting_sheet_row, 8, "IN_PROGRESS")

        # Started At
        sheet.update_cell(
            waiting_sheet_row,
            10,  # Started At column
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        )

    # =========================
    # Kuch bhi active nahi tha
    # =========================
    if not inprogress_row and not waiting_row:

        return None

    # =========================
    # Result return karo
    # =========================
    return {
        "completed_customer": (
            inprogress_row["Customer Name"] if inprogress_row else None
        ),
        "next_customer": (waiting_row["Customer Name"] if waiting_row else None),
        "next_customer_type": (waiting_row["Customer Type"] if waiting_row else None),
        "next_customer_phone": (waiting_row["Phone Number"] if waiting_row else None),
        "second_customer": (
            second_waiting_row["Customer Name"] if second_waiting_row else None
        ),
        "second_customer_type": (
            second_waiting_row["Customer Type"] if second_waiting_row else None
        ),
        "second_customer_phone": (
            second_waiting_row["Phone Number"] if second_waiting_row else None
        ),
        "completed_customer_type": (
            inprogress_row["Customer Type"] if inprogress_row else None
        ),
        "completed_customer_phone": (
            inprogress_row["Phone Number"] if inprogress_row else None
        ),
        "completed_customer_token": (
            inprogress_row["Stylist Token"] if inprogress_row else None
        ),
        "next_customer_token": (waiting_row["Stylist Token"] if waiting_row else None),
    }


# Queue open karo
def open_queue():

    sheet = get_sheet("Settings")

    rows = sheet.get_all_records()

    row_number = 2

    for row in rows:

        if row["Key"] == "Queue Status":

            sheet.update_cell(row_number, 2, "OPEN")

            global settings_cache
            settings_cache = None

            return True

        row_number += 1

    return False


# Queue close karo
def close_queue():

    sheet = get_sheet("Settings")

    rows = sheet.get_all_records()

    row_number = 2

    for row in rows:

        if row["Key"] == "Queue Status":

            sheet.update_cell(row_number, 2, "CLOSED")

            global settings_cache
            settings_cache = None

            return True

        row_number += 1

    return False


# Customer queue leave kare
def leave_queue(phone_number):

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Saara data lao
    rows = sheet.get_all_records()

    # Google Sheet row numbering
    sheet_row_number = 2

    for row in rows:

        # Customer mila aur active queue me hai
        if str(row["Phone Number"]) == str(phone_number) and row["Status"] in [
            "WAITING",
            "IN_PROGRESS",
        ]:

            # Status update karo
            sheet.update_cell(sheet_row_number, 8, "CANCELLED")

            return {
                "phone": row["Phone Number"],
                "name": row["Customer Name"],
                "stylist": row["Stylist"],
                "token": row["Stylist Token"],
            }

        sheet_row_number += 1

    return None


# Stylist ka next waiting customer lao
def get_next_waiting_customer(stylist):

    sheet = get_sheet("Queue")

    rows = sheet.get_all_records()

    waiting_customer = None

    for row in rows:

        if row["Stylist"] == stylist and row["Status"] == "WAITING":

            waiting_customer = row
            break

    return waiting_customer


# Check karo stylist ke paas koi active customer hai ya nahi
def has_active_customer(stylist):

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Saara data lao
    rows = sheet.get_all_records()

    for row in rows:

        # Sirf same stylist dekho
        if row["Stylist"] != stylist:
            continue

        # Agar koi customer already active hai
        if row["Status"] in ["WAITING", "IN_PROGRESS"]:

            return True

    return False


def get_queue_summary(stylist):

    sheet = get_sheet("Queue")
    rows = sheet.get_all_records()

    in_progress = 0
    waiting = 0
    completed = 0
    cancelled = 0

    for row in rows:
        if row["Stylist"] != stylist:
            continue
        if row["Status"] == "IN_PROGRESS":
            in_progress += 1
        elif row["Status"] == "WAITING":
            waiting += 1
        elif row["Status"] == "COMPLETED":
            completed += 1
        elif row["Status"] == "CANCELLED":
            cancelled += 1

    return {
        "in_progress": in_progress,
        "waiting": waiting,
        "completed": completed,
        "cancelled": cancelled,
    }


def get_current_customer(stylist):

    sheet = get_sheet("Queue")
    rows = sheet.get_all_records()

    for row in rows:
        if row["Stylist"] == stylist and row["Status"] == "IN_PROGRESS":
            return {
                "name": row["Customer Name"],
                "token": row["Stylist Token"],
                "customer_type": row["Customer Type"],
            }

    return None


# Auto close queue after closing time
def should_auto_close_queue():

    close_time = get_setting("CLOSE_TIME")
    now = datetime.now()
    close_dt = datetime.strptime(close_time, "%H:%M")

    close_dt = now.replace(
        hour=close_dt.hour,
        minute=close_dt.minute,
        second=0,
        microsecond=0,
    )
    return now >= close_dt


# Get today's queue summary
def get_today_summary(stylist):

    sheet = get_sheet("Queue")
    rows = sheet.get_all_records()

    completed = 0
    cancelled = 0
    online = 0
    walkin = 0

    for row in rows:
        if row["Stylist"] != stylist:
            continue
        status = row["Status"]

        if row["Customer Type"] == "ONLINE":
            online += 1

        elif row["Customer Type"] == "WALKIN":
            walkin += 1

        if status == "COMPLETED":
            completed += 1

        elif status == "CANCELLED":
            cancelled += 1

    return {
        "completed": completed,
        "cancelled": cancelled,
        "online": online,
        "walkin": walkin,
    }


def update_customer_history(
    phone_number,
    customer_name,
    stylist,
):

    # Walk-in skip
    if phone_number == "-":
        return

    sheet = get_sheet("Customer History")
    rows = sheet.get_all_records()

    row_number = 2

    for row in rows:

        # Existing customer
        if str(row["Phone Number"]) == str(phone_number) and row["Stylist"] == stylist:

            total_visits = int(row["Total Visits"]) + 1

            sheet.update_cell(row_number, 3, total_visits)
            sheet.update_cell(row_number, 4, datetime.now().strftime("%d-%m-%Y"))
            sheet.update_cell(row_number, 5, stylist)

            return

        row_number += 1

    # New customer
    sheet.append_row(
        [
            phone_number,
            customer_name,
            1,
            datetime.now().strftime("%d-%m-%Y"),
            stylist,
        ]
    )


# Get all services
def get_services():

    global services_cache

    # Load services only once
    if services_cache is None:
        sheet = get_sheet("Services")
        services_cache = sheet.get_all_records()

    return services_cache


# Check if queue has active customers
def has_active_queue(stylist):

    sheet = get_sheet("Queue")
    rows = sheet.get_all_records()

    for row in rows:
        if row["Stylist"] == stylist and row["Status"] in ["WAITING", "IN_PROGRESS"]:

            return True

    return False
