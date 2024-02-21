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

def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('Parade State')
    last = types.KeyboardButton('Roster')
    markup.add(first)
    markup.add(last)
    return markup

def parade_state_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('Add Entry')
    second = types.KeyboardButton('Modify Entry')
    last = types.KeyboardButton('Generate')
    markup.add(first)
    markup.add(second)
    markup.add(last)
    return markup

def add_modify_entry_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    first = types.KeyboardButton('Not in Camp')
    second = types.KeyboardButton('Report Sick')
    third = types.KeyboardButton('Medical Appt')
    fourth = types.KeyboardButton('Status')
    fifth = types.KeyboardButton('Others')
    sixth = types.KeyboardButton('Back')
    markup.add(first)
    markup.add(second)
    markup.add(third)
    markup.add(fourth)
    markup.add(fifth)
    markup.add(sixth)
    return markup

def select_names_markup(name_list):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in name_list:
        markup.add(types.KeyboardButton(name))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu', reply_markup=start_menu_markup())
    bot.register_next_step_handler(message, start_menu_choice)

def start_menu_choice(message):
    if message.text.strip()=="Parade State":
        bot.reply_to(message, f'Select an option:', reply_markup=parade_state_menu_markup())
        bot.register_next_step_handler(message, parade_state_menu)
#    else:
#        roster call function :)

def parade_state_menu(message):

    if message.text.strip() == '/start':
        bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu', reply_markup=start_menu_markup())
        return bot.register_next_step_handler(message, start_menu_choice)

    if message.text.strip() == "Generate":
        bot.register_next_step_handler(message, generate_type)
        bot.reply_to(message, 'What type of parade state do you want?', reply_markup=start_markup_parade_type())
    elif message.text.strip() == "Add Entry":
        bot.register_next_step_handler(message, add_entry_menu)
        bot.reply_to(message, 'Which list would you like to add to?', reply_markup=add_modify_entry_markup())
    else:
        bot.register_next_step_handler(message, modify_entry_menu)
        bot.reply_to(message, 'Which list would you like to modify?', reply_markup=add_modify_entry_markup())

    
# def generate(message):

    
#     bot.register_next_step_handler(message, generate_type)

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

def add_entry_menu(message):

    update_list = message.text.strip()
    parade_state = {}

    # Open the JSON file containing previous parade state data
    with open('parade.json', 'r') as f: 
        try:
            parade_state = json.load(f)
        except:
            parade_state = parade.generate()

    if update_list == 'Not in Camp':
        update_list = 'notInCampList'
    elif update_list == 'Report Sick':
        update_list = 'reportSickList'
    elif update_list == 'Medical Appt':
        update_list = 'medApptList'
    elif update_list == 'Status':
        update_list = 'statusList'
    elif update_list == 'Others':
        update_list = 'othersList'
    else:
        bot.reply_to(message, f'Select an option:', reply_markup=parade_state_menu_markup())
        return bot.register_next_step_handler(message, parade_state_menu)


    
    bot.reply_to(message,'\n'.join(parade_state[update_list]))
    bot.send_message(message.chat.id, 'Enter details:')
    bot.register_next_step_handler(message, add_entry, parade_state, update_list)

    

def add_entry(message, parade_state, update_list):
    data = message.text.strip()
    updated_parade_state = parade.add(parade_state, update_list, data)
    bot.reply_to(message, '\n'.join(updated_parade_state[update_list]))

def modify_entry_menu(message):
    
    update_list = message.text.strip()
    parade_state = {}

    # Open the JSON file containing previous parade state data
    with open('parade.json', 'r') as f: 
        try:
            parade_state = json.load(f)
        except:
            parade_state = parade.generate()

    if update_list == 'Not in Camp':
        update_list = 'notInCampList'
    elif update_list == 'Report Sick':
        update_list = 'reportSickList'
    elif update_list == 'Medical Appt':
        update_list = 'medApptList'
    elif update_list == 'Status':
        update_list = 'statusList'
    elif update_list == 'Others':
        update_list = 'othersList'
    else:
        bot.reply_to(message, f'Select an option:', reply_markup=parade_state_menu_markup())
        return bot.register_next_step_handler(message, parade_state_menu)

    selected_list = parade_state[update_list]

    bot.reply_to(message, "Select an entry to modify", reply_markup=select_names_markup(selected_list))
    bot.register_next_step_handler(message, modify_entry, parade_state, update_list)

def modify_entry(message, parade_state, update_list):
    name = message.text.strip()

    def del_edit_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for item in ['Edit','Delete']:
            markup.add(types.KeyboardButton(name))
        return markup

    bot.reply_to(message, f"What would you like to do?", reply_markup=del_edit_markup())
    bot.register_callback_query_handler(message, del_edit, parade_state, update_list, name)

def del_edit(message, parade_state, update_list, name):
    answer = message.text.upper()
    if 'DELETE' in answer.upper():
        parade.delete(parade_state, update_list, name)
        bot.reply_to(message, f"Successfully deleted\n<code>{name}</code>\n", parse_mode="HTML")
    else:
        bot.reply_to(message, f"Submit your new changes for \n<code>{name}</code>\n", parse_mode="HTML")
        bot.register_next_step_handler(message, modify_entry_save, parade_state, update_list, name)

def modify_entry_save(message, parade_state, update_list, name):
    new_entry = message.text.strip()
    
    new_entry = parade.modify(parade_state, update_list, name, new_entry)

    bot.reply_to(message, f"Congrats! updated \n<code>{name}</code>\nto\n<code>{new_entry}</code>\n", parse_mode="HTML")

c1 = types.BotCommand(command='start', description='Pull up the start menu')

bot.set_my_commands([c1])

bot.polling()