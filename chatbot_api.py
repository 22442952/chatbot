from flask import Flask, render_template, request
import requests
from pymongo import MongoClient

# Telegram bot API token
TOKEN = '6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c'

# MongoDB connection string
client = MongoClient("mongodb://localhost:27017/")

# Flask application
app = Flask(__name__)

# Route to handle incoming Telegram messages
@app.route('/{}'.format(TOKEN), methods=['POST'])
def webhook():
    # Parse the incoming message data
    update = request.get_json()
    message = update['message']
    
    # Get the user ID and message text
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    username = message['from']['username']
    text = message['text']
    
    # Check if the message is a location request
    if text.lower() == '/location':
        # Ask the user to share their location
        response = {
            'chat_id': chat_id,
            'text': 'Please share your location.',
            'reply_markup': {
                'keyboard': [[{
                    'text': 'Share location',
                    'request_location': True
                }]],
                'one_time_keyboard': True
            }
        }
        send_message(response)
        return 'OK', 200
    
    # Check if the message is a manual request
    if text.lower() == '/manual':
        # Ask the user to enter their location
        response = {
            'chat_id': chat_id,
            'text': 'Please enter your location (e.g. "New York City").'
        }
        send_message(response)
        return 'OK', 200
    
    # Send the message to OpenWeatherMap API to get weather data
    url = 'https://api.openweathermap.org/data/2.5/weather'
    if 'location' in message:
        lat, lon = message['location']['latitude'], message['location']['longitude']
        params = {'lat': lat, 'lon': lon}
    else:
        params = {'q': text}
    params['units'] = 'imperial'
    params['appid'] = '72203176d99513da49ddb482585eb6f9'
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract the weather data
    location = data['name']
    temperature = data['main']['temp']
    description = data['weather'][0]['description']
    
    # Store the message and weather data in MongoDB
    db = client['chat_history']
    collection = db['messages']
    message_data = {
        'chat_id': chat_id,
        'user_id': user_id,
        'username': username,
        'timestamp': message['date'],
        'message_text': text,
        'location': location,
        'temperature': temperature,
        'description': description
    }
    collection.insert_one(message_data)
    
    # Send the weather data back to the user
    response = {
        'chat_id': chat_id,
        'text': 'The temperature in {} is {}°F and {}'.format(location, temperature, description)
    }
    send_message(response)
    return 'OK', 200

# Function to send a message using the Telegram bot API
def send_message(response):
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(TOKEN)
    headers = {'Content-type': 'application/json'}
    requests.post(url, headers=headers, json=response)

# Route to display the chat history
@app.route('/')
def index():
    # Get the chat history from MongoDB
    db = client['chat_history']
    collection = db['messages']
   
    # Query the messages collection and sort by timestamp in descending order
    messages = collection.find().sort('timestamp', -1)
    
    # Render the chat history template with the messages
    return render_template('chat_history.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
