from repository.customer_history_repository import (
    get_customer_history,
    add_customer_history,
    update_customer_history,
)


# ====================================
# Update Customer History
# ====================================
def update_customer_history_service(
    phone_number,
    customer_name,
    stylist,
):
    
    # Skip walk-in customers
    if phone_number == "-":
        return

    customer = get_customer_history(
        phone_number,
        stylist,
    )

    if customer:
        customer = update_customer_history(
            phone_number,
            stylist,
        )
        return
    
    customer = add_customer_history(
        phone_number,
        customer_name,
        stylist,
    )