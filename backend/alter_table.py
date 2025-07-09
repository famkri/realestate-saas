from sqlalchemy import create_engine, text
import os

# You can use the DATABASE_URL from your environment, or paste it directly here
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://famkri:2RrBV4QxEcHUzQHg6l3H6UC9SobBr8dc@dpg-d1n7d2uuk2gs739lvskg-a.oregon-postgres.render.com/realestate_saas")

# If your URL starts with postgres://, change it to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # This will add the column only if it doesn't already exist
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;"))
        print("Column 'updated_at' added successfully!")
    except Exception as e:
        print(f"Error: {e}")
