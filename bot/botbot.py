from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['chatbot_db']
collection = db['career_paths']

if '<your MongoDB collection name>' not in db.list_collection_names():
    # Create the MongoDB collection
    collection = db.create_collection('career_paths')
    logging.info('Created MongoDB collection')

    # Load the sample data from the JSON file
    with open('data/career_paths.json') as f:
        data = json.load(f)

    # Insert the sample data into the MongoDB collection
    collection.insert_many(data)
    logging.info('Inserted sample data into MongoDB collection')

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the IT Career Bot! How can I help you?")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You can ask me about different IT career paths and I'll provide you with some information.")