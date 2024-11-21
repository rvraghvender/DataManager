import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI is None:
    raise ValueError("MONGO_URI is not set in the .env file")

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATABASE_NAME = 'filemanager'

UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads')
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
MONGO_DATA_DIR = os.path.join(ROOT_DIR, 'mongoDB')
MONGO_LOG_DIR = os.path.join(ROOT_DIR, 'logs')

os.makedirs(MONGO_DATA_DIR, exist_ok=True)
os.makedirs(MONGO_LOG_DIR, exist_ok=True)

MONGO_PORT = os.getenv("MONGO_PORT", 27017)
MONGO_LOG_FILE = os.path.join(MONGO_LOG_DIR, "mongod.log")

def get_config():
    return {
        "MONGO_URI": MONGO_URI,
        "ROOT_DIR": ROOT_DIR,
        "UPLOAD_FOLDER": UPLOAD_FOLDER,
        "LOG_DIR": LOG_DIR,
        "DATABASE_NAME": DATABASE_NAME,
        "MONGO_DATA_DIR": MONGO_DATA_DIR,
        "MONGO_LOG_DIR": MONGO_LOG_DIR,
        "MONGO_LOG_FILE": MONGO_LOG_FILE,
        "MONGO_PORT": MONGO_PORT
    }
