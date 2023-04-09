import logging
import json
import pymongo
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Set up MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['chatbot_db']
collection = db['career_paths']


if 'career_paths' not in db.list_collection_names():
    # Create the MongoDB collection
    try:
        collection = db.create_collection('career_paths')
        logging.info('Created MongoDB collection')
    except pymongo.errors.CollectionInvalid:
        # Collection already exists, retrieve it instead
        collection = db['career_paths']
        logging.info('Retrieved MongoDB collection')
else:
    # Retrieve the existing collection
    collection = db['career_paths']
    logging.info('Retrieved MongoDB collection')
    
    # Load the sample data from the JSON file
    with open('data/career_paths.json') as f:
        data = json.load(f)

    # Insert the sample data into the MongoDB collection
    collection.insert_many(data)
    logging.info('Inserted sample data into MongoDB collection')

# Define the start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! I can help you with information about IT career paths. Just send me a message with a keyword to get started.')

# Define the message handler
def message(update, context):
    keyword = update.message.text.lower()

    # Query the MongoDB collection for information about the keyword
    result = collection.find_one({'keyword': keyword})

    if result:
        context.bot.send_message(chat_id=update.effective_chat.id, text=result['information'])
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, I couldn\'t find any information about that keyword.')

# Set up the command and message handlers
updater = Updater('6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c', use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, message))

# Start the bot
updater.start_polling()
updater.idle()