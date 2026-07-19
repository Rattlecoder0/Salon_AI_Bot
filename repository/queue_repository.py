from sqlalchemy import func, select
from datetime import datetime, date
from database.models import Queue
from database.database import SessionLocal


# ====================================
# Add Customer
# ====================================
def create_queue_entry(queue):

    with SessionLocal() as db:

        db.add(queue)
        db.commit()
        db.refresh(queue)

        return queue


# ====================================
# Global Token
# ====================================
def get_next_global_token():

    with SessionLocal() as db:

        last_token = db.scalar(
            select(func.max(Queue.global_token))
            .where(
                func.date(Queue.created_at) == date.today()
            )
        )

        return (last_token or 0) + 1


# ====================================
# Stylist Token
# ====================================
def get_next_stylist_token(stylist):

    with SessionLocal() as db:

        last_token = db.scalar(
            select(func.max(Queue.stylist_token))
            .where(
                Queue.stylist == stylist,
                func.date(Queue.created_at) == date.today()
            )
        )

        return (last_token or 0) + 1
    
# ====================================
# Add Customer
# ====================================
def add_customer(
    customer_name,
    phone_number,
    stylist,
    service,
    customer_type,
    status,
    global_token,
    stylist_token,
):

    queue = Queue(
        global_token=global_token,
        customer_name=customer_name,
        phone_number=phone_number,
        stylist=stylist,
        stylist_token=stylist_token,
        service=service,
        customer_type=customer_type,
        status=status,
        created_at=datetime.now(),
        started_at=datetime.now() if status == "IN_PROGRESS" else None,
        completed_at=None,
    )

    return create_queue_entry(queue)

def get_current_serving_customer(stylist):

    with SessionLocal() as db:

        return db.scalar(
            select(Queue).where(
                Queue.stylist == stylist,
                Queue.status == "IN_PROGRESS",
            )
        )
    
def get_next_waiting_customer(stylist):

    with SessionLocal() as db:

        return db.scalar(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.status == "WAITING",
            )
            .order_by(Queue.stylist_token)
        )
    
# ====================================
# Update Customer Status
# ====================================
def update_customer_status(queue_id, status):

    with SessionLocal() as db:

        customer = db.get(Queue, queue_id)

        if not customer:
            return None

        customer.status = status

        if status == "IN_PROGRESS":
            customer.started_at = datetime.now()

        elif status == "COMPLETED":
            customer.completed_at = datetime.now()

        db.commit()
        db.refresh(customer)

        return customer
    
# ====================================
# Complete Next Customer
# ====================================
def complete_next_customer(stylist):

    with SessionLocal() as db:

        current_customer = db.scalar(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.status == "IN_PROGRESS",
                func.date(Queue.created_at) == date.today(),
            )
            .order_by(Queue.stylist_token)
        )

        next_customer = db.scalar(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.status == "WAITING",
                func.date(Queue.created_at) == date.today(),
            )
            .order_by(Queue.stylist_token)
        )

        if current_customer:
            current_customer.status = "COMPLETED"
            current_customer.completed_at = datetime.now()

        if next_customer:

            next_customer.status = "IN_PROGRESS"
            next_customer.started_at = datetime.now()

        db.commit()

        if current_customer:
            db.refresh(current_customer)

        if next_customer:
            db.refresh(next_customer)

        return current_customer, next_customer
    
# ====================================
# Get Active Queue
# ====================================
def get_active_queue(stylist):
    with SessionLocal() as db:

        return db.scalars(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.status.in_(["WAITING", "IN_PROGRESS"]),
                func.date(Queue.created_at) == date.today(),
            )
            .order_by(Queue.stylist_token)
        ).all()
    
# ====================================
# Get Customer By Phone
# ====================================
def get_active_customer(phone_number):

    with SessionLocal() as db:

        return db.scalar(
            select(Queue).where(
                Queue.phone_number == str(phone_number),
                Queue.status.in_(["WAITING", "IN_PROGRESS"]),
            )
        )
    
# ====================================
# Check Today's Completed Customer
# ====================================
def is_customer_completed_today(phone_number):

    with SessionLocal() as db:

        customer = db.scalar(
            select(Queue).where(
                Queue.phone_number == str(phone_number),
                Queue.status == "COMPLETED",
                func.date(Queue.created_at) == date.today(),
            )
        )

        return customer is not None
    
# ====================================
# Cancel Customer
# ====================================
def cancel_customer(queue_id):

    with SessionLocal() as db:

        customer = db.get(Queue, queue_id)

        if not customer:
            return None

        customer.status = "CANCELLED"

        db.commit()
        db.refresh(customer)

        return customer
    
# ====================================
# Get All Customers By Stylist
# ====================================
def get_all_customers(stylist):

    with SessionLocal() as db:

        return db.scalars(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                func.date(Queue.created_at) == date.today()
                )
            .order_by(Queue.stylist_token)
        ).all()
    
# ====================================
# Get Total Walk-In Customers
# ====================================
def get_walkin_count():

    with SessionLocal() as db:

        return db.scalar(
            select(func.count())
            .select_from(Queue)
            .where(Queue.customer_type == "WALKIN")
        )
    
# ====================================
# Get All Queue
# ====================================
def get_all_queue():

    with SessionLocal() as db:

        return db.scalars(
            select(Queue).order_by(
                Queue.created_at
            )
        ).all()

# ====================================
# Get Waiting Online Customers
# ====================================
def get_waiting_online_customers(stylist):

    with SessionLocal() as db:

        return db.scalars(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.customer_type == "ONLINE",
                Queue.status == "WAITING",
            )
            .order_by(Queue.stylist_token)
            .limit(5)
        ).all()

# ====================================
# Get Waiting Queue
# ====================================
def get_waiting_queue(stylist):

    with SessionLocal() as db:

        return db.scalars(
            select(Queue)
            .where(
                Queue.stylist == stylist,
                Queue.status == "WAITING",
                func.date(Queue.created_at) == date.today(),
            )
            .order_by(Queue.stylist_token)
        ).all()
    
# ====================================
# Total Active Queue Count
# ====================================
def get_total_active_queue_count():

    with SessionLocal() as db:

        return db.scalar(
            select(func.count())
            .select_from(Queue)
            .where(
                Queue.status.in_(["WAITING", "IN_PROGRESS"]),
                func.date(Queue.created_at) == date.today(),
            )
        )