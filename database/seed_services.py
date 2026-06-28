from sqlalchemy import select

from database.database import SessionLocal
from database.models import Service
from queue_service import get_services


def seed_services():

    services = get_services()

    with SessionLocal() as db:

        for service in services:

            exists = db.scalar(
                select(Service).where(
                    Service.name == service["Service"]
                )
            )

            if exists:
                continue

            db.add(
                Service(
                    name=service["Service"],
                    price=int(service["Price"]),
                    average_time=int(service["Average Time"]),
                    is_active=True,
                )
            )

        db.commit()

    print("✅ Services seeded successfully.")


if __name__ == "__main__":
    seed_services()