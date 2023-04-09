import json
import logging
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']

# Check if the MongoDB collection exists
if 'response' in db.list_collection_names():
    # Retrieve the existing collection
    collection = db['response']
    logging.info('Retrieved MongoDB collection')
else:
    # Create the MongoDB collection
    collection = db.create_collection('response')
    logging.info('Created MongoDB collection')

# Load data from JSON file
with open('data/career_paths.json') as f:
    data = json.load(f)

# Insert the data into the collection
result = collection.insert_many(data)
logging.info('Inserted sample data into MongoDB collection')