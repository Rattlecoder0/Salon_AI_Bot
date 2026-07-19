from sqlalchemy import select

from google_sheets import get_sheet

from database.database import SessionLocal
from database.models import CustomerHistory


def seed_customer_history():

    sheet = get_sheet("Customer History")

    rows = sheet.get_all_records()

    with SessionLocal() as db:

        for row in rows:

            exists = db.scalar(
                select(CustomerHistory).where(
                    CustomerHistory.phone_number == str(row["Phone Number"]),
                    CustomerHistory.stylist == row["Stylist"],
                )
            )

            if exists:
                continue

            db.add(
                CustomerHistory(
                    phone_number=str(row["Phone Number"]),
                    customer_name=row["Customer Name"],
                    total_visits=int(row["Total Visits"]),
                    last_visit=row["Last Visit"],
                    stylist=row["Stylist"],
                )
            )

        db.commit()

    print("✅ Customer History seeded successfully.")


if __name__ == "__main__":
    seed_customer_history()