# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- PostgreSQL Connection Parameters ---
PG_USER = "postgres"
PG_PASSWORD = "6497"
PG_HOST = "localhost"
PG_PORT = 5432 # This must be an integer, not a string
PG_DB_NAME = "WEBPython"

# Construct the URL using f-string for create_engine (or use connect_args)
SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}"

# SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # This is the single Base object all models use

# You can keep your init_db function here if you use it for the main app
def init_db():
    print("Initializing the database from database.py...")
    try:
        # Import models here if init_db is called independently
        from models import Item, User, Role, LostItem # Added LostItem
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully by database.py init_db.")
    except Exception as e:
        print(f"Error creating tables in database.py init_db: {e}")