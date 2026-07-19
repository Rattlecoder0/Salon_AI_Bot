from sqlalchemy import select

from database.database import SessionLocal
from database.models import Setting
from google_sheets import get_sheet


def seed_settings():

    sheet = get_sheet("Settings")
    rows = sheet.get_all_records()

    with SessionLocal() as db:

        for row in rows:

            exists = db.scalar(
                select(Setting).where(
                    Setting.key == row["Key"]
                )
            )

            if exists:
                continue

            db.add(
                Setting(
                    key=row["Key"],
                    value=str(row["Value"]),
                )
            )

        db.commit()

    print("✅ Settings seeded successfully.")


if __name__ == "__main__":
    seed_settings()