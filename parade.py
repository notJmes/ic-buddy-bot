import re
import time
import json
from datetime import datetime

## TEST DATA 
'''
These are the message templates for us to test our functions
'''

ps = """
DIS WING FIRST PARADE STATE CONDUCTED ON 160224 @ 0550

CADET TOTAL STENGTH: 54/55

NOT IN CAMP: 1

1) ME4-T JOEY SEE - 2D MC, CORNEA INFECTION (15/02/24 - 16/02/24)

REPORT SICK: 0

1) ME4-T HAGEN LI - VOMIT, DIARRHEA

MEDICAL APPOINTMENT: 5

1) ME4-T TIMOTHY SEOW - PHYSIOTHERAPY, SAFTI MI MEDICAL CENTRE, 0940H (16/02/24 - 16/02/24)
2) ME4-T JOEY SEE - DENTAL APPOINTMENT, ZHONGSAN MALL, 1200H (16/02/24 - 16/02/24)
3) ME4-T NICKOLAS TING - DENTAL APPOINTMENT, SAFTI MI MEDICAL CENTRE, 0930H (22/02/24 - 22/02/24)
4) ME4-T DARREN TOH - DERMATOLOGIST CONSULTATION, CGH DERMATOLOGY CLINIC, 0930H (23/02/24 - 23/02/24)
5) ME4-T CAELAN LEE - DENTAL TREATMENT, NUH DENTAL CENTRE, 1200H (27/02/24 - 27/02/24)

STATUS: 2

1) ME4-T LING ZHI PENG - 3D LD (14/02/24 - 16/02/24)
2) ME4-T TIMOTHY SEOW - 3D EXCUSE HEAVY LOAD AND UPPER LIMB (14/02/24 - 16/02/24)

OTHERS: 5

1) ME4-T CLEMENT LOY - PES B4, PERM EX RMJ
2) ME4-T BRYAN BEH WAH JUN - C9, EX HEAVY LOAD
3) ME4-T LING ZHI PENG - C2L2
4) ME4-T TOH YEW SIANG - C9
5) ME4-T ANDY SIM - UNIVERSITY INTERVIEW, SUSS, 1400H - 1800H (20/02/24 - 20/02/24)

REMARKS: 0
        """

ps_autocomplete = """
DIS WING FIRST PARADE STATE CONDUCTED ON 160224 @ 0550

CADET TOTAL STENGTH: 54/55

NOT IN CAMP: 1

1) ME4-T JOEY SEE - 2D MC, CORNEA INFECTION (15/02/24 - 16/02/24)

REPORT SICK: 0

1) ME4-T HAGEN LI - VOMIT, DIARRHEA

MEDICAL APPOINTMENT: 5

1) [tim] - PHYSIOTHERAPY, SAFTI MI MEDICAL CENTRE, 0940H (16/02/24 - 16/02/24)
2) ME4-T JOEY SEE - DENTAL APPOINTMENT, ZHONGSAN MALL, 1200H (16/02/24 - 16/02/24)
3) ME4-T NICKOLAS TING - DENTAL APPOINTMENT, SAFTI MI MEDICAL CENTRE, 0930H (22/02/24 - 22/02/24)
4) ME4-T DARREN TOH - DERMATOLOGIST CONSULTATION, CGH DERMATOLOGY CLINIC, 0930H (23/02/24 - 23/02/24)
5) ME4-T CAELAN LEE - DENTAL TREATMENT, NUH DENTAL CENTRE, 1200H (27/02/24 - 27/02/24)

STATUS: 2

1) ME4-T LING ZHI PENG - 3D LD (14/02/24 - 16/02/24)
2) ME4-T TIMOTHY SEOW - 3D EXCUSE HEAVY LOAD AND UPPER LIMB (14/02/24 - 16/02/24)

OTHERS: 5

1) [clement] - PES B4, PERM EX RMJ
2) ME4-T BRYAN BEH WAH JUN - C9, EX HEAVY LOAD
3) ME4-T LING ZHI PENG - C2L2
4) ME4-T TOH YEW SIANG - C9
5) [andy] - UNIVERSITY INTERVIEW, SUSS, 1400H - 1800H (20/02/24 - 20/02/24)

REMARKS: 0
        """

#######################





## Generates the first parade based on the previous parade data
def generate(type='first', clean=False, time='UNDEFINED', total_strength=55, prev={}):
    log = ''

    # Empty template to work on
    base = """
DIS WING {type} PARADE STATE CONDUCTED ON {date} @ {time}

CADET TOTAL STENGTH: {strength}/{total_strength}

NOT IN CAMP: {notInCampCount}

{notInCampList}

REPORT SICK: {reportSickCount}

{reportSickList}

MEDICAL APPOINTMENT: {medApptCount}

{medApptList}

STATUS: {statusCount}

{statusList}

OTHERS: {othersCount}

{othersList}

REMARKS: 0


    """

    

    # For every "list", eg. not in camp, status, medical appointment.., check the date range
    for item in prev:
        if item != 'reportSickList' : # Skip for report sick list (no need date range)
            ls = prev[item]
            tmp = [] # initialise an empty list

            # For every name in each list (status, not in camp..)
            for entry in ls:

                # Use a specific pattern to extract the date ranges in the record
                '''
                Example: ME4-T LING ZHI PENG - 3D LD (14/02/24 - 16/02/24) <--date
                '''
                p = re.compile('[0-9]{2}/[0-9]{2}/[0-9]{2}') 
                dates = p.findall(entry)

                # Convert the 'string' of the date to a readable type by python
                dates = [datetime.strptime(d, '%d/%m/%y').date() for d in dates]
                
                # If today is still within the date range, then include it in the new parade state
                if len(dates) == 0 or dates[0] <= datetime.now().date() <= dates[1]:
                    print('Adding', entry)
                    tmp.append(entry)
                else:
                    # Else, remove it
                    print('Removing', entry)
                    log += f'{item}: Removed {entry}\n'

                
            prev[item] = tmp

    
    
    # Sudo (mini) function to join the list of names to a string for formatting
    convert = lambda x: '\n'.join(x)

    # Filling up the params in the base string and generating a filled template
    new = base.format(reportSickCount=len(prev['reportSickList']),
                      reportSickList=convert(prev['reportSickList']),
                      medApptCount=len(prev['medApptList']),
                      medApptList=convert(prev['medApptList']),
                      statusCount=len(prev['statusList']),
                      statusList=convert(prev['statusList']),
                      othersCount=len(prev['othersList']),
                      othersList=convert(prev['othersList']),
                      notInCampCount=len(prev['notInCampList']),
                      notInCampList=convert(prev['notInCampList']),
                      date=datetime.now().strftime('%d%m%y'),
                      time=time,
                      strength=total_strength-len(prev['notInCampList']),
                      total_strength=total_strength,
                      type = type.upper())

    return new, log

