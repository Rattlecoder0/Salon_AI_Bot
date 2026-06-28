# User ki temporary booking data store karne ke liye

customer_data = {}


def get_customer_data(user_number):
    return customer_data.get(user_number, {})


def set_customer_data(user_number, key, value):

    # Agar user pehle se exist nahi karta to empty object banao
    if user_number not in customer_data:
        customer_data[user_number] = {}

    customer_data[user_number][key] = value