import telebot # Main telegram bot library
from telebot import types # Extra UI libraries for the bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton # Even more extra UI libraries

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

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['echo'])
def welcome(message):
    bot.reply_to(message, f'{message.from_user.username} said: "{message.text}"')

@bot.message_handler(commands=['jason'])
def welcome(message):
    bot.reply_to(message, 'stupid jason.')

bot.polling()