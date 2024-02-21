import telebot
import datetime

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

bot = telebot.TeleBot(TOKEN)

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



#Use DateTime Library to get the week number for the year
def GetWeekNum():
    current_date = datetime.datetime.now() #Gets current date and time
    week_num = datetime.date(current_date.year,current_date.month, current_date.day).isocalendar()[1] #Gets the current week number of the year
    return week_num


#Rotating the cleaning roster for lvl based on the week number
def RotateCleaningRoster(weeknum, areas, lvl_bunks):
    weeknum = GetWeekNum()      #Call GetWeekNum() function and assign output to variable weeknum
    rotation_num = weeknum % len(lvl_bunks)     #Use the remainder of the weeknumber divided by the number of cleaning areas to rotate
    rotated_lvl_bunks = lvl_bunks[rotation_num:] + lvl_bunks[:rotation_num]     #Rotates the cleaning areas using slice operator
    lvl_cleaningroster = {}     #Create empty dictionary
    for key in rotated_lvl_bunks:       #Adds to the dictionary after the cleaning areas have been rotated
        for value in areas:
            lvl_cleaningroster[key] = value     #Assign the bunk number as dictionary keys for the cleaning area (e.g. {02-10 : Toilet 1} )
            areas.remove(value)     #Remove the value from the areas list after it has been assigned a bunk number
            break                  #Break to exit the child loop and back to the parent loop
    return lvl_cleaningroster       #Return the completed dictionary rotated roster


# if __name__ == '__main__':
#     # Start command handler
#     @bot.message_handler(commands=['start'])
#     def start(message):
#         bot.reply_to(message, 'Welcome! Use /lvl2_roster or /lvl3_roster to generate a cleaning roster for this week.')
        

#     #Generate roster for Level 2
#     @bot.message_handler(commands=['lvl2_roster'])
#     def GenerateRoster(message):
#         weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
#         lvl2_roster = ""            #Create empty roster string
#         cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
#         cleaning_areas_copy[-1] = "Level 1"      #Change the last list value to 'Level 1'
#         lvl2_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl2_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl2_cleaningroster
#         for key, value in lvl2_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
#             lvl2_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl2_roster' as a new line after every iteration
        
#         bot.reply_to(message, 'Level 2 Cleaning Roster for this week:\n' + lvl2_roster) #Output the entire roster as a message in telegram
        

#     #Generate roster for Level 3
#     @bot.message_handler(commands=['lvl3_roster'])
#     def GenerateRoster(message):
#         weeknum = GetWeekNum()      #Call GetWeekNum() function and assign the output to weeknum
#         lvl3_roster = ""            #Create empty roster string
#         cleaning_areas_copy = cleaning_areas[:]   #Make a copy of cleaning_areas list
#         cleaning_areas_copy[-1] = "Level 4"      #Change the last list value to 'Level 4'
#         lvl3_cleaningroster = RotateCleaningRoster(weeknum, cleaning_areas_copy, lvl3_bunks)    #Call RotateCleaningRoster() function with relevant variables and assign the dictionary output to lvl3_cleaningroster
#         for key, value in lvl3_cleaningroster.items():      #Change the dict key and value into an item pair as list values and then loop true with the variables 'key' 'value'
#             lvl3_roster += f"{key} : {value}\n"     #Append the string to the variable 'lvl3_roster' as a new line after every iteration

#         bot.reply_to(message, 'Level 3 Cleaning Roster for this week:\n' + lvl3_roster)     #Output the entire roster as a message in telegram


#     # Error handler
#     @bot.message_handler(func=lambda message: True)
#     def echo_all(message):
#         bot.reply_to(message, "Sorry, I didn't understand that command.")


#     # Polling to start the bot
#     bot.polling()


#################### IGNORE THIS ##############################
'''
# Function to generate roster for bunk rooms
def generate_roster(message):
    roster = ""     # create empty roster first
    for i, bunk in enumerate(lvl3_bunks): # enumerate(bunk_num) returns an iterable where each element is a tuple containing the index of the element and the element itself 
        task = cleaning_areas[i % len(cleaning_areas)]  # The [i % len(cleaning_tasks)] ensures that the resulting index stays within the bounds of the cleaning_tasks list.
        roster += f"{bunk}: {task}\n"  # ensures that each new assignment is appended to the end of the roster string
    bot.reply_to(message, 'Cleaning Roster for this week:\n' + roster)
'''