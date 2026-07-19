from sqlalchemy import select

from database.database import SessionLocal
from database.models import Service


def get_active_services():

    with SessionLocal() as db:

        return db.scalars(
            select(Service).where(Service.is_active == True)
        ).all()
    
# ====================================
# Get Service By Name
# ====================================
def get_service_by_name(service_name):

    with SessionLocal() as db:

        return db.scalar(
            select(Service).where(
                Service.name == service_name,
                Service.is_active == True,
            )
        )
    
# ====================================
# Get All Services
# ====================================
def get_all_services():

    with SessionLocal() as db:

        return db.scalars(
            select(Service)
        ).all()
    
# ====================================
# Get Service Time Map
# ====================================
def get_service_time_map():

    with SessionLocal() as db:

        services = db.scalars(
            select(Service)
        ).all()

        return {
            service.name: service.average_time
            for service in services
        }