import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import telebot

# import os
# from pymongo import MongoClient  

# Set up the Telegram bot
bot_token = '6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c'
bot = telegram.Bot(token=bot_token)
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

# Define a command handler for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! Welcome to COMP7940 project demo.')

# Define a message handler for all non-command messages
def message(update, context):
    # Get the user's message and process it
    message_text = update.message.text
    # TODO: process the message and generate a response
    response_text = 'This is a response to your message.'
    # Send the response back to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Add the handlers to the dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, message))

# Set up the MongoDB client
# MONGO_URL = os.environ.get('MONGO_URL')
# client = MongoClient(MONGO_URL)

# Get the database and collection
# db = client.my_chatbot_database
# collection = db.my_chatbot_collection

# Insert a document into the collection
# document = {"message": "Hello, world!"}
# result = collection.insert_one(document)
# print(result.inserted_id)

# Find all documents in the collection
# documents = collection.find()
# for document in documents:
#    print(document)

# Start the bot

# Telegram logging function

updater.start_polling()

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot('6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c')

@bot.message_handler(func=lambda message: True)
def log_message(message):
    logging.info(f'{message.chat.username}: {message.text}')

bot.polling()