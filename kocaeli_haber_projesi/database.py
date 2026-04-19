import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kocaeli_haber_db")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

haberler_col = db["haberler"]
geocache_col = db["geocache"]  


haberler_col.create_index([("haber_linki", ASCENDING)], unique=True, sparse=True)
haberler_col.create_index([("haber_turu", ASCENDING)])
haberler_col.create_index([("ilce", ASCENDING)])
haberler_col.create_index([("yayin_tarihi", ASCENDING)])
geocache_col.create_index([("konum_metni", ASCENDING)], unique=True)




