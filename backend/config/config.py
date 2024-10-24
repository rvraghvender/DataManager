import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI is None:
    raise ValueError("MONGO_URI is not set in the .env file")

# Define upload folder
UPLOAD_FOLDER = 'uploads'
