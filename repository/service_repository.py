from sqlalchemy import select

from database.database import SessionLocal
from database.models import Service


def get_all_services():

    with SessionLocal() as db:

        return db.scalars(
            select(Service).where(Service.is_active == True)
        ).all()