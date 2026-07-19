from datetime import datetime, timedelta
from repository.service_repository import get_active_services, get_service_by_name
from repository.settings_repository import get_setting as db_get_setting, update_setting
from repository.queue_repository import (
    add_customer,
    complete_next_customer as db_complete_next_customer,
    get_active_queue,get_active_customer, cancel_customer, get_all_customers, get_waiting_queue, is_customer_completed_today, get_total_active_queue_count
)


# Check if online joining is allowed
def is_joining_allowed():

    close_time = db_get_setting("CLOSE_TIME")
    buffer_minutes = int(db_get_setting("BUFFER_MINUTES"))

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

    return now < join_deadline


def join_queue(customer_name, phone_number, stylist, service, customer_type):

    from repository.queue_repository import (
        get_next_global_token,
        get_next_stylist_token,
    )

    global_token = get_next_global_token()
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

    db_customer = add_customer(
        customer_name=customer_name,
        phone_number=phone_number,
        stylist=stylist,
        service=service,
        customer_type=customer_type,
        status=status,
        global_token=global_token,
        stylist_token=stylist_token,
    )

    return {
        "global_token": global_token,
        "stylist_token": stylist_token,
        "status": status,
    }


# Get service average time
def get_service_time(service_name):

    service = get_service_by_name(service_name)

    if not service:
        return 20

    return service.average_time


# Get queue information
def get_queue_info(stylist, stylist_token):

    waiting_rows = get_waiting_queue(stylist)
    people_ahead = 0
    estimated_wait = 0

    for customer in waiting_rows:
        if customer.stylist_token < stylist_token:
            people_ahead += 1
            estimated_wait += get_service_time(customer.service)

    return {
        "people_ahead": people_ahead,
        "estimated_wait": estimated_wait,
    }


# Check if customer is already in queue
def is_customer_already_in_queue(phone_number):

    customer = get_active_customer(phone_number)

    return customer is not None


# Get customer queue information
def get_customer_queue_info(phone_number):

    customer = get_active_customer(phone_number)

    if not customer:
        return None

    queue_info = get_queue_info(
        stylist=customer.stylist,
        stylist_token=customer.stylist_token,
    )

    return {
        "stylist": customer.stylist,
        "service": customer.service,
        "token": customer.stylist_token,
        "people_ahead": queue_info["people_ahead"],
        "estimated_wait": queue_info["estimated_wait"],
        "status": customer.status,
    }


# Check if queue is open
def is_queue_open():

    # Auto close based on shop closing time
    if should_auto_close_queue():
        return False

    return db_get_setting("QUEUE_STATUS") == "OPEN"


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

    # Check if customer already completed today's service
    if is_customer_completed_today(phone_number):

        return {
            "allowed": False,
            "message": (
                "Aap aaj already service le chuke hain\n\n"
                "Agar aapko dubara service leni hain toh direct saloon visit kijiye."
            ),
        }

    # Customer queue join kar sakta hai
    return {"allowed": True, "message": ""}


# Next customer ko complete karo
def complete_next_customer(stylist):

    # Complete current customer and start next customer
    completed_customer, next_customer = db_complete_next_customer(stylist)

    # Active queue after update
    active_queue = get_active_queue(stylist)

    second_customer = None

    if len(active_queue) >= 2:
        second_customer = active_queue[1]

    return {
        "completed_customer": (
            completed_customer.customer_name if completed_customer else None
        ),
        "completed_customer_phone": (
            completed_customer.phone_number if completed_customer else None
        ),
        "completed_customer_type": (
            completed_customer.customer_type if completed_customer else None
        ),
        "next_customer": (next_customer.customer_name if next_customer else None),
        "next_customer_phone": (next_customer.phone_number if next_customer else None),
        "next_customer_type": (next_customer.customer_type if next_customer else None),
        "second_customer": (second_customer.customer_name if second_customer else None),
        "second_customer_phone": (
            second_customer.phone_number if second_customer else None
        ),
        "second_customer_type": (
            second_customer.customer_type if second_customer else None
        ),
        "completed_customer_token": (
            completed_customer.stylist_token if completed_customer else None
        ),
        "next_customer_token": (next_customer.stylist_token if next_customer else None),
        "second_customer_token": (
            second_customer.stylist_token if second_customer else None
        ),
    }


# Open queue
def open_queue():

    if update_setting("QUEUE_STATUS", "OPEN"):

        # sync_all_settings()

        return True

    return False


# Close queue
def close_queue():

    if update_setting("QUEUE_STATUS", "CLOSED"):

        # sync_all_settings()

        return True

    return False

# Customer leave queue
def leave_queue(phone_number):

    # Get active customer from database
    customer = get_active_customer(phone_number)

    if not customer:
        return False

    # Update database
    customer = cancel_customer(customer.id)

    return {
        "phone": customer.phone_number,
        "name": customer.customer_name,
        "stylist": customer.stylist,
        "token": customer.stylist_token,
    }


# Check if stylist has any active customers
def has_active_customer(stylist):

    active_queue = get_active_queue(stylist)

    return len(active_queue) > 0


# Get queue summary
def get_queue_summary(stylist):

    customers = get_all_customers(stylist)

    in_progress = 0
    waiting = 0
    completed = 0
    cancelled = 0

    for customer in customers:

        if customer.status == "IN_PROGRESS":
            in_progress += 1
        elif customer.status == "WAITING":
            waiting += 1
        elif customer.status == "COMPLETED":
            completed += 1
        elif customer.status == "CANCELLED":
            cancelled += 1

    return {
        "in_progress": in_progress,
        "waiting": waiting,
        "completed": completed,
        "cancelled": cancelled,
    }


# Auto close queue after closing time
def should_auto_close_queue():

    close_time = db_get_setting("CLOSE_TIME")
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

    customers = get_all_customers(stylist)

    completed = 0
    cancelled = 0
    online = 0
    walkin = 0

    for customer in customers:
        if customer.customer_type == "ONLINE":
            online += 1
        elif customer.customer_type == "WALKIN":
            walkin += 1
        if customer.status == "COMPLETED":
            completed += 1
        elif customer.status == "CANCELLED":
            cancelled += 1

    return {
        "completed": completed,
        "cancelled": cancelled,
        "online": online,
        "walkin": walkin,
    }


# Get all services
def get_services():

    services = get_active_services()

    return [
        {
            "Service": service.name,
            "Price": service.price,
            "Average Time": service.average_time,
        }
        for service in services
    ]

def get_total_queue_count():
    return get_total_active_queue_count()