from pymongo import MongoClient, DESCENDING
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json

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

    # Check if the JSON data has already been imported
    if collection.count_documents({}) == 0:
        # Import the data into the collection
        with open('data/career_paths.json') as f:
            data = json.load(f)
            for item in data:
                collection.insert_one(item)
            logging.info('Inserted sample data into MongoDB collection')
    else:
        logging.info('JSON data already imported into MongoDB collection')

    # Close the MongoDB connection
client.close()

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the IT Career Bot! How can I help you?")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You can ask me about different IT job and I'll suggest you with some require skill.")
    
def add_response(update, context):
    """Add a new response to the database."""
    # Get the keywords and response from the user input
    user_input = context.args
    keywords = user_input[0:2]
    response = user_input[3:]

    # Split the keywords string into separate keywords
    keywords = [keyword.strip() for keyword in ','.join(keywords).split(',')]

    # Save the new response to the database
    response_data = {
        'keywords': " ".join(keywords),
        'response': " ".join(response)
    }
    collection.insert_one(response_data)
     
     # Send a confirmation message to the user
    doc = {"keywords": keywords, "response": response}
    collection.insert_one(doc)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks, I've added that to my responses.")

    
def search(update, context):
    keywords = update.message.text.lower().split()
    client = MongoClient('mongodb://localhost:27017/')
    db = client['chatbot_db']
    collection = db['response']
    query = {"keywords": {"$all": keywords}}
    result = collection.find_one(query, sort=[('_id', DESCENDING)])
    
def handle_message(update, context):
    """Handle incoming messages."""
    message = update.message.text.lower()
    
    for response in collection.find():
        keywords = response['keywords'].split()
        if all(keyword in message for keyword in keywords):
            context.bot.send_message(chat_id=update.effective_chat.id, text=response['response'])
            # context.bot.send_message(chat_id=update.effective_chat.id, text="Here's some more information:\n{}".format(response))
            break
        elif any(keyword.startswith(message) for keyword in keywords):
            context.bot.send_message(chat_id=update.effective_chat.id, text=response['response'])
            # context.bot.send_message(chat_id=update.effective_chat.id, text="Here's some more information:\n{}".format(response))
            break
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't find any information about that keyword.")

def main():
    # Set up the Telegram bot and add handlers
    updater = Updater(token="6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c", use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("add_response", add_response))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()