from google_sheets import get_sheet

from database.database import SessionLocal
from database.models import Staff


def seed_staff():

    sheet = get_sheet("Staff")

    rows = sheet.get_all_records()

    with SessionLocal() as db:

        # Clear existing data
        db.query(Staff).delete()

        for row in rows:

            db.add(
                Staff(
                    name=row["Name"],
                    is_active=row["Active"].strip().lower() == "yes",
                )
            )

        db.commit()

    print("Staff seeded successfully.")


if __name__ == "__main__":

    seed_staff()