import sqlite3
import tabulate

#The c_config class contains default values for the cepheus manager tools

class c_config:
    _instance = None

    def __init__(self):
        self.default_date = "2776-01-01"
        self.DATABASE_FILE = "cepheus_campaign.db"
        self.default_crew = None
        self.active_crew_id = None  # Initialize active_crew_id

    @staticmethod
    def get_instance():
        if c_config._instance is None:
            c_config._instance = c_config()
        return c_config._instance

config = c_config.get_instance()


 #These are standard functions found in all modules. c_config.connect is essential 
 #for all sql operations,   

def connect_to_database():
    """Establish connection to the SQLite database."""
    config = c_config.get_instance()
    conn = sqlite3.connect(config.DATABASE_FILE)
    return conn

def set_active_crew(input_int):
    """Sets the active_crew variable. Should be the first function called at start of session"""
    active_crew_id = input_int

def get_crews():
    """Retrieve all crews from the database."""
    # Establish connection to the SQLite database
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()

    # Query the database to retrieve all crews
    cursor.execute('''SELECT * FROM Crews''')
    crews = cursor.fetchall()  # Fetch all crews

    # Close the connection
    conn.close()

    return crews


def get_crew_name(crew_id = config.active_crew_id):
    """Retrieve the name of the crew with the given ID."""
    # Establish connection to the SQLite database
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()

    # Query the database to retrieve the crew name
    cursor.execute('''SELECT crew_name FROM Crews WHERE crew_id = ?''', (crew_id,))
    crew_name = cursor.fetchone()[0]  # Fetch the crew name

    # Close the connection
    conn.close()

    return crew_name



#Function that should appear as the first line in any function that requires active_crew_id.
def validate_active_crew():
    '''Returns None if no crews are found in the database.
    If '''
    global active_crew_id
    

    crewlist = get_crews()

    if len(crewlist) == 0: 
        print('No crews found in the Crews table. Please run make_crew() to create a record. Exiting')
        exit()
    while True:
        if any(crew[0] == active_crew_id for crew in crewlist):
                    return active_crew_id
        
        
        headers = ["ID", "Name"]
        crews_table = tabulate(crewlist, headers=headers, tablefmt="grid")
        print("Available Crews:")
        print(crews_table)   
        active_crew_id = input('Please select a valid crew_id')
        if not active_crew_id.isdigit():
            print('Please input an integer value')
        else: active_crew_id = int(active_crew_id)