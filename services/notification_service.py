from repository.queue_repository import (
    get_current_serving_customer,
    get_waiting_online_customers,
)
from whatsapp import send_whatsapp_message


# ====================================
# Notify Queue Progress
# ====================================
def notify_queue_progress(stylist):

    current_customer = get_current_serving_customer(stylist)

    if not current_customer:
        return

    waiting_customers = get_waiting_online_customers(stylist)

    if not waiting_customers:
        return
    
    for position, customer in enumerate(waiting_customers):

        # Position 0 = Next customer
        # Position 1 = You're next
        if position < 2:
            continue

        people_ahead = position

        message = (
            "💈 Queue Update\n\n"
            f"Now Serving: Token #{current_customer.stylist_token}\n"
            f"Your Token: #{customer.stylist_token}\n"
            f"People Ahead: {people_ahead}"
        )

        send_whatsapp_message(
            customer.phone_number,
            message,
        )