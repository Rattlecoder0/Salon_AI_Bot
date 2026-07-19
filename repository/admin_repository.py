from sqlalchemy import select

from database.database import SessionLocal
from database.models import Admin


def get_admin_by_phone(phone_number):

    with SessionLocal() as db:

        return db.scalar(
            select(Admin).where(
                Admin.phone_number == str(phone_number)
            )
        )


def get_admin_by_name(name):

    with SessionLocal() as db:

        return db.scalar(
            select(Admin).where(
                Admin.name == name
            )
        )