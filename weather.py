import requests
from pymongo import MongoClient
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_logs']
collection = db['logs']

# Telegram bot token
bot = telegram.Bot(token='6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c')

# Function to handle /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, I'm a weather chatbot! Send me the name of a city and I'll tell you the current weather conditions.")

# Function to handle user input and retrieve weather data from Openweather API
def get_weather(update, context):
    city = ' '.join(context.args)
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=72203176d99513da49ddb482585eb6f9'
    response = requests.get(url).json()
    if response['cod'] == 200:
        weather = response['weather'][0]['description']
        temp = response['main']['temp']
        message = f"The weather in {city} is {weather} and the temperature is {temp} Kelvin."
    else:
        message = "Sorry, I couldn't retrieve weather data for that city."
    # Insert a new chat log into the database
    collection.insert_one({'user': update.effective_user.username, 'message': city})
    # Send the weather data to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Function to handle user messages and search chat logs
def search_logs(update, context):
    query = update.message.text
    results = collection.find({'message': {'$regex': query}})
    if results.count() > 0:
        message = "Here are some chat logs that match your query:\n\n"
        for result in results:
            message += f"{result['user']}: {result['message']}\n"
    else:
        message = "Sorry, I couldn't find any chat logs that match your query."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    # Create the Telegram bot
    updater = Updater(token='6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c', use_context=True)
    dispatcher = updater.dispatcher

    # Define command and message handlers
    start_handler = CommandHandler('start', start)
    weather_handler = CommandHandler('weather', get_weather)
    search_handler = MessageHandler(Filters.text & (~Filters.command), search_logs)

    # Add the handlers to the dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(weather_handler)
    dispatcher.add_handler(search_handler)

    # Start the bot
    updater.start_polling()

if __name__ == '__main__':
    main()
