from admin_service import get_admin_number_by_stylist
from whatsapp import send_whatsapp_message
from states import get_state, set_state
from google_sheets import get_active_staff
from customer_data import get_customer_data, set_customer_data
from queue_service import (
    can_join_queue,
    join_queue,
    get_customer_queue_info,
    is_customer_already_in_queue,
    is_queue_open,
    leave_queue,
    is_joining_allowed,
    get_services
)
from admin_service import is_admin  # Admin detection ke liye
from admin_flow import handle_admin_message  # Admin flow handler
from logger_config import log_event


def handle_message(user_number, user_message):

    # User ki current conversation state
    current_state = get_state(user_number)
    print(f"Current State: {current_state}")

    # ==================================
    # ADMIN ROUTING
    # ==================================

    # Check karo user admin hai ya nahi
    if is_admin(user_number):
        print("ADMIN DETECTED")

        handle_admin_message(user_number, user_message)
        return

    # =========================
    # START STATE
    # =========================
    if current_state == "START":

        # Fallback:
        # Agar state reset ho jaye (server restart/reload),
        # tab bhi customer queue leave kar sake.
        if (
            user_message == "1"
            and is_customer_already_in_queue(user_number)
        ):

            left_customer = leave_queue(user_number)

            if left_customer:
                log_event(
                    "CUSTOMER_LEFT_QUEUE",
                    PHONE=left_customer["phone"],
                    NAME=left_customer["name"],
                    STYLIST=left_customer["stylist"],
                    TOKEN=left_customer["token"],
                )

            send_whatsapp_message(
                user_number,
                "Queue Left ✅\n\n"
                "Aapko queue se remove kar diya gaya hai."
            )

            return        

        # Customer already queue me hai
        if is_customer_already_in_queue(user_number):

            info = get_customer_queue_info(user_number)

            # Customer is not in queue anymore
            if not info:
                send_whatsapp_message(
                    user_number,
                    "❌ You are not in any active queue."
                )
                set_state(user_number, "START")

                return

            send_whatsapp_message(
                user_number,
                f"Aap queue me hain ✅\n\n"
                f"Stylist: {info['stylist']}\n"
                f"Token: #{info['token']}\n"
                f"People Ahead: {info['people_ahead']}\n"
                f"Estimated Wait: {info['estimated_wait']} min\n\n"
                f"1. Leave Queue"
            )

            return

        # Check karo online queue open hai ya nahi
        if not is_queue_open():

            send_whatsapp_message(
                user_number,
                "Welcome to Adarsh Hair Salon 👋\n\n"
                "⚠️ Online Queue Closed\n\n"
                "1. Price List\n"
                "2. Working Hours",
            )

            set_state(user_number, "MAIN_MENU_CLOSED")

            return

        # Queue open hai
        send_whatsapp_message(
            user_number,
            "Welcome to Adarsh Hair Salon 👋\n\n"
            "1. Join Queue\n"
            "2. Price List\n"
            "3. Working Hours",
        )

        set_state(user_number, "MAIN_MENU")

        return

    # =========================
    # MAIN MENU
    # =========================
    if current_state == "MAIN_MENU":
        print("MAIN MENU ENTERED")
        print(f"Message = {user_message}")

        if user_message == "1":

            # Check if online joining is allowed
            if not is_joining_allowed():

                send_whatsapp_message(
                    user_number,
                    "⚠️ Cannot Join Queue\n\n"
                    "Salon is about to close.\n\n"
                    "Please visit the salon directly."
                )

                return

            send_whatsapp_message(
                user_number,
                "Select Service ✂️\n\n" "1. Haircut\n" "2. Beard\n" "3. Hair Spa",
            )

            set_state(user_number, "WAITING_FOR_SERVICE")
            return

        # =========================
        # PRICE LIST
        # =========================
        if user_message == "2":

            services = get_services()

            message = "💈 Price List\n\n"

            for service in services:

                message += (
                    f"{service['Service']} - ₹{service['Price']}\n"
                )

            send_whatsapp_message(user_number, message)

            return

        elif user_message == "3":

            send_whatsapp_message(user_number, "Working Hours 🕒\n\n" "10 AM - 8 PM")

            return

        else:

            send_whatsapp_message(user_number, "Please select 1, 2 or 3.")

            return

    # =========================
    # MAIN MENU CLOSED
    # =========================
    if current_state == "MAIN_MENU_CLOSED":

        # Agar queue reopen ho gayi hai
        if is_queue_open():

            set_state(user_number, "START")

            handle_message(user_number, user_message)

            return

        # =========================
        # PRICE LIST
        # =========================
        if user_message == "1":
            services = get_services()
            message = "💈 Price List\n\n"

            for service in services:
                message += (
                    f"{service['Service']} - ₹{service['Price']}\n"
                )

            send_whatsapp_message(user_number, message)

            return

        elif user_message == "2":

            send_whatsapp_message(user_number, "Working Hours 🕒\n\n" "10 AM - 8 PM")

            return

        else:

            send_whatsapp_message(user_number, "Please select 1 or 2.")

            return

    # =========================
    # IN QUEUE
    # =========================
    if current_state == "IN_QUEUE":
        print("🔥 IN_QUEUE BLOCK ENTERED 🔥")
        # Customer queue leave karna chahta hai
        if user_message == "1":

            left_customer = leave_queue(user_number)

            if left_customer:
                log_event(
                    "CUSTOMER_LEFT_QUEUE",
                    PHONE=left_customer["phone"],
                    NAME=left_customer["name"],
                    STYLIST=left_customer["stylist"],
                    TOKEN=left_customer["token"],
                )
            else:
                log_event(
                    "CUSTOMER_LEAVE_FAILED",
                    level="WARNING",
                    PHONE=user_number,
                )

            send_whatsapp_message(
                user_number,
                "Queue Left ✅\n\n" "Aapko queue se remove kar diya gaya hai.",
            )

            set_state(user_number, "START")

            return

        info = get_customer_queue_info(user_number)
        
        # Customer is not in queue anymore
        if not info:
            send_whatsapp_message(
                user_number,
                "❌ You are not in any active queue."
            )
            set_state(user_number, "START")

            return

        send_whatsapp_message(
            user_number,
            f"Aap queue me hain ✅\n\n"
            f"Stylist: {info['stylist']}\n"
            f"Token: #{info['token']}\n"
            f"People Ahead: {info['people_ahead']}\n"
            f"Estimated Wait: {info['estimated_wait']} min\n\n"
            f"1. Leave Queue",
        )

        return

    # =========================
    # SERVICE SELECTION
    # =========================
    if current_state == "WAITING_FOR_SERVICE":

        service_map = {"1": "Haircut", "2": "Beard", "3": "Hair Spa"}

        service = service_map.get(user_message)

        if not service:

            send_whatsapp_message(user_number, "Please select 1, 2 or 3.")
            return

        # Service save karo
        set_customer_data(user_number, "service", service)

        # Active staff Google Sheet se lao
        staff_list = get_active_staff()

        staff_message = "Select Stylist ✂️\n\n"

        for index, staff_name in enumerate(staff_list, start=1):
            staff_message += f"{index}. {staff_name}\n"

        send_whatsapp_message(user_number, staff_message)

        set_state(user_number, "WAITING_FOR_STAFF")

        return

    # =========================
    # STAFF SELECTION
    # =========================
    if current_state == "WAITING_FOR_STAFF":

        staff_list = get_active_staff()

        try:

            selected_index = int(user_message) - 1

            selected_staff = staff_list[selected_index]

        except:

            send_whatsapp_message(user_number, "Please select a valid stylist number.")

            return

        # Selected stylist save karo
        set_customer_data(user_number, "staff", selected_staff)

        send_whatsapp_message(
            user_number, f"{selected_staff} selected ✅\n\n" "Aapka naam kya hai?"
        )

        set_state(user_number, "WAITING_FOR_NAME")

        return

    # =========================
    # NAME COLLECTION
    # =========================
    if current_state == "WAITING_FOR_NAME":

        # Customer ka naam save karo
        set_customer_data(user_number, "name", user_message)

        # Customer data lao
        data = get_customer_data(user_number)

        # Check karo queue join kar sakta hai ya nahi
        queue_check = can_join_queue(user_number)

        # Queue join allowed nahi hai
        if not queue_check["allowed"]:

            # Agar customer pehle se queue me hai
            if is_customer_already_in_queue(user_number):

                info = get_customer_queue_info(user_number)

                # Customer is not in queue anymore
                if not info:

                    send_whatsapp_message(
                        user_number,
                        "❌ You are not in any active queue."
                    )

                    set_state(user_number, "START")

                    return                

                send_whatsapp_message(
                    user_number,
                    f"Aap pehle se queue me hain ✅\n\n"
                    f"Stylist: {info['stylist']}\n"
                    f"Token: #{info['token']}\n"
                    f"People Ahead: {info['people_ahead']}\n"
                    f"Estimated Wait: {info['estimated_wait']} min",
                )
                return

            # Queue band hai ya koi aur reason
            send_whatsapp_message(user_number, queue_check["message"])
            return

        # Customer ko queue me add karo
        result = join_queue(
            customer_name=data["name"],
            phone_number=user_number,
            stylist=data["staff"],
            service=data["service"],
            customer_type="ONLINE",
        )

        log_event(
            "CUSTOMER_JOINED",
            PHONE=user_number,
            NAME=data["name"],
            STYLIST=data["staff"],
            TOKEN=result["stylist_token"],
            SERVICE=data["service"],
            TYPE="ONLINE",
        )

        # Queue details lao
        info = get_customer_queue_info(user_number)

        # Customer is not in queue anymore
        if not info:
            send_whatsapp_message(
                user_number,
                "❌ You are not in any active queue."
            )
            set_state(user_number, "START")

            return        

        # Customer ko token details bhejo
        send_whatsapp_message(
            user_number,
            f"Queue Joined ✅\n\n"
            f"Stylist: {info['stylist']}\n"
            f"Token: #{info['token']}\n"
            f"People Ahead: {info['people_ahead']}\n"
            f"Estimated Wait: {info['estimated_wait']} min",
        )

        # =========================
        # Admin Notification
        # =========================
        admin_number = get_admin_number_by_stylist(
            data["staff"]
        )

        print(f"ADMIN NUMBER FOUND: {admin_number}")

        if admin_number:
            send_whatsapp_message(
                admin_number,
                f"🔔 New Online Customer\n\n"
                f"Name: {data['name']}\n"
                f"Service: {data['service']}\n"
                f"Token: #{info['token']}"
            )        

        # =========================
        # Customer Reminder
        # =========================
        if result["status"] == "IN_PROGRESS":
            send_whatsapp_message(
                user_number,
                "⚡ Aapka pehla number hai.\n\n"
                "Kripya salon ki taraf nikal jaiye."
            )

        elif info["people_ahead"] == 1:
            send_whatsapp_message(
                user_number,
                "⚡ Agla aapka number hai.\n\n"
                "Kripya salon ki taraf nikal jaiye."
            )

        # Customer queue me hai
        set_state(user_number, "IN_QUEUE")
        print("SETTING STATE TO IN_QUEUE")

        print(f"STATE AFTER SET: {get_state(user_number)}")

        return
