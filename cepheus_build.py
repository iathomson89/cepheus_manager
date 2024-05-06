import sqlite3
import csv

# Establish connection to the SQLite database
conn = sqlite3.connect('cepheus_campaign.db')
cursor = conn.cursor()

# Create table: Crews
cursor.execute('''CREATE TABLE IF NOT EXISTS Crews (
                    crew_id INTEGER PRIMARY KEY,
                    crew_name TEXT,
                    start_date DATE,
                    current_date DATE
                )''')

# Create table: Roles
cursor.execute('''CREATE TABLE IF NOT EXISTS Roles (
                    role_id INTEGER PRIMARY KEY,
                    role_name TEXT,
                    default_salary INTEGER
                )''')

def get_tsv_data(filepath):
    """Import a tsv file into a list of tuples"""
    data = []
    with open(filepath, 'r', newline = '') as file:
        reader = csv.reader(file, delimiter = '\t')
        for row in reader:
            data.append(tuple(row))
    return data

# Check if each role_name already exists in the Roles table
role_data = get_tsv_data('./data_sources/role_data.tsv')
for role_name, default_salary in role_data:
    cursor.execute('''SELECT COUNT(*) FROM Roles WHERE role_name = ?''', (role_name,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute('''INSERT INTO Roles (role_name, default_salary) VALUES (?, ?)''', (role_name, default_salary))


# Create table: CrewMembers
cursor.execute('''CREATE TABLE IF NOT EXISTS CrewMembers (
                    crew_member_id INTEGER PRIMARY KEY,
                    crew_id INTEGER,
                    member_name TEXT,
                    role_id INTEGER,
                    member_salary INTEGER,
                    FOREIGN KEY (crew_id) REFERENCES Crews (crew_id),
                    FOREIGN KEY (role_id) REFERENCES Roles (role_id)
                )''')



#Create Table: Worlds
cursor.execute('''CREATE TABLE IF NOT EXISTS Planets (
            planet_id INTEGER PRIMARY KEY,
            planet_name TEXT,
            column_coordinate INTEGER,
            row_coordinate INTEGER,
            starport_quality INTEGER,
            planet_size INTEGER,
            atmosphere_type INTEGER,
            hydrosphere_percentage INTEGER,
            population_level INTEGER,
            government_type INTEGER,
            law_level INTEGER,
            tech_level INTEGER,
            base_code VARCHAR(1),
            travel_zone TEXT,
            population_modifier INTEGER,
            planetoid_belts INTEGER,
            gas_giants INTEGER,
            allegiance VARCHAR(2),
            Ag BIT,
            Ast BIT,
            Ba BIT,
            De BIT,
            Fl BIT,
            Ga BIT,
            Hi BIT,
            Ht BIT,
            Ic BIT,
            Ind BIT,
            Lo BIT,
            Lt BIT,
            Na BIT,
            Ni BIT,
            Po BIT,
            Ri BIT,
            Wa BIT,
            Va BIT
);''')


#Create and populate StarportClasses table
cursor.execute('''CREATE TABLE IF NOT EXISTS StarportClasses (
                starport_class VARCHAR(1) PRIMARY KEY,
                descriptor TEXT,
                best_fuel TEXT,
                annual_maintenance BIT,
                shipyard_capacity TEXT,
                possible_naval_base BIT,
                possible_scout_base BIT
);''')

# Check if each role_name already exists in the Roles table
starport_data = get_tsv_data('./data_sources/starport_classes.tsv')
for starport_class, descriptor, best_fuel, annual_maintenance, shipyard_capacity, possible_naval_base, possible_scout_base in starport_data:
    cursor.execute('''SELECT COUNT(*) FROM StarportClasses WHERE starport_class = ?''', (starport_class,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO StarportClasses (
                       starport_class, 
                       descriptor, 
                       best_fuel, 
                       annual_maintenance, 
                       shipyard_capacity, 
                       possible_naval_base, 
                       possible_scout_base) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (
                        starport_class, 
                        descriptor, 
                        best_fuel, 
                        annual_maintenance, 
                        shipyard_capacity, 
                        possible_naval_base, 
                        possible_scout_base
                        ))
        
#Create and populate WorldSizes table

cursor.execute('''CREATE TABLE IF NOT EXISTS WorldSizes (
                digit INTEGER PRIMARY KEY,
                world_size INTEGER,
                surface_gravity FLOAT
);''')


worldsize_data = get_tsv_data('./data_sources/worldsizes.tsv')
for digit, world_size, surface_gravity in worldsize_data:
    cursor.execute('''SELECT COUNT(*) FROM WorldSizes WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO WorldSizes (digit, world_size, surface_gravity) VALUES (?,?,?)''',
                (digit, world_size, surface_gravity))
        
     


#Create and populate Atmospheres table

cursor.execute('''CREATE TABLE IF NOT EXISTS Atmospheres (
                digit INTEGER PRIMARY KEY,
                atmosphere TEXT,
                pressure TEXT,
                survival_gear_required TEXT
);''')


atmosphere_data = get_tsv_data('./data_sources/atmospheres.tsv')
for digit, atmosphere, pressure, survival_gear_required in atmosphere_data:
    cursor.execute('''SELECT COUNT(*) FROM Atmospheres WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO Atmospheres (digit, atmosphere, pressure, survival_gear_required) VALUES (?,?,?,?)''',
                (digit, atmosphere, pressure, survival_gear_required))




#create and populate Hydrographics table
cursor.execute('''CREATE TABLE IF NOT EXISTS Hydrographics (
                digit INTEGER PRIMARY KEY,
                hydrographic_percent TEXT,
                description TEXT
);''')


hydrographics_data = get_tsv_data('./data_sources/hydrographics.tsv')
for digit, hydrographic_percent, description in hydrographics_data:
    cursor.execute('''SELECT COUNT(*) FROM Hydrographics WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO Hydrographics (digit, hydrographic_percent, description) VALUES (?,?,?)''',
                (digit, hydrographic_percent, description))

#create and populate Hydrographics table
cursor.execute('''CREATE TABLE IF NOT EXISTS Hydrographics (
                digit INTEGER PRIMARY KEY,
                hydrographic_percent TEXT,
                description TEXT
);''')



#Create and populate BasePopulations
cursor.execute('''CREATE TABLE IF NOT EXISTS BasePopulations (
                digit INTEGER PRIMARY KEY,
                population TEXT,
                range INTEGER,
                comparison TEXT
);''')


population_data = get_tsv_data('./data_sources/population.tsv')
for digit, population, range, comparison in population_data:
    cursor.execute('''SELECT COUNT(*) FROM BasePopulations WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO BasePopulations (digit, population, range, comparison) VALUES (?,?,?,?)''',
                (digit, population, range, comparison))


#Create and populate GovernmentTypes
cursor.execute('''CREATE TABLE IF NOT EXISTS GovernmentTypes (
                digit INTEGER PRIMARY KEY,
                government_type TEXT
);''')


government_data = get_tsv_data('./data_sources/governments.tsv')
for digit, government_type in government_data:
    cursor.execute('''SELECT COUNT(*) FROM GovernmentTypes WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO GovernmentTypes (digit, government_type) VALUES (?,?)''',
                (digit, government_type))


#Create and populate LawLevels
cursor.execute('''CREATE TABLE IF NOT EXISTS LawLevels (
                digit INTEGER PRIMARY KEY,
                law_descriptor TEXT,
               restrictions TEXT
);''')

law_data = get_tsv_data('./data_sources/lawlevels.tsv')
for digit, law_descriptor, restrictions in law_data:
    cursor.execute('''SELECT COUNT(*) FROM LawLevels WHERE digit = ?''', (digit,))
    existing_records = cursor.fetchone()[0]

    # If no records with the same role_name exist, insert the new record
    if existing_records == 0:
        cursor.execute(
            '''INSERT INTO LawLevels (digit, law_descriptor, restrictions) VALUES (?,?,?)''',
                (digit, law_descriptor, restrictions))


# Commit changes and close connection
conn.commit()
conn.close()



