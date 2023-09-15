import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

class MongoDBConnection:
    def __init__(self, connection_string):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['djaisp']

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close_connection(self):
        self.client.close()

class Database:
    def __init__(self):
        self.connection = MongoDBConnection(os.getenv('CONNECTION_STRING'))

    def insert_document(self, document):
        collection = self.connection.get_collection('users')
        return collection.insert_one(document)

    def find_documents(self, query={}):
        collection = self.connection.get_collection('users')
        return collection.find(query)

    def find_one_document(self, query={}):
        collection = self.connection.get_collection('users')
        return collection.find_one(query)

    def update_document(self, query, update_data):
        collection = self.connection.get_collection('users')
        return collection.update_one(query, {'$set': update_data})

    def delete_document(self, query):
        collection = self.connection.get_collection('users')
        return collection.delete_one(query)

    def close_connection(self):
        self.connection.close_connection()