from sqlalchemy import select

from database.database import SessionLocal
from database.models import Admin
from google_sheets import get_sheet


def seed_admins():

    sheet = get_sheet("Admins")
    rows = sheet.get_all_records()

    with SessionLocal() as db:

        for row in rows:

            exists = db.scalar(
                select(Admin).where(
                    Admin.phone_number == str(row["Phone Number"])
                )
            )

            if exists:
                continue

            db.add(
                Admin(
                    name=row["Name"],
                    phone_number=str(row["Phone Number"]),
                    role=row["Role"],
                )
            )

        db.commit()

    print("✅ Admins seeded successfully.")


if __name__ == "__main__":
    seed_admins()