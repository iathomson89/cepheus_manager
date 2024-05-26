import sqlite3
from tabulate import tabulate
import json
from datetime import datetime
import os
import math
import cepheus_config as c_con





if c_con.config.active_crew_id is None:
    print('No default crew set. You can set this by assigning an ID number in "defaults.json".')
else:
    conn = sqlite3.connect(c_con.config.DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT crew_name FROM crews WHERE crew_id = ?''', (c_con.config.active_crew_id,))
    active_crew_name = cursor.fetchone()[0]
    conn.close()
    print(f"The active crew is {c_con.get_crew_name(c_con.config.active_crew_id)}, (crew ID: {c_con.config.active_crew_id}).")


def get_roles():
    """Fetch roles from the database."""
    conn = sqlite3.connect(c_con.config.DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT role_id, role_name, default_salary FROM Roles''')
    roles = cursor.fetchall()
    conn.close()
    return roles

def add_crew(crew_name, start_date, start_col, start_row):
    """Add a new crew to the database."""
    conn = c_con.connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Crews (crew_name, start_date, current_date, current_column, current_row) 
                   VALUES (?,?,?,?,?)''', (crew_name, start_date, start_date, start_col, start_row))
    conn.commit()
    conn.close()

def add_role(role_name, default_salary):
    """Add a new role to the database."""
    conn = c_con.connect_to_database()
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
    
def hex_unparse(num):
    if not isinstance(num, int) or num < 0:
        print('Please input a non-negative integer')
        return
    elif num <= 9:
        return str(num)
    else:
        return chr(ord('A') + num - 10)


def UWP_parse(UWP):
    '''Parses a UWP intp a list for entry into database.'''

    return [hex_parse(char) for char in UWP if char != '-']


#Basic function for adding a planet to the database.
def add_planet(sec_string):
    '''Adds a planet to the planets table, with a SEC string as input.'''
    sec_list = sec_parse(sec_string)


    name = sec_list[0]
    sec_col = sec_list[1]
    sec_row = sec_list[2]
    conn = c_con.connect_to_database()
    cursor = conn.cursor()
    #Find planets with the same name
    cursor.execute('''SELECT COUNT(*) FROM Planets WHERE planet_name = ?''', (name,))
    existing_name = cursor.fetchone()[0]

    cursor.execute('''SELECT COUNT(*) FROM Planets 
                   WHERE column_coordinate = ?
                   AND row_coordinate = ?''', (sec_col,sec_row))
    existing_coord = cursor.fetchone()[0]

    # If no records with the same planet exist, insert the new record
    if existing_name == 0 and existing_coord == 0:
        try:
            conn = c_con.connect_to_database()
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
            allcodes = ['Ag', 'As', 'Ba', 'De', 'Fl', 'Ga', 'Hi', 'Ht', 'Ic', 'In', 'Lo', 'Lt', 'Na', 'Ni', 'Po', 'Ri', 'Wa', 'Va']
            for m in allcodes: 
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
        except:
            print(f'Something went wrong parsing the trade codes')
        conn.commit()
        conn.close()
        print(f'Added planet {name} to database.')
        return


    elif existing_name != 0:
        print(f'''Planet {name} already exists. Did not add planet to database.''')
        return
    else:
        print(f'''Planet with coordinates {str(sec_col)},{str(sec_row)} already exists. Did not add planet to database.''')



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
    conn = c_con.connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''SELECT crew_name FROM crews WHERE crew_name = ? ''', (crew_name,))
    dupe_check = cursor.fetchone()
    conn.close()
    if dupe_check is not None:
        print(f'There is already a crew called {crew_name}. Crew creation cancelled.')
    else:

        #Set dates for crew
        start_planet = input('''Please enter the name of the planet the crew starts on.''')
        try:
            conn = c_con.connect_to_database()
            cursor = conn.cursor()
            cursor.execute('''SELECT column_coordinate, row_coordinate FROM Planets WHERE LOWER(planet_name) = LOWER(?)''', (start_planet,))
            start_coords = cursor.fetchone()
            print(f'Starting on {start_planet} with starting coordinates {start_coords[0], start_coords[1]}.')
            conn.close()

        except:
            print('Something went wrong with the coordinates.')
            return

        start_date = input(f'''Please enter the in-universe start date of the campaign in YYYY-MM-DD format. 
                           Leave blank for the default date of {c_con.config.default_date}.''')
        if start_date == '':
            start_date = c_con.config.default_date
            print(f"Using default date pf {c_con.config.default_date}.")
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            print(f"Starting date set to {start_date}.")
        except ValueError:
            print(start_date)
            print("Invalid date format. Stopping crew creation")
            return

        confirmation = input(f"Create {crew_name} starting in {start_date}? [Y/N]")
        if "y" in confirmation.lower():
            add_crew(crew_name, start_date, start_coords[0], start_coords[1])
            conn = c_con.connect_to_database()
            cursor = conn.cursor()
            cursor.execute('''SELECT crew_id FROM crews WHERE crew_name = ?''', (crew_name,))
            crew_id = cursor.fetchone()[0]
            c_con.set_active_crew(crew_id)
            print(f"{crew_name} added to database with id {crew_id}. Setting to active.")
            conn.close()

        else:
            print("Crew Creation cancelled")

    


