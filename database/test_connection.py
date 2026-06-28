from sqlalchemy import text
from database.database import engine, create_tables

try:
    with engine.connect() as connection:

        create_tables()

        result = connection.execute(text("SELECT version();"))

        print("\n✅ PostgreSQL Connected Successfully!\n")
        print(result.scalar())

except Exception as e:

    print("\n❌ Database Connection Failed\n")
    print(e)