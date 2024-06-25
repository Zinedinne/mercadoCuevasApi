from mercado_cuevas_api.config import (
    DOCUMENT_DB_PASSWORD,
    DOCUMENT_DB_USER,
    DOCUMENT_DB_URL,
    DEFAULT_DATABASE,
)
from pymongo import MongoClient


class DatabaseConnection:
    def __init__(self, database: str = DEFAULT_DATABASE):
        self._CONNECTION_URI = ("mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".format(DOCUMENT_DB_USER, DOCUMENT_DB_PASSWORD, DOCUMENT_DB_URL))
        self._client = MongoClient(self._CONNECTION_URI)
        self._db = self._client[database]

    def get_db(self):
        return self._db


class Collections:
    def __init__(self):
        self._clientdb = DatabaseConnection().get_db()

    def get_collection(self, collection_name: str):
        if len(collection_name) and isinstance(collection_name, str):
            return self._clientdb[collection_name]
