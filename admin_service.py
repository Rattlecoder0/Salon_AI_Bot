from google_sheets import get_sheet

admins_cache = None

# Get admin information
def get_admin_info(phone_number):

    global admins_cache

    # Load admins only once
    if admins_cache is None:

        sheet = get_sheet("Admins")
        admins_cache = sheet.get_all_records()

    # Find matching admin
    for row in admins_cache:

        if str(row["Phone Number"]) == str(phone_number):

            return {
                "name": row["Name"],
                "role": row["Role"],
                "stylist": row["Stylist"],
            }

    return None


def is_admin(phone_number):

    # Phone number se admin details check karo
    admin = get_admin_info(phone_number)

    # Agar admin exist karta hai
    if admin:
        return True

    # Nahi mila to normal customer
    return False


def get_next_walkin_name():

    # Queue sheet kholo
    sheet = get_sheet("Queue")

    # Saara queue data lao
    rows = sheet.get_all_records()

    walkin_count = 0

    # Existing walk-in customers count karo
    for row in rows:

        if row["Customer Type"] == "WALKIN":

            walkin_count += 1

    # Next walk-in name return karo
    return f"Walk-In {walkin_count + 1}"


# Stylist ka admin number lao
def get_admin_number_by_stylist(stylist):
    sheet = get_sheet("Admins")
    rows = sheet.get_all_records()

    for row in rows:
        if row["Stylist"] == stylist:
            return str(row["Phone Number"])

    return None
