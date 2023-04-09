import os
import json
import pymongo
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# MongoDB configuration
MONGO_HOST = "mongodb://localhost:27017/"
MONGO_DB = "it_career_paths"
MONGO_COLLECTION = "career_paths"

# Telegram bot configuration
TELEGRAM_TOKEN = ('bot/bot.env')
if not TELEGRAM_TOKEN:
    raise ValueError('Please provide TELEGRAM_TOKEN environment variable')


def start(update, context):
    """Command handler for /start command"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a chatbot that can help you with IT career paths. Please type in some keywords related to your query.")


def search(update, context):
    """Message handler for user queries"""
    keywords = update.message.text.lower().split()
    client = pymongo.MongoClient(MONGO_HOST)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    query = {"keywords": {"$all": keywords}}
    result = collection.find_one(query)
    if result:
        response = result['response']
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't find any information on that topic.")


def main():
    # Create database if not exists
    client = pymongo.MongoClient(MONGO_HOST)
    db_list = client.list_database_names()
    if MONGO_DB not in db_list:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        with open('data/career_paths.json') as f:
            data = json.load(f)
        collection.insert_many(data)

    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN = ('bot/bot.env'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Message handlers
    search_handler = MessageHandler(Filters.text & ~Filters.command, search)
    dispatcher.add_handler(search_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()