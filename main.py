import json
import parade

import telebot # Main telegram bot library
from telebot import types # Extra UI libraries for the bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup # Even more extra UI libraries

try:
    with open('token.txt', 'r') as f:
        TOKEN = f.read().strip()

        '''
        1. f contains the data from token.txt
        2. read() will output the data from f
        3. strip() removes any white spaces (spacebar) from the text retrieved from f
        '''
except:
    print('please ensure token.txt is present.')
    exit(0)

data = {}

bot = telebot.TeleBot(TOKEN)

def start_markup_parade_type():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('First ☀️')
    last = types.KeyboardButton('Last 🌙')
    markup.add(first)
    markup.add(last)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu')

@bot.message_handler(commands=['generate'])
def generate(message):

    bot.reply_to(message, 'What type of parade state do you want?', reply_markup=start_markup_parade_type())
    bot.register_next_step_handler(message, generate_type)

def generate_type(message):

    # Extract the parameter "first" or "last"
    state_type = message.text.strip()
    state_type = 'FIRST' if 'F' in state_type.upper() else 'LAST'

    global data
    data[message.from_user.username] = {'state_type': state_type}

    bot.reply_to(message, 'What will the time be in HHMM?', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, generate_time)

def generate_time(message):

    data[message.from_user.username]['state_time'] = message.text.strip()

    bot.reply_to(message, 'What is the total strength?')
    bot.register_next_step_handler(message, generate_strength)

def generate_strength(message):

    try:
        strength = int(message.text.strip())
    except:
        bot.reply_to(message, 'Provide a proper input')
        bot.register_next_step_handler(message, generate_strength)
        return
    global data
    state_type = data[message.from_user.username]['state_type']
    state_time = data[message.from_user.username]['state_time']

    # Open the JSON file containing previous parade state data
    with open('parade.json', 'r') as f: 
        try:
            old_state = json.load(f)
            clean = False
        except:
            clean = True
        
    # Generate
    new, log = parade.generate(state_type, clean=clean, time=state_time, total_strength=strength, prev=old_state)
    bot.reply_to(message, new, parse_mode="HTML")
    bot.reply_to(message, f"The following changes were made:\n```\n{log}\n```", parse_mode="MarkdownV2")

@bot.message_handler(commands=['echo'])
def welcome(message):
    bot.reply_to(message, f'{message.from_user.username} said: "{message.text}"')

@bot.message_handler(commands=['jason'])
def welcome(message):
    bot.reply_to(message, 'stupid jason.')

bot.polling()