def add_from_pprofile(pfname):
    if pfname.endswith('.txt') == True:
        filename = pfname
    else:    
        filename = pfname + '.txt'
    with open(f'./pprofiles/{filename}', 'r') as f:
        gstring = f.readline()[:-1]
        print(gstring)
        add_planet(gstring)
        conn = c_con.connect_to_database()
        cursor = conn.cursor()
        planet_name = filename[:-4]
        print(f'planet name: {planet_name}, file_name: {filename}')
        cursor.execute('''UPDATE planets SET pprofile = ? WHERE LOWER(planet_name) = LOWER(?)''', (filename, planet_name))
        conn.commit()
        conn.close()
        

def import_all_pprofiles():
    files = os.listdir('./pprofiles/')
    txt_files = [file for file in files if file.endswith('.txt')]
    for file in txt_files:
        add_from_pprofile(file)




#More direct input. For more user-friendly version, use 'Hire Crew'
def add_crew_member(crew_id, member_name, role_id, member_salary):
    """Add a new crew member to the database."""
    conn = c_con.connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO CrewMembers (crew_id, member_name, role_id, member_salary) VALUES (?, ?, ?, ?)''',
                   (crew_id, member_name, role_id, member_salary))
    conn.commit()
    conn.close()


def hire_crew_member():
    """Walk the user through the process of hiring a new crew member."""
    print("Hiring a New Crew Member")
    print("=========================")
    c_con.validate_active_crew()

    # Check if there is an active crew

    confirm = False
    while confirm == False:
        active_crew_name = c_con.get_crew_name(c_con.config.active_crew_id)
        proceed_with_hire = input(f"Hirie a new crew member to crew '{active_crew_name}'? [Y/N]")
        if 'y' not in proceed_with_hire.lower():
            c_con.config.active_crew_id = None
            print('Setting new active crew')
            c_con.validate_active_crew()
        else: confirm = True



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

    if 'y' in default_or_custom.lower():
        # Use default salary
        member_salary = default_salary
    else:
        # Prompt the user for a new salary
        try: 
            member_salary = int(input("Enter the new salary: "))
        except:
            print('Salary must be an integer value. Hiring cancelled.')
            return

    # Confirm hiring
    confirm_hire = input(f"Hire {role_name} {member_name} with a salary of {member_salary}? [Y/N]")
    
    if 'y' in confirm_hire.lower():
        # Add the new crew member to the database
        add_crew_member(crew_id= c_con.config.active_crew_id, member_name=member_name, role_id=role_id, member_salary=member_salary)
        print(f"Successfully hired {member_name} as a crew member with role ID {role_id} to crew '{active_crew_name}'.")
    else:
        print("Hiring canceled.")




def get_genie_string(planet_name):
    conn = c_con.connect_to_database()
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM Planet_Genie WHERE planet_name = ? COLLATE NOCASE''', (planet_name,) )
    
    plist = cursor.fetchone()
    #print('Adding planet name.')
    sec_string = plist[0].ljust(14)
    #print('Adding coordinates')
    sec_string = sec_string + plist[1] + ' '
    #print('Adding UWP')
    sec_string = sec_string + ''.join(hex_unparse(i) for i in plist[2:9]) + '-' + hex_unparse(plist[9]) + '  '
    #print('adding Base code')
    sec_string = sec_string + plist[10].ljust(2)
    #print('Adding trade codes')
    sec_string = sec_string + plist[11].ljust(16)
    #print('Adding travel zone')
    sec_string = sec_string + str(plist[12]).ljust(3)
    #print('Adding PBG')
    sec_string = sec_string + ''.join(hex_unparse(i) for i in plist[13:16]) + ' '
    #print('Adding allegiance')
    sec_string = sec_string + plist[16]

    conn.close()  
    return sec_string[0:57]  
    

      



def create_pprofile(planet_name):
    conn = c_con.connect_to_database()
    cursor = conn.cursor()

    cursor.execute(f'''SELECT * FROM Planet_Genie
                   WHERE planet_name = ? COLLATE NOCASE''', (planet_name,))
    plist = cursor.fetchone()
    if plist == None:
        print(f'No planet matching {planet_name} found. Aborting.')
        return
    
    elif plist[-1] != None:
        print(f'Profile for {plist[0]} already exists. Aborting')
    
    else:
        
        print (f'Creating profile for {plist[0]}.')
        with open(f'./pprofiles/{plist[0]}.txt', 'a') as f:
            f.write(get_genie_string(plist[0]) + '\n')
            f.write(f'''Planet Name: {plist[0]}\tCoordinates: {str(plist[1])}\tTravel Zone: {plist[11].ljust(1)}\n''')

            f.write(f'''Starport Quality: {hex_unparse(plist[2])}\tTech Level: {str(plist[9])}\tTrade codes: {plist[11]}\tBases: {plist[10]}\n''')
            f.write(f'''Planetoid Belts: {plist[14]}\t Gas Giants: {plist[15]}\tAllegiance: {plist[16]}\n''')



            cursor.execute('''SELECT * FROM WorldSizes
                           WHERE digit = ?''', (plist[3],))
            sizelist = cursor.fetchone()
            world_size = sizelist[1]
            grav = sizelist[2]
            f.write(f'''Planet Size: {world_size} km\tSurface Gravity: {str(grav)} gs\n''') # type: ignore

            cursor.execute(f'''SELECT * FROM Atmospheres
                           WHERE digit = ?''',(int(plist[4]),) )
            atlist = cursor.fetchone()
            atmo = atlist[1]
            pressure = atlist[2]
            surv_gear = atlist[3]
            f.write(f'''Atmosphere: {atmo}\tPressure: {pressure} atm\tRequired Gear: {surv_gear}\n''')


            cursor.execute('''SELECT * FROM Hydrographics
                           WHERE digit = ?''', (plist[5],))
            hydrolist = cursor.fetchone()
            hydro_per = hydrolist[1]
            hydro_des = hydrolist[2]
            f.write(f'''Hydrographic Percentage: {hydro_per} km\tHydrographic description: {hydro_des}\n''')


            cursor.execute('''SELECT range FROM BasePopulations
                           WHERE digit = ?''', (plist[6],))
            basepop = cursor.fetchone()[0]
            popmod = plist[13]

            cursor.execute('''SELECT government_type FROM GovernmentTypes
                           WHERE digit = ?''', (plist[7],))
            gov_type = cursor.fetchone()[0]
            f.write(f'''Population: {basepop * popmod:,}\tGovernment Type: {str(gov_type)}\n''')

            #print(plist[8])
            cursor.execute('''SELECT restrictions FROM LawLevels
                           WHERE digit = ?''', (min(plist[8],10),))
            restrictions = cursor.fetchone()[0]
            f.write(f'''Law Level: {str(plist[8])}\tRestrictions: {str(restrictions)}\n''')


            f.close()
            cursor.execute('''UPDATE Planets SET pprofile = ? WHERE planet_name = ?''', (plist[0] + '.txt', plist[0]))
            conn.commit()      

    conn.close()

#cube coordinates make for easier distance measures. These three functions set up
#the offset hex distance
def evenq_to_cube(x,y):
    q = x
    r = int(y - (x + (x & 1))/2)
    s = -q-r
    return (q, r, s)

#Here, a and b are integer 3-tuples.
def cube_dist(a,b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]), abs(a[2]-b[2]))

def hex_dist(map_start, map_end):
    #offset to q (columns) and r (diagonal) cube coordinates
    cube_start = evenq_to_cube(map_start[0], map_start[1])
    cube_end = evenq_to_cube(map_end[0], map_end[1])
    return cube_dist(cube_start, cube_end)


def calc_jumplist(start_coords, jump_limit):
    '''start_coords is a tuple containing the (column,row) grid coordinates
    jump_limit is an integer equal to a ship's jump rating
    Returns list of tuples: (planet_name, column_coord, row_coord, jump distance, starport_quality)'''
    jumplist = []
    conn = c_con.connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''SELECT planet_name, column_coordinate, row_coordinate, starport_quality FROM planets''')
    planet_data = cursor.fetchall()
    conn.close()
    for p in planet_data:
        p_coords = (p[1],p[2])
        jump_dist = hex_dist(start_coords, p_coords)
        if jump_dist >0 and jump_dist <= jump_limit:
            print(p[0])
            p_tuple = [p[0], p[1], p[2], jump_dist, hex_unparse(p[3])]
            jumplist.append(p_tuple)
    return jumplist

    

