import sqlite3

# Establish connection to the SQLite database
conn = sqlite3.connect('cepheus_campaign.db')
cursor = conn.cursor()

# Create table: Crews
cursor.execute('''CREATE TABLE IF NOT EXISTS Crews (
                    crew_id INTEGER PRIMARY KEY,
                    crew_name TEXT
                )''')

# Create table: Roles
cursor.execute('''CREATE TABLE IF NOT EXISTS Roles (
                    role_id INTEGER PRIMARY KEY,
                    role_name TEXT,
                    default_salary INTEGER
                )''')

role_data = [
    ('Player Character', 0),
    ('Pilot', 6000),
    ('Navigator', 5000),
    ('Chief Engineer', 4000),
    ('Master', 6000),
    ('Medic', 2000),
    ('Purser', 3000),
    ('Gunner', 1000),
    ('Technician', 1000),
    ('Deck Hand', 1000),
    ('Security', 1000),
    ('Steward', 3000)
]

# Check if each role_name already exists in the Roles table
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



# Commit changes and close connection
conn.commit()
conn.close()
