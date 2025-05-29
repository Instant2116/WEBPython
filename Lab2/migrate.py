import sqlite3

import psycopg2

try:
    from database import Base, engine as pg_engine

    from database import PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB_NAME
except ImportError as e:
    print(
        f"Error: Could not import necessary components from database.py: {e}. Make sure 'database.py' is accessible and exports 'Base', 'engine', and the PG_* connection parameters.")
    exit(1)

try:
    from models import Item, User, Role, LostItem
except ImportError as e:
    print(f"Error: Could not import models: {e}. Make sure 'models.py' is accessible.")
    exit(1)

SQLITE_DB_PATH = "test.db"


def migrate_data():
    sqlite_conn = None
    sqlite_cursor = None
    pg_conn = None
    pg_cursor = None

    try:
        print("--- Ensuring PostgreSQL tables exist ---")

        print(
            f"DEBUG: Connecting to PostgreSQL with user='{PG_USER}', host='{PG_HOST}', port={PG_PORT}, dbname='{PG_DB_NAME}'")

        print("Attempting to create all defined tables in PostgreSQL (if they don't already exist) via SQLAlchemy...")
        Base.metadata.create_all(bind=pg_engine)
        print("PostgreSQL tables checked/created successfully via SQLAlchemy.")

        pg_conn = psycopg2.connect(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB_NAME
        )
        pg_cursor = pg_conn.cursor()

        print("Verifying tables from psycopg2 connection:")
        try:
            pg_cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name IN ('roles', 'users', 'items', 'lost_items');
            """)
            verified_tables_psycopg2 = [row[0] for row in pg_cursor.fetchall()]
            print(f"  Found these tables in PostgreSQL (via psycopg2): {verified_tables_psycopg2}")

            expected_tables = ["roles", "users", "items", "lost_items"]
            missing_tables = [t for t in expected_tables if t not in verified_tables_psycopg2]
            if missing_tables:
                raise Exception(
                    f"CRITICAL ERROR: The following tables are missing from PostgreSQL after creation attempt: {missing_tables}")

        except Exception as e:
            print(f"  Error verifying tables in PostgreSQL (via psycopg2): {e}")
            raise

        print("\n--- Starting data migration ---")

        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        migrate_table(sqlite_cursor, pg_cursor, "roles")
        migrate_table(sqlite_cursor, pg_cursor, "users")
        migrate_table(sqlite_cursor, pg_cursor, "items")
        migrate_table(sqlite_cursor, pg_cursor, "lost_items")

        pg_conn.commit()
        print("\nData migration completed successfully!")

    except (sqlite3.Error, psycopg2.Error) as e:
        print(f"\nError during migration: {e}")
        if pg_conn:
            pg_conn.rollback()
    except Exception as e:
        print(f"\nAn unexpected error occurred during migration setup or verification: {e}")
    finally:

        if sqlite_cursor:
            sqlite_cursor.close()
        if sqlite_conn:
            sqlite_conn.close()
        if pg_cursor:
            pg_cursor.close()
        if pg_conn:
            pg_conn.close()


def migrate_table(sqlite_cursor, pg_cursor, table_name):
    print(f"  Migrating table: {table_name}")

    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = sqlite_cursor.fetchall()

    if not columns_info:
        print(
            f"    Warning: No column info found for table '{table_name}' in SQLite. Skipping migration for this table.")
        return

    columns = [col[1] for col in columns_info]
    placeholders = ", ".join(["%s"] * len(columns))

    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    quoted_columns = [f'"{col}"' for col in columns]
    insert_query = f"INSERT INTO {table_name} ({', '.join(quoted_columns)}) VALUES ({placeholders})"

    try:
        if rows:
            pg_cursor.executemany(insert_query, rows)
            print(f"    Migrated {len(rows)} rows to {table_name}")
        else:
            print(f"    No data to migrate for {table_name}")
    except psycopg2.Error as e:
        print(f"    Error migrating {table_name}: {e}")
        raise
    except Exception as e:
        print(f"    An unexpected error occurred during migration of {table_name}: {e}")
        raise


if __name__ == "__main__":
    migrate_data()