# Save the state 
def cache(parade_state):

    patterns = {'notInCampList':'(?<=NOT IN CAMP: )[0-9]{1,2}(.*\n)*(?=REPORT)',
                'reportSickList':'(?<=REPORT SICK: )[0-9]{1,2}(.*\n)*(?=MEDICAL)',
                'medApptList':'(?<=MEDICAL APPOINTMENT: )[0-9]{1,2}(.*\n)*(?=STATUS)',
                'statusList':'(?<=STATUS: )[0-9]{1,2}(.*\n)*(?=OTHERS)',
                'othersList':'(?<=OTHERS: )[0-9]{1,2}(.*\n)*(?=REMARKS)'}
    out = {}
    for pattern in patterns:
        p = re.compile(patterns[pattern])
        try:
            extracted = p.search(parade_state).group(0).split('\n\n', 1)[-1].strip()
            out[pattern] = [item[3:] for item in extracted.split('\n')]
        except:
            out[pattern] = None
    
    return out

def add(parade_state, update_list, data):
    new_line = autocomplete(data)
    parade_state[update_list].append(new_line)

    with open('parade.json', 'w') as f:
        json.dump(parade_state, f, indent=4)

    return parade_state

def modify(parade_state, update_list, name, new_entry):
    new_entry = autocomplete(new_entry)
    index = parade_state[update_list].index(name)
    parade_state[update_list][index] = new_entry
    
    with open('parade.json', 'w') as f:
        json.dump(parade_state, f, indent=4)
 
    return new_entry
## Replace short-form names in [] with rank & full names of cadets 

def delete(parade_state, update_list, name):
    parade_state = parade_state[update_list].remove(name)

    with open('parade.json', 'w') as f:
        json.dump(parade_state, f, indent=4)
        

def autocomplete(message): 
 
  # Find all occurences of short-form name in parade state message 
  # Save them all in a list called lookup_namelist 
  lookup_namelist = re.findall(r"\[[a-zA-Z ]+\]", message) 
 
  # Create a list of full names of all cadets 
  fullname_list = create_namelist() 
 
  # Check through each short-form name in lookup_namelist 
  for name in lookup_namelist: 
 
    # Get full name of cadet based on short-form name 
    full_name = lookup_name(name, fullname_list) 
 
    # Raise error if full name is not found 
    if full_name == None: 
      return f'Error! Invalid name: {name}!' 
    else: 
      # Otherwise, replace short-form name with rank and full name of cadet 
      message = message.replace(name, f'ME4-T {full_name}') 
 
  return message

## Create a list of full names of cadets 
def create_namelist(): 
 
  # Open file containing full names of all caders 
  cadet_names = open('cadet_names.txt','r') 
 
  # Save contents as a string in namelist. 
  ''' 
  Eg: 
  JOHN DOE 
  JANE DOE 
  ''' 
  namelist = cadet_names.read() 
  cadet_names.close() 
 
  # Seperate namelist by newline character 
  # Example output: ['JOHN DOE', 'JANE DOE'] 
  return namelist.split('\n')

## Compare short-form name against list of full names 
def lookup_name(name, fullname_list): 
 
  # Remove [ and ] from short-form name, change it to UPPERCASE 
  name = name.replace('[','') 
  name = name.replace(']','') 
  name = name.upper() 
   
  # Check through list of full names 
  for full_name in fullname_list: 
 
    # If short-form name appears in list of full names, 
    if name in full_name: 
 
      # output the full name  
      return full_name 
       
  # Otherwise, output None 
  return None

if __name__ == '__main__':
    
    
    
    print('[+] TESTING CACHE')

    data = cache(ps)

    with open('parade.json', 'w') as f:
        json.dump(data, f, indent=4)

    with open('parade.json', 'r') as f:
        data = json.load(f)

    time.sleep(1)
    print('[+] TESTING GENERATION')

    new = generate(prev=data)
    print(new)

    time.sleep(1)
    print('[+] TESTING AUTOCOMPLETE')

    data = autocomplete(ps_autocomplete)
    print(data)

    time.sleep(1)
    print('[+] TESTING Add')
    print()

    updated = add(cache(ps), 'notInCampList', '[russell] - 3D MC, HIV, (20/02/24-22/02/24)')
    print(updated)
