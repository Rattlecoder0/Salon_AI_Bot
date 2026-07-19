from sqlalchemy import select

from database.database import SessionLocal
from database.models import Staff


# ====================================
# Get Active Staff Members
# ====================================
def get_active_staff_members():

    with SessionLocal() as db:

        return db.scalars(
            select(Staff).where(
                Staff.is_active == True
            )
        ).all()


# ====================================
# Get Staff By Name
# ====================================
def get_staff_by_name(name):

    with SessionLocal() as db:

        return db.scalar(
            select(Staff).where(
                Staff.name == name
            )
        )