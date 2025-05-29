from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "web_lab_db"

client: MongoClient = None


def connect_to_mongo():
    """Establishes connection to MongoDB and sets global client/db objects."""
    global client, db
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        client.admin.command('ping')
        db = client[MONGO_DB_NAME]
        print(f"Successfully connected to MongoDB database '{MONGO_DB_NAME}'")
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")

        raise


def close_mongo_connection():
    """Closes the MongoDB client connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")


def get_database():
    """Dependency to yield the MongoDB Database object."""

    if db is None:
        connect_to_mongo()
    yield db
