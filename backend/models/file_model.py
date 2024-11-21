from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, ConfigurationError
from backend.config.config import get_config
from backend.logger import logging

# Fetch configuration
CONFIG = get_config()
MONGO_URI = CONFIG['MONGO_URI']
DATABASE_NAME = CONFIG['DATABASE_NAME']

# Initialize MongoDB Client

def get_db_client():
    """
    Establish and return the MongoDB client and database connection.
    """
    try:
        # Log connection attempt
        logging.info(f"Attempting to connect to MongoDB at {MONGO_URI} using database '{DATABASE_NAME}'")
        
        # Establish MongoDB connection
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]  # Access the database dynamically
        logging.info(f"Successfully connected to database: {DATABASE_NAME}")
        return db
    except ServerSelectionTimeoutError as e:
        logging.error(f"MongoDB connection timeout error: {e}")
        raise  # Re-raise for the caller to handle or log further
    except ConnectionFailure as e:
        logging.error(f"MongoDB connection failure: {e}")
        raise  # Re-raise for the caller to handle or log further
    except OperationFailure as e:
        logging.error(f"MongoDB operation failure: {e}")
        raise  # Re-raise for the caller to handle or log further
    except ConfigurationError as e:
        logging.error(f"MongoDB configuration error: {e}")
        raise  # Re-raise for the caller to handle or log further
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise for the caller to handle or log further

# Get the 'files' collection
def get_files_collection():
    """
    Return the 'files' collection from the database.
    Ensures that the database client is properly initialized first.
    """
    try:
        db = get_db_client()  # Ensure the client is connected and database is accessible
        collection = db.files  # Get the files collection dynamically
        logging.info(f"Successfully accessed the 'files' collection.")
        return collection
    except Exception as e:
        logging.error(f"Failed to access the 'files' collection: {e}")
        raise  # Re-raise for the caller to handle or log further
