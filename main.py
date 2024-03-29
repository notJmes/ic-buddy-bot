import json
import parade
from roster import GetWeekNum, RotateCleaningRoster

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

# {'key':'value'} | {'car':4, 'bike':2}

bot = telebot.TeleBot(TOKEN)

# Creating the menu for first or last parade
def start_markup_parade_type():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('First ☀️')
    last = types.KeyboardButton('Last 🌙')
    markup.add(first)
    markup.add(last)
    return markup

# The inital menu to choose parade state or roster
def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('Parade State')
    last = types.KeyboardButton('Roster')
    markup.add(first)
    markup.add(last)
    return markup

# Parade: Menu for adding, modifying or generating the parade state
def parade_state_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    first = types.KeyboardButton('Add Entry')
    second = types.KeyboardButton('Modify Entry')
    last = types.KeyboardButton('Generate')
    markup.add(first)
    markup.add(second)
    markup.add(last)
    return markup

# Parade: Menu for choosing which list to modify
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

# Parade: Menu to generate buttons with the names
def select_names_markup(name_list):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in name_list:
        markup.add(types.KeyboardButton(name))
    return markup

# Roster: Menu to choose level 1 or 2
def roster_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in ['Level 2', 'Level 3', 'Back']:
        markup.add(types.KeyboardButton(item))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    # Message to send to the user 
    bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu', reply_markup=start_menu_markup())
    # Direct to the next step
    bot.register_next_step_handler(message, start_menu_choice)

def start_menu_choice(message):

    # Depending on the user's choice, parade or roster
    if message.text.strip()=="Parade State":
        # Sends next step if user clicks on parade state
        bot.reply_to(message, f'Select an option:', reply_markup=parade_state_menu_markup())
        bot.register_next_step_handler(message, parade_state_menu)
    elif message.text.strip()=="Roster":   
        # Sends next step if user clicks on the roster
        bot.reply_to(message, f'Select your level to generate a roster for this week:', reply_markup=roster_menu())
        bot.register_next_step_handler(message, roster_lvl_selection)

def parade_state_menu(message):
    # If user does a /start, cancel the menu and bring back to screen
    if message.text.strip() == '/start':
        bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu', reply_markup=start_menu_markup())
        return bot.register_next_step_handler(message, start_menu_choice)

    # Same thing, based on the choice of the user, return the corresponding next step
    if message.text.strip() == "Generate":
        bot.register_next_step_handler(message, generate_type)
        bot.reply_to(message, 'What type of parade state do you want?', reply_markup=start_markup_parade_type())
    elif message.text.strip() == "Add Entry":
        bot.register_next_step_handler(message, add_entry_menu)
        bot.reply_to(message, 'Which list would you like to add to?', reply_markup=add_modify_entry_markup())
    else:
        bot.register_next_step_handler(message, modify_entry_menu)
        bot.reply_to(message, 'Which list would you like to modify?', reply_markup=add_modify_entry_markup())


def generate_type(message):

    # Receives the type of parade state. Extract the parameter "first" or "last"
    state_type = message.text.strip()
    state_type = 'FIRST' if 'F' in state_type.upper() else 'LAST'

    # Storing the user's choices in an object "data"
    data = {}
    data[message.from_user.username] = {'state_type': state_type}

    bot.reply_to(message, 'What will the time be in HHMM?', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, generate_time, data)

def generate_time(message, data):

    # Receives the time from the user
    data[message.from_user.username]['state_time'] = message.text.strip()

    bot.reply_to(message, 'What is the total strength?')
    bot.register_next_step_handler(message, generate_strength, data)

def generate_strength(message, data):

    # Receives total strength from user
    try:
        strength = int(message.text.strip())
    except:
        bot.reply_to(message, 'Provide a proper input')
        bot.register_next_step_handler(message, generate_strength)
        return
    
    state_type = data[message.from_user.username]['state_type']
    state_time = data[message.from_user.username]['state_time']

    # Open the JSON file containing previous parade state data
    with open('parade.json', 'r') as f: 
        try:
            old_state = json.load(f)
            clean = False
        except:
            clean = True
        
    # Generate and send the new parade state to the user
    new, log = parade.generate(state_type, clean=clean, time=state_time, total_strength=strength, prev=old_state)
    bot.reply_to(message, new, parse_mode="HTML")
    # bot.reply_to(message, f"The following changes were made:\n```\n{log}\n```", parse_mode="MarkdownV2")

### TEST COMMANDS ###

@bot.message_handler(commands=['echo'])
def welcome(message):
    bot.reply_to(message, f'{message.from_user.username} said: "{message.text}"')

@bot.message_handler(commands=['jason'])
def welcome(message):
    bot.reply_to(message, 'stupid jason.')

####################


def add_entry_menu(message):
    # Receives decision from the user on which list he wants to add on to
    update_list = message.text.strip()
    parade_state = {}

    # Open the JSON file containing previous parade state data
    with open('parade.json', 'r') as f: 
        try:
            parade_state = json.load(f)
        except:
            parade_state = parade.generate()

    # This if/else translates the button choice to the key in the json file
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
    # Similar to the add menu, but its modifying existing users instead
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

    # Prompts the user to select the cadet to modify
    bot.reply_to(message, "Select an entry to modify", reply_markup=select_names_markup(selected_list))
    bot.register_next_step_handler(message, modify_entry, parade_state, update_list)

def modify_entry(message, parade_state, update_list):
    name = message.text.strip()

    # Prompts users if they want to edit or delete the selected cadet
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

# Start command handler
@bot.message_handler(commands=['roster'])
def roster(message):
    bot.reply_to(message, 'Welcome! Use /lvl2_roster or /lvl3_roster to generate a cleaning roster for this week.')
    

# Define cleaning tasks
cleaning_areas = [
    "Toilet 1",
    "Toilet 2",
    "Toilet 3",
    "Short wing",
    "Long wing",
    "Main staircase",
    "Secondary staircase",
    "Big common area",
    "Small common area 1",
    "Small common area 2",
    "Small common area 3",
    "Level 1 or level 4"
]


# Define room numbers
lvl2_bunks = [
    "02-10", 
    "02-11", 
    "02-12", 
    "02-13", 
    "02-14", 
    "02-16", 
    "02-17",
    "02-18", 
    "02-20", 
    "02-21", 
    "02-22", 
    "02-23"
]

lvl3_bunks = [
    "03-04",
    "03-06",
    "03-07",
    "03-08",
    "03-09",
    "03-11",
    "03-12",
    "03-14",
    "03-16",
    "03-17",
    "03-18",
    "03-19",
    "03-20",
    "03-21"
]



#Generate roster for Level 2
@bot.message_handler(commands=['lvl2_roster'])
def GenerateRoster(message):
    weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
    lvl2_roster = ""            #Create empty roster string
    cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
    cleaning_areas_copy[-1] = "Level 1"      #Change the last list value to 'Level 1'
    lvl2_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl2_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl2_cleaningroster
    for key, value in lvl2_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
        lvl2_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl2_roster' as a new line after every iteration
    
    bot.reply_to(message, 'Level 2 Cleaning Roster for this week:\n' + lvl2_roster) #Output the entire roster as a message in telegram
    

#Generate roster for Level 3
@bot.message_handler(commands=['lvl3_roster'])
def GenerateRoster(message):
    weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
    lvl3_roster = ""            #Create empty roster string
    cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
    cleaning_areas_copy[-1] = "Level 4"      #Change the last list value to 'Level 4'
    lvl3_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl3_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl3_cleaningroster
    for key, value in lvl3_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
        lvl3_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl3_roster' as a new line after every iteration

    bot.reply_to(message, 'Level 3 Cleaning Roster for this week:\n' + lvl3_roster)     #Output the entire roster as a message in telegram

def roster_lvl_selection(message):

    if 'BACK' in message.text.upper():
        bot.reply_to(message, f'Welcome to the IC Buddy Bot! Your all in one stop set of tools to help you on your chores. Go ahead and explore the menu', reply_markup=start_menu_markup())
        return bot.register_next_step_handler(message, start_menu_choice)

    elif '2' in message.text:

        weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
        lvl2_roster = ""            #Create empty roster string
        cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
        cleaning_areas_copy[-1] = "Level 1"      #Change the last list value to 'Level 1'
        lvl2_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl2_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl2_cleaningroster
        for key, value in lvl2_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
            lvl2_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl2_roster' as a new line after every iteration
        
        bot.reply_to(message, 'Level 2 Cleaning Roster for this week:\n' + lvl2_roster) #Output the entire roster as a message in telegram
        
    elif '3' in message.text:

        weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
        lvl3_roster = ""            #Create empty roster string
        cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
        cleaning_areas_copy[-1] = "Level 4"      #Change the last list value to 'Level 4'
        lvl3_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl3_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl3_cleaningroster
        for key, value in lvl3_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
            lvl3_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl3_roster' as a new line after every iteration

        bot.reply_to(message, 'Level 3 Cleaning Roster for this week:\n' + lvl3_roster)     #Output the entire roster as a message in telegram
    
    bot.reply_to(message, f'Select your level to generate a roster for this week:', reply_markup=roster_menu())
    bot.register_next_step_handler(message, roster_lvl_selection)




# Error handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Sorry, I didn't understand that command.")



c1 = types.BotCommand(command='start', description='Pull up the start menu')

bot.set_my_commands([c1])

bot.polling()