from sqlalchemy import select

from database.database import SessionLocal
from database.models import Setting


def get_setting(key):

    with SessionLocal() as db:

        setting = db.scalar(
            select(Setting).where(Setting.key == key)
        )

        if setting:
            return setting.value

        return None
    
# ====================================
# Update Setting
# ====================================
def update_setting(key, value):

    with SessionLocal() as db:

        setting = db.scalar(
            select(Setting).where(Setting.key == key)
        )

        if not setting:
            return False

        setting.value = value

        db.commit()

        return True
    
# ====================================
# Get All Settings
# ====================================
def get_all_settings():

    with SessionLocal() as db:

        return db.scalars(
            select(Setting)
        ).all()