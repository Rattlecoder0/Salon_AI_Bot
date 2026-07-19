from repository.admin_repository import (
    get_admin_by_phone,
    get_admin_by_name,
)
from repository.queue_repository import get_walkin_count
from threading import Lock

admins_cache = None
admin_locks = {}

# Get admin information
def get_admin_info(phone_number):

    admin = get_admin_by_phone(phone_number)

    if not admin:
        return None

    return {
        "name": admin.name,
        "role": admin.role,
    }


def is_admin(phone_number):

    return get_admin_by_phone(phone_number) is not None


# Get next walk-in customer name
def get_next_walkin_name():

    walkin_count = get_walkin_count()

    return f"Walk-In {walkin_count + 1}"


# Stylist ka admin number lao
def get_admin_number_by_name(name):

    admin = get_admin_by_name(name)

    if admin:
        return admin.phone_number

    return None

def acquire_admin_lock(phone_number):

    if phone_number not in admin_locks:
        admin_locks[phone_number] = Lock()

    return admin_locks[phone_number].acquire(blocking=False)


def release_admin_lock(phone_number):

    if phone_number in admin_locks:
        admin_locks[phone_number].release()