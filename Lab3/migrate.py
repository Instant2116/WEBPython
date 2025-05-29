import json

import psycopg2
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

PG_USER = "postgres"
PG_PASSWORD = "6497"
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB_NAME = "WEBPython"

MONGO_DB_URL = "mongodb://localhost:27017/"
MONGO_DB_NAME = "web_lab_db"


def get_pg_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB_NAME
        )
        print(f"Connected to PostgreSQL database: {PG_DB_NAME}")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None


def get_mongo_client():
    """Establishes and returns a MongoDB client."""
    try:
        client = MongoClient(MONGO_DB_URL)

        client.admin.command('ismaster')
        print(f"Connected to MongoDB at: {MONGO_DB_URL}")
        return client
    except ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def migrate_data():
    pg_conn = None
    mongo_client = None
    try:
        pg_conn = get_pg_connection()
        if not pg_conn:
            print("Aborting migration due to PostgreSQL connection error.")
            return

        mongo_client = get_mongo_client()
        if not mongo_client:
            print("Aborting migration due to MongoDB connection error.")
            return

        mongo_db = mongo_client[MONGO_DB_NAME]

        print("\n--- Migrating Roles ---")
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT id, name FROM roles ORDER BY id")
        pg_roles = pg_cursor.fetchall()
        pg_cursor.close()

        mongo_roles_collection = mongo_db.roles
        mongo_roles_collection.delete_many({})

        role_id_map = {}
        for pg_id, name in pg_roles:
            role_doc = {"name": name}
            result = mongo_roles_collection.insert_one(role_doc)
            role_id_map[pg_id] = result.inserted_id
            print(f"Migrated Role: '{name}' (PG ID: {pg_id}) to Mongo ID: {result.inserted_id}")

        print("\n--- Roles Migration Complete ---")
        print(f"Role ID Map: {json.dumps({k: str(v) for k, v in role_id_map.items()}, indent=2)}")

        print("\n--- Migrating Users ---")
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT id, username, email, password, role_id FROM users ORDER BY id")
        pg_users = pg_cursor.fetchall()
        pg_cursor.close()

        mongo_users_collection = mongo_db.users
        mongo_users_collection.delete_many({})

        for pg_id, username, email, password_hash, pg_role_id in pg_users:
            mongo_role_id = role_id_map.get(pg_role_id)
            if not mongo_role_id:
                print(f"Warning: Role ID {pg_role_id} not found in map for user '{username}'. Skipping user.")
                continue

            user_doc = {
                "username": username,
                "email": email,
                "password": password_hash,
                "role_id": mongo_role_id
            }
            result = mongo_users_collection.insert_one(user_doc)
            print(f"Migrated User: '{username}' (PG ID: {pg_id}) to Mongo ID: {result.inserted_id}")

        print("\n--- Users Migration Complete ---")

        print("\n--- Migrating Found Items ---")
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT id, name, description FROM items ORDER BY id")
        pg_items = pg_cursor.fetchall()
        pg_cursor.close()

        mongo_items_collection = mongo_db.items
        mongo_items_collection.delete_many({})

        for pg_id, name, description in pg_items:
            item_doc = {"name": name, "description": description}
            result = mongo_items_collection.insert_one(item_doc)
            print(f"Migrated Found Item: '{name}' (PG ID: {pg_id}) to Mongo ID: {result.inserted_id}")

        print("\n--- Found Items Migration Complete ---")

        print("\n--- Migrating Lost Items ---")
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT id, name, description FROM lost_items ORDER BY id")
        pg_lost_items = pg_cursor.fetchall()
        pg_cursor.close()

        mongo_lost_items_collection = mongo_db.lost_items
        mongo_lost_items_collection.delete_many({})

        for pg_id, name, description in pg_lost_items:
            lost_item_doc = {"name": name, "description": description}
            result = mongo_lost_items_collection.insert_one(lost_item_doc)
            print(f"Migrated Lost Item: '{name}' (PG ID: {pg_id}) to Mongo ID: {result.inserted_id}")

        print("\n--- Lost Items Migration Complete ---")

        print("\n--- All Data Migration Finished Successfully! ---")

    except Exception as e:
        print(f"\nAn error occurred during migration: {e}")
    finally:
        if pg_conn:
            pg_conn.close()
            print("PostgreSQL connection closed.")
        if mongo_client:
            mongo_client.close()
            print("MongoDB connection closed.")


if __name__ == "__main__":
    migrate_data()
