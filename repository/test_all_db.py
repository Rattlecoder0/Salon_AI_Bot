from repository.queue_repository import (
    get_active_customer,
    cancel_customer,
)

customer = get_active_customer("918275435464")

print(customer.customer_name)

cancel_customer(customer.id)

print("Cancelled")