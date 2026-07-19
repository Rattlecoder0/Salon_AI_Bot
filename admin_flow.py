from services.notification_service import notify_queue_progress
from whatsapp import send_whatsapp_message
from admin_service import get_admin_info, get_next_walkin_name
from logger_config import log_event
from queue_service import (
    has_active_customer,
    join_queue,
    complete_next_customer,
    is_queue_open,
    open_queue,
    close_queue,
    get_queue_summary,
    should_auto_close_queue,
    get_today_summary,
)
from services.history_service import update_customer_history_service


def handle_admin_message(user_number, user_message):

    # Admin ki information lao
    admin = get_admin_info(user_number)

    # Auto close queue when shop closes
    if should_auto_close_queue() and is_queue_open():

        close_queue()

    queue_status = "OPEN" if is_queue_open() else "CLOSED"

    stats = get_queue_summary(admin["name"])
    waiting_count = stats["waiting"]

    # =========================
    # QUEUE CLOSED CHECK
    # =========================
    if not is_queue_open():

        active_queue = has_active_customer(admin["name"])

        # =========================
        # HEAD ADMIN
        # =========================
        if admin["role"] == "HEAD_ADMIN":

            # Greeting
            if user_message.lower() in ["hi", "hello", "hey", "hii"]:

                if active_queue:
                    send_whatsapp_message(
                        user_number,
                        "Salon Admin Panel\n\n"
                        f"Queue: {queue_status}\n"
                        f"Waiting: {waiting_count}\n\n"
                        "1. Next Customer\n"
                        "2. Daily Report\n"
                        "3. Open Queue",
                    )

                else:
                    send_whatsapp_message(
                        user_number,
                        "Salon Admin Panel\n\n"
                        f"Queue: {queue_status}\n"
                        f"Waiting: {waiting_count}\n\n"
                        "1. Daily Report\n"
                        "2. Open Queue",
                    )

                return

        # =========================
        # NORMAL ADMIN
        # =========================
        else:

            if user_message.lower() in ["hi", "hello", "hey", "hii"]:

                if active_queue:
                    send_whatsapp_message(
                        user_number,
                        "Salon Admin Panel\n\n"
                        f"Queue: {queue_status}\n"
                        f"Waiting: {waiting_count}\n\n"
                        "1. Next Customer\n"
                        "2. Daily Report",
                    )
                else:
                    send_whatsapp_message(
                        user_number,
                        "Salon Admin Panel\n\n"
                        f"Queue: {queue_status}\n"
                        f"Waiting: {waiting_count}\n\n"
                        "1. Daily Report",
                    )
                return

    # =========================
    # VALIDATE CLOSED MENU
    # =========================
    if not is_queue_open():

        active_queue = has_active_customer(admin["name"])

        # Head Admin
        if admin["role"] == "HEAD_ADMIN":
            if active_queue:
                allowed = ["1", "2", "3", "hi", "hello", "hey", "hii"]

                if user_message.lower() not in allowed:

                    send_whatsapp_message(user_number, "Please select 1, 2 or 3.")
                    return
            else:
                allowed = ["1", "2", "hi", "hello", "hey", "hii"]

                if user_message.lower() not in allowed:

                    send_whatsapp_message(user_number, "Please select 1 or 2.")
                    return

        # Normal Admin
        else:
            if active_queue:
                allowed = ["1", "2", "hi", "hello", "hey", "hii"]

                if user_message.lower() not in allowed:

                    send_whatsapp_message(user_number, "Please select 1 or 2.")
                    return

            else:
                allowed = ["1", "hi", "hello", "hey", "hii"]

                if user_message.lower() not in allowed:

                    send_whatsapp_message(user_number, "Please select 1.")
                    return

    # =========================
    # REMAP MENU (QUEUE CLOSED)
    # =========================
    if not is_queue_open():

        active_queue = has_active_customer(admin["name"])

        # Head Admin
        if admin["role"] == "HEAD_ADMIN":

            if active_queue:

                if user_message == "1":
                    user_message = "2"  # Next Customer

                elif user_message == "2":
                    user_message = "3"  # Daily Report

                elif user_message == "3":
                    user_message = "OPEN_QUEUE"

            else:

                if user_message == "1":
                    user_message = "3"  # Daily Report

                elif user_message == "2":
                    user_message = "OPEN_QUEUE"

        # Normal Admin
        else:

            if active_queue:

                if user_message == "1":
                    user_message = "2"

                elif user_message == "2":
                    user_message = "3"

            else:

                if user_message == "1":
                    user_message = "3"

    # =========================
    # ADD WALK-IN CUSTOMER
    # =========================
    if user_message == "1":

        walkin_name = get_next_walkin_name()

        result = join_queue(
            customer_name=walkin_name,
            phone_number="-",
            stylist=admin["name"],
            service="Haircut",
            customer_type="WALKIN",
        )

        log_event(
            "WALKIN_ADDED",
            NAME=walkin_name,
            STYLIST=admin["name"],
            TOKEN=result["stylist_token"],
        )

        send_whatsapp_message(
            user_number,
            f"Walk-In Customer Added ✅\n\n"
            f"Stylist: {admin['name']}\n"
            f"Token: #{result['stylist_token']}",
        )

        return

    # =========================
    # NEXT CUSTOMER
    # =========================
    if user_message == "2":
        result = complete_next_customer(admin["name"])

        # Queue me koi customer nahi
        if not result:
            send_whatsapp_message(user_number, "Queue Empty ✅")

            return

        # Current customer complete hua
        completed_customer = result["completed_customer"]

        if completed_customer:
            log_event(
                "CUSTOMER_COMPLETED",
                PHONE=result["completed_customer_phone"],
                NAME=completed_customer,
                STYLIST=admin["name"],
                TOKEN=result["completed_customer_token"],
                TYPE=result["completed_customer_type"],
            )

        if result["next_customer"]:
            log_event(
                "NEXT_CUSTOMER_STARTED",
                PHONE=result["next_customer_phone"],
                NAME=result["next_customer"],
                STYLIST=admin["name"],
                TOKEN=result["next_customer_token"],
                TYPE=result["next_customer_type"],
            )

        # Update customer history
        if (
            result["completed_customer_phone"]
            and result["completed_customer_phone"] != "-"
        ):

            update_customer_history_service(
                phone_number=result["completed_customer_phone"],
                customer_name=result["completed_customer"],
                stylist=admin["name"],
            )

        # =========================
        # Thank You Message
        # =========================
        if (
            result["completed_customer_phone"]
            and result["completed_customer_phone"] != "-"
            and result["completed_customer_type"] == "ONLINE"
        ):

            send_whatsapp_message(
                result["completed_customer_phone"],
                "✨ Thank you for visiting Adarsh Hair Salon.\n\n"
                "Humare salon par aane ke liye dhanyavaad ❤️",
            )

        # =========================
        # Customer ko notify karo Aapka number aa gaya hai
        # =========================
        if (
            result["next_customer_phone"]
            and result["next_customer_phone"] != "-"
            and result["next_customer_type"] == "ONLINE"
        ):

            send_whatsapp_message(
                result["next_customer_phone"],
                "🔥 Aapka number aa gaya hai.\n\n" "Kripya salon me report karein.",
            )

        # =========================
        # Queue me agla waiting customer
        # =========================
        if (
            result["second_customer_phone"]
            and result["second_customer_phone"] != "-"
            and result["second_customer_type"] == "ONLINE"
        ):

            send_whatsapp_message(
                result["second_customer_phone"],
                "⚡ Agla aapka number hai.\n\n" "Kripya salon ki taraf nikal jaiye.",
            )

        notify_queue_progress(admin["name"])

        # Next customer available hai
        if result["next_customer"]:

            send_whatsapp_message(
                user_number,
                f"Customer Completed ✅\n\n"
                f"Customer: {completed_customer}\n\n"
                f"Now Serving: {result['next_customer']}",
            )

        # Queue khatam
        else:
            send_whatsapp_message(
                user_number,
                f"Queue is Empty 🎉",
            )

        return

    # =========================
    # DAILY REPORT
    # =========================
    if user_message == "3":

        report = get_today_summary(admin["name"])

        log_event(
            "DAILY_REPORT_VIEWED",
            ADMIN=admin["name"],
            ROLE=admin["role"],
            STYLIST=admin["name"],
        )

        send_whatsapp_message(
            user_number,
            f"📊 Full Report\n\n"
            f"Walk-In: {report['walkin']}\n"
            f"Online: {report['online']}\n\n"
            f"Completed: {report['completed']}\n"
            f"Cancelled: {report['cancelled']}",
        )

        return

    # =========================
    # OPEN QUEUE
    # =========================
    if admin["role"] == "HEAD_ADMIN" and user_message == "OPEN_QUEUE":

        if is_queue_open():
            send_whatsapp_message(user_number, "Queue is already open.")
            return

        open_queue()

        log_event(
            "QUEUE_OPENED",
            ADMIN=admin["name"],
            PHONE=user_number,
        )

        send_whatsapp_message(user_number, "Queue Opened ✅")

        return

    # =========================
    # CLOSE QUEUE
    # =========================
    if admin["role"] == "HEAD_ADMIN" and user_message == "4":

        if not is_queue_open():
            send_whatsapp_message(user_number, "Queue is already closed.")
            return

        close_queue()

        log_event(
            "QUEUE_CLOSED",
            ADMIN=admin["name"],
            PHONE=user_number,
        )

        send_whatsapp_message(user_number, "Queue Closed ✅")

        return

    # =========================
    # HEAD ADMIN MENU
    # =========================
    if admin["role"] == "HEAD_ADMIN":

        send_whatsapp_message(
            user_number,
            "Salon Admin Panel\n\n"
            f"Queue: {queue_status}\n"
            f"Waiting: {waiting_count}\n\n"
            "1. Add walkin customer\n"
            "2. Next customer\n"
            "3. Daily Report\n"
            "4. Close queue",
        )
        return

    # =========================
    # NORMAL ADMIN MENU
    # =========================
    send_whatsapp_message(
        user_number,
        "Salon Admin Panel\n\n"
        f"Queue: {queue_status}\n"
        f"Waiting: {waiting_count}\n\n"
        "1. Add walkin customer\n"
        "2. Next customer\n"
        "3. Daily Report",
    )
