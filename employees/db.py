from django.conf import settings
from pymongo import MongoClient

_client = None
_db = None

def get_db():
    global _client, _db
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB_NAME]
    return _db

def get_employees_collection():
    db = get_db()
    return db['employees']
