from sqlalchemy import select
from datetime import datetime
from database.database import SessionLocal
from database.models import CustomerHistory


# ====================================
# Get Customer History
# ====================================
def get_customer_history(phone_number, stylist):

    with SessionLocal() as db:

        return db.scalar(
            select(CustomerHistory).where(
                CustomerHistory.phone_number == str(phone_number),
                CustomerHistory.stylist == stylist,
            )
        )


# ====================================
# Add Customer History
# ====================================
def add_customer_history(
    phone_number,
    customer_name,
    stylist,
):    
    with SessionLocal() as db:

        customer = CustomerHistory(
            phone_number=str(phone_number),
            customer_name=customer_name,
            total_visits=1,
            last_visit=datetime.now().strftime("%d-%m-%Y"),
            stylist=stylist,
        )        
        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer


# ====================================
# Update Customer History
# ====================================
def update_customer_history(phone_number, stylist):

    with SessionLocal() as db:                
        customer = db.scalar(
            select(CustomerHistory).where(
                CustomerHistory.phone_number == str(phone_number),
                CustomerHistory.stylist == stylist,
            )
        )        
        if not customer:
            return None

        customer.total_visits += 1
        customer.last_visit = datetime.now().strftime("%d-%m-%Y")

        db.commit()
        db.refresh(customer)

        return customer
    
# ====================================
# Get All Customer History
# ====================================
def get_all_customer_history():

    with SessionLocal() as db:

        return db.scalars(
            select(CustomerHistory)
        ).all()