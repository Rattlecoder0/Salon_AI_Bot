from repository.staff_repository import get_active_staff_members


# ====================================
# Get Active Staff
# ====================================
def get_active_staff():

    staff_members = get_active_staff_members()

    return [
        staff.name
        for staff in staff_members
    ]