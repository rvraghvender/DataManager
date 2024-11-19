import os
from dotenv import load_dotenv
from pathlib import Path


# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI is None:
    raise ValueError("MONGO_URI is not set in the .env file")

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

# Define upload folder
UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads')
print(UPLOAD_FOLDER)
