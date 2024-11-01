import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MONGO_DATABASE")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

if not MONGO_URI or not DATABASE_NAME or not COLLECTION_NAME:
    raise ValueError("Ensure MONGO_URI, MONGO_DATABASE, and MONGO_COLLECTION are set in .env file.")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]