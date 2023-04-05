import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from pymongo import MongoClient
import logging
import telebot

# Connect to MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['telegram_chatbot']
users = db['users']
interactive_data = db['interactive_data']

# Telegram bot token
bot = telegram.Bot(token='6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c')

# Command handler to register a new user
def start(update, context):
    user_id = update.message.chat_id
    user_name = update.message.chat.first_name
    
    # Check if user is already registered
    if users.count_documents({'user_id': user_id}) == 0:
        # Insert new user into MongoDB
        user_data = {'user_id': user_id, 'user_name': user_name}
        users.insert_one(user_data)
        update.message.reply_text('You have been registered!')
    else:
        update.message.reply_text('You are already registered!')

# Command handler to start the interactive quiz
def start_quiz(update, context):
    user_id = update.message.chat_id
    
    # Check if user has already started the quiz
    if interactive_data.count_documents({'user_id': user_id}) == 0:
        # Insert new quiz data into MongoDB
        quiz_data = {
            'user_id': user_id,
            'current_question': 0,
            'correct_answers': 0
        }
        interactive_data.insert_one(quiz_data)
        update.message.reply_text('Welcome to the quiz! Here is your first question...')
    else:
        update.message.reply_text('You have already started the quiz!')

# Message handler to process quiz answers
def process_answer(update, context):
    user_id = update.message.chat_id
    user_answer = update.message.text.lower()
    
    # Check if user is in the middle of the quiz
    if interactive_data.count_documents({'user_id': user_id}) > 0:
        quiz_data = interactive_data.find_one({'user_id': user_id})
        current_question = quiz_data['current_question']
        
        # Check if user's answer is correct
        if user_answer == quiz_questions[current_question]['answer'].lower():
            quiz_data['correct_answers'] += 1
            interactive_data.update_one({'user_id': user_id}, {'$set': {'correct_answers': quiz_data['correct_answers']}})
            update.message.reply_text('Correct!')
        else:
            update.message.reply_text('Incorrect.')
            
        # Check if there are more questions in the quiz
        if current_question < len(quiz_questions) - 1:
            next_question = quiz_questions[current_question + 1]['question']
            interactive_data.update_one({'user_id': user_id}, {'$set': {'current_question': current_question + 1}})
            update.message.reply_text(next_question)
        else:
            final_score = quiz_data['correct_answers']
            interactive_data.delete_one({'user_id': user_id})
            update.message.reply_text(f'Quiz complete! Your final score is {final_score}.')
    else:
        update.message.reply_text('You have not started the quiz yet.')

# Set up the Telegram bot handlers
updater = Updater(token='6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start_quiz', start_quiz))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_answer))

# Quiz questions
quiz_questions = [
    {'question': 'What is the capital of France?', 'answer': 'Paris'},
    {'question': 'What is the largest country in the world by land area?', 'answer': 'Russia'},
    {'question': 'What is the smallest country in the world by land area?', 'answer': 'Vatican City'}
]

# Start the bot
updater.start_polling()

#logging function

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot('6028594612:AAGVp2lE1aJtlcx6K1iy-ScAz3Bh0M9_T2c')

@bot.message_handler(func=lambda message: True)
def log_message(message):
    logging.info(f'{message.chat.username}: {message.text}')

bot.polling()
