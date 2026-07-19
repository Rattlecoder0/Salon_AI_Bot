from database.database import SessionLocal
from database.models import Admin, Setting, Staff, Service


def seed_database():
    db = SessionLocal()

    try:
        # ==========================
        # ADMINS
        # ==========================
        if db.query(Admin).count() == 0:
            db.add_all([
                Admin(
                    name="Ruturaj",
                    phone_number="91827543546",
                    role="HEAD_ADMIN"
                ),
                Admin(
                    name="Ramesh",
                    phone_number="918275435466",
                    role="ADMIN"
                ),
                Admin(
                    name="Ubaid",
                    phone_number="918275435463",
                    role="ADMIN"
                ),
            ])

        # ==========================
        # SETTINGS
        # ==========================
        if db.query(Setting).count() == 0:
            db.add_all([
                Setting(key="QUEUE_STATUS", value="OPEN"),
                Setting(key="OPEN_TIME", value="10:00"),
                Setting(key="CLOSE_TIME", value="23:58"),
                Setting(key="BUFFER_MINUTES", value="1"),
            ])

        # ==========================
        # STAFF
        # ==========================
        if db.query(Staff).count() == 0:
            db.add_all([
                Staff(name="Ruturaj", is_active=True),
                Staff(name="Ramesh", is_active=True),
                Staff(name="Ubaid", is_active=True),
            ])

        # ==========================
        # SERVICES
        # ==========================
        if db.query(Service).count() == 0:
            db.add_all([
                Service(
                    name="Haircut",
                    price=100,
                    average_time=20,
                    is_active=True,
                ),
                Service(
                    name="Beard",
                    price=50,
                    average_time=10,
                    is_active=True,
                ),
                Service(
                    name="Hair Spa",
                    price=200,
                    average_time=45,
                    is_active=True,
                ),
                Service(
                    name="Haircut + Beard",
                    price=150,
                    average_time=30,
                    is_active=True,
                ),
            ])

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()