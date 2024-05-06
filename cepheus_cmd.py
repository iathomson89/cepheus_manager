import sqlite3
import csv
from tabulate import tabulate
import json
from datetime import datetime


# Define the SQLite database filename

active_crew_id = None

with open('./data_sources/defaults.json', 'r') as file:
    data = json.load(file)
    DATABASE_FILE = data['DATABASE_FILE']
    default_date = data['default_date']
    active_crew_id = data['default_crew']
    if active_crew_id is None:
        print('No default crew set. You can set this by assigning an ID number in "defaults.json".')
    else:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''SELECT crew_name FROM crews WHERE crew_id = ?''', (active_crew_id,))
        active_crew_name = cursor.fetchone()[0]
        conn.close()
        print(f"The active crew is {active_crew_name}, (crew ID: {active_crew_id}).")


def connect_to_database():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

def set_active_crew(input_int):
    """Sets the active_crew variable. Should be the first function called at start of session"""
    active_crew_id = input_int

def get_crews():
    """Retrieve all crews from the database."""
    # Establish connection to the SQLite database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Query the database to retrieve all crews
    cursor.execute('''SELECT * FROM Crews''')
    crews = cursor.fetchall()  # Fetch all crews

    # Close the connection
    conn.close()

    return crews

def get_crew_name(crew_id):
    """Retrieve the name of the crew with the given ID."""
    # Establish connection to the SQLite database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Query the database to retrieve the crew name
    cursor.execute('''SELECT crew_name FROM Crews WHERE crew_id = ?''', (crew_id,))
    crew_name = cursor.fetchone()[0]  # Fetch the crew name

    # Close the connection
    conn.close()

    return crew_name

def get_roles():
    """Fetch roles from the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT role_id, role_name, default_salary FROM Roles''')
    roles = cursor.fetchall()
    conn.close()
    return roles

def add_crew(crew_name, start_date):
    """Add a new crew to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Crews (crew_name, start_date, current_date) VALUES (?,?,?)''', (crew_name,start_date, start_date))
    conn.commit()
    conn.close()

def add_role(role_name, default_salary):
    """Add a new role to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Roles (role_name, default_salary) VALUES (?, ?)''', (role_name, default_salary))
    conn.commit()
    conn.close()

#Parse SEC files from cepheusjournal.com subsector generator
def sec_parse(sec_string):
    '''Takes a 57 character input string for a world from an SEC mapping format, and parses into a 
    list of features for easy import into database.
    Note: Remember that sec_list[5] is a list and needs further parsing on database entry. '''
    if len(sec_string) != 57:
        print('Error. SEC string must be exactly 57 characters long.')
        return
    else:
        try:
            world_name = sec_string[0:14].strip()
            col_coord = int(sec_string[14:16])
            row_coord = int(sec_string[16:18])
            UWP_code = sec_string[19:28]
            base_code = sec_string[30:31].strip()
            trade_code_list = sec_string[32:48].split()
            travel_zone = sec_string[48:49].strip()
            pop_mod = int(sec_string[51:52])
            belts = int(sec_string[52:53])
            gas_giants = int(sec_string[53:54])
            allegiance = sec_string[55:57]

            sec_list = [
                world_name,
                col_coord,
                row_coord,
                UWP_code,
                base_code,
                trade_code_list,
                travel_zone,
                pop_mod,
                belts,
                gas_giants,
                allegiance
            ]

            return sec_list
        
        except:
            print('Invalid string. Please SEC input is correct')


#Basic function parsing psuedohex
def hex_parse(char):
    char = str(char)
    if len(str(char)) > 1:
        print('Please input a single character value')
        return
    elif char.isdigit():
        return int(char)
    else:
        return ord(char.upper()) - ord('A') + 10
    
def UWP_parse(UWP):
    '''Parses a UWP intp a list for entry into database.'''

    return [hex_parse(char) for char in UWP if char != '-']


#Basic function for adding a planet to the database.
def add_planet(sec_string):
    '''Adds a planet to the planets table, with a SEC string as input.'''
    sec_list = sec_parse(sec_string)


    name = sec_list[0]
    conn =connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM Planets WHERE planet_name = ?''', (name,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same planet exist, insert the new record
    if existing_records == 0:
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO Planets (
                planet_name,
                column_coordinate,
                row_coordinate,
                base_code,
                travel_zone,
                population_modifier,
                planetoid_belts,
                gas_giants,
                allegiance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    sec_list[0],
                    sec_list[1],
                    sec_list[2],
                    sec_list[4],
                    sec_list[6],
                    sec_list[7],
                    sec_list[8],
                    sec_list[9],
                    sec_list[10]
                )
                )
        except:
             print(f'Something went wrong with parsing the basic list for {name}.')
        
        # Update UUP Code Values
        try:
            UWP_list = UWP_parse(sec_list[3])
            cursor.execute('''
                           UPDATE Planets
                           SET starport_quality = ?,
                            planet_size = ?,
                            atmosphere_type = ?,
                            hydrosphere_percentage = ?,
                            population_level = ?,
                            government_type = ?,
                            law_level = ?,
                            tech_level = ?
                           WHERE planet_name = ?
                           ''',(*UWP_list, name))


        except:
            print(f'Something went wrong parsing the UPP code for {name}.')

        # Update trade codes

        try:
            trade_codes = sec_list[5]
            for k in trade_codes:
                if k == 'As':
                    code = "Ast"
                elif k == 'In':
                    code = 'Ind'
                else:
                    code = k
                cursor.execute(f'''
                        UPDATE Planets
                            SET {code} = 1
                            WHERE planet_name = ?
                    ''',(name,)
                )
            allcodes = ['Ag', 'As', 'Ba', 'De', 'Fl', 'Ga', 'Hi', 'Ht', 'Ic', 'In', 'Lo', 'Lt', 'Na', 'Ni', 'Po', 'Ri', 'Wa', 'Va']
            
            for m in allcodes: 
                if m in trade_codes:
                    if m == 'As':
                        nullcode = "Ast"
                    elif m == 'In':
                        nullcode = 'Ind'
                    else:
                        nullcode = m
                    cursor.execute(f'''
                        UPDATE Planets
                            SET {nullcode} = 0
                            WHERE planet_name = ?
                    ''',(name,))

        except:
            print(f'Something went wrong parsing the trade codes')
        conn.commit()
        conn.close()
        print(f'Added planet {name} to database.')
        return


    else:
        print(f'''Planet {name} already exists. Did not add planet to database.''')
        return



def mass_import_planets(sec_file):
    '''Takes a file from the data_sources folder, and imports it to the planets table'''
    with open('./data_sources/' + sec_file, 'r') as file:
        for line in file:
            add_planet(line.strip())


#Guided creation of a crew
def make_crew():
    """Create a crew step-by-step for a new campaign."""
    print("Creating a new crew")
    print("=========================")
    crew_name = input("Please enter the name for this crew:")
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''SELECT crew_name FROM crews WHERE crew_name = ? ''', (crew_name,))
    dupe_check = cursor.fetchone()
    conn.close()
    if dupe_check is not None:
        print(f'There is already a crew called {crew_name}. Crew creation cancelled.')
    else:

        #Set dates for crew
        start_date = input(f"Please enter the in-universe start date of the campaign in YYYY-MM-DD format. Leave blank for the default date of {default_date}.")
        if start_date == '':
            start_date = default_date
            print(f"Using default date pf {default_date}.")
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            print(f"Starting date set to {start_date}.")
        except ValueError:
            print(start_date)
            print("Invalid date format. Stopping crew creation")
            return

        confirmation = input(f"Create {crew_name} starting in {start_date}? [Y/N]")
        if "y" in confirmation.lower():
            add_crew(crew_name, start_date)
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute('''SELECT crew_id FROM crews WHERE crew_name = ?''', (crew_name,))
            crew_id = cursor.fetchone()[0]
            set_active_crew(crew_id)
            print(f"{crew_name} added to database with id {crew_id}. Setting to active.")
            conn.close()

        else:
            print("Crew Creation cancelled")

    








#More direct input. For more user-friendly version, use 'Hire Crew'
def add_crew_member(crew_id, member_name, role_id, member_salary):
    """Add a new crew member to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO CrewMembers (crew_id, member_name, role_id, member_salary) VALUES (?, ?, ?, ?)''',
                   (crew_id, member_name, role_id, member_salary))
    conn.commit()
    conn.close()


def hire_crew_member():
    """Walk the user through the process of hiring a new crew member."""
    global active_crew_id
    print("Hiring a New Crew Member")
    print("=========================")

    # Check if there is an active crew
    active_check = False
    while active_check == False:
        if active_crew_id is not None:
            active_crew_name = get_crew_name(active_crew_id)
            proceed_with_hire = input(f"Hirie a new crew member to crew '{active_crew_name}'? [Y/N]")
            if 'y' in proceed_with_hire.lower():
                active_check = True
            else: 
                print('Hiring cancelled.')
                return
        else:
            print("No active crew found.")
            # Display crews table
            crews = get_crews()  # Get crews from the database
            headers = ["ID", "Name"]
            crews_table = tabulate(crews, headers=headers, tablefmt="grid")
            print("Available Crews:")
            print(crews_table)
            # Prompt the user to select an active crew
            active_crew_id = input("Enter the ID of the active crew: ")
            # Set the selected crew as active
            set_active_crew(active_crew_id)
            active_crew_name = get_crew_name(active_crew_id)
            print(f"Active crew set to '{active_crew_name}'.")
            return(active_crew_id)

    # Prompt the user for crew member name
    member_name = input("Enter the name of the new crew member: ")

    # Display roles table with IDs, role names, and salaries
    roles = get_roles()  # Get roles from the database
    headers = ["ID", "Name", "Salary"]
    role_table = tabulate(roles, headers=headers, tablefmt="grid")
    print(role_table)

    # Prompt the user to input the ID of the desired role
    role_id = input("Enter the ID of the desired role: ")
    try:
        role_id = int(role_id)
    except:
        print("Please enter an integer value. Cancelling Hiring.")

    # Get the role name and default salary for the selected role
    role_info = [role for role in roles if role[0] == role_id][0]
    role_name = role_info[1]
    default_salary = role_info[2]

    # Prompt the user to choose whether to use default salary or set a new salary
    default_or_custom = input(f"The default salary of {role_name} is {default_salary}. Use default salary? (yes/no) ")

    if default_or_custom.lower() == 'yes':
        # Use default salary
        member_salary = default_salary
    else:
        # Prompt the user for a new salary
        member_salary = input("Enter the new salary: ")

    # Confirm hiring
    confirm_hire = input(f"Hire {role_name} {member_name} with a salary of {member_salary}? [Y/N]")
    
    if 'y' in confirm_hire.lower():
        # Add the new crew member to the database
        add_crew_member(crew_id=active_crew_id, member_name=member_name, role_id=role_id, member_salary=member_salary)
        print(f"Successfully hired {member_name} as a crew member with role ID {role_id} to crew '{active_crew_name}'.")
    else:
        print("Hiring canceled.")