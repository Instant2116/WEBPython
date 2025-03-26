from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    print("Initializing the database...")

    try:

        from models import Item, User, Role

        Base.metadata.create_all(bind=engine)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            print("Tables in the database:", tables)

        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
