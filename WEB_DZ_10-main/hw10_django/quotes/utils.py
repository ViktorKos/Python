from pymongo import MongoClient
from pymongo.server_api import ServerApi


def get_mongodb():
    uri = "mongodb+srv://phenix:567432@clusterphenix.wy97tt3.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client["hw"]
    return db
