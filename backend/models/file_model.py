from pymongo import MongoClient
from config.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.filemanager
files_collection = db.files
