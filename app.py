import logging
import json
import re
# import os
from pymongo import MongoClient, DESCENDING
import pymongo
import urllib
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# # Manual MongoDB connection credentials and SSL/TLS certificate paths from environment variables
# mongo_host = os.environ.get('MONGO_HOST', 'localhost')
# mongo_port = int(os.environ.get('MONGO_PORT', '27017'))
# mongo_user = os.environ.get('MONGO_USER', '')
# mongo_pass = os.environ.get('MONGO_PASS', '')
# ssl_cert_path = os.environ.get('SSL_CERT_PATH', '')

# # Create a MongoDB client and connect securely
# client = MongoClient(
#     host=mongo_host,
#     port=mongo_port,
#     username=mongo_user,
#     password=mongo_pass,
#     ssl=True,
#     ssl_certfile=ssl_cert_path,
#     ssl_cert_reqs='CERT_NONE'
# )

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

# Define the error handler
def error_handler(update: Update, context: CallbackContext):
    logging.error(msg="Exception occurred", exc_info=context.error)

# Create the Telegram bot
updater = Updater(token='6151346084:AAHSUdphrAvNMIPx5wtpBiGRmtOM79gqGqk', use_context=True)

# Register the error handler
updater.dispatcher.add_error_handler(error_handler)

# Connect local MongoDB for function test
client = pymongo.MongoClient("mongodb+srv://test_user:"+urllib.parse.quote("P@ssw0rd")+"@cluster0.jhnr6tf.mongodb.net/?retryWrites=true&w=majority")
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

    # Check if the JSON data has already been exist
    if collection.count_documents({}) == 0:
        with open('data/career_paths.json') as f:
            data = json.load(f)
            for item in data:
                collection.insert_one(item)
            logging.info('Inserted sample data into MongoDB collection')
    else:
        logging.info('JSON data already imported into MongoDB collection')

# Close the MongoDB connection
# client.close()

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the IT Career Bot! What can I help you?")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You can ask me about different kind of IT job and I'll suggest you with some require skill.")
    
def end(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I hope these information could help you, bye")

def add_response(update, context):
    """Add a new response to the database."""
    # Get the keywords and response from the user input
    user_input = context.args
    keywords = user_input[0:2]
    response = user_input[3:]

    # Join the keywords and response into strings
    keywords_str = " ".join(keywords)
    response_str = " ".join(response)
   
    # Save the new response to the database
    response_data = {
        'keywords': keywords_str,
        'response': response_str
    }
    collection.insert_one(response_data)
     
     # Send a confirmation message to the user
    # doc = {"keywords": keywords, "response": response}
    # collection.insert_one(doc)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks, I've added that to my responses.")

# Define search location and method   
def search(update, context):
   
    keywords = update.message.text.split()
    
    # client = MongoClient('mongodb://localhost:27017/')
    db = client['chatbot_db']
    collection = db['response']
    regex = re.compile('|'.join(keywords), re.IGNORECASE)
    query = {"keywords": {"$all": [regex]}}
    result = collection.find_one(query, sort=[('_id', DESCENDING)])
    print(result)
    context.bot.send_message(chat_id=update.effective_chat.id, text=result["keywords"])

# Set up response message with different search result    
def handle_message(update, context):
    """Handle incoming messages."""
    message = update.message.text.lower()
    found = False
    for response in collection.find():
        keywords = response['keywords'].split()
        if all(keyword in message for keyword in keywords):
            context.bot.send_message(chat_id=update.effective_chat.id, text=response['response'])
            # context.bot.send_message(chat_id=update.effective_chat.id, text="Here's some more information:\n{}".format(response))
            found = True
            break
        elif any(keyword.startswith(message) for keyword in keywords):
                context.bot.send_message(chat_id=update.effective_chat.id, text=response['response'])
                # context.bot.send_message(chat_id=update.effective_chat.id, text="Here's some more information:\n{}".format(response))
                found = True
                break
    
    if not found:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't find any information about this keyword.")
            
# Set up the Telegram bot handlers
def main():
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("add_response", add_response))
    dispatcher.add_handler(CommandHandler("end", end))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()