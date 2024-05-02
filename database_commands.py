import sqlite3
from tabulate import tabulate

# Define the SQLite database filename
DATABASE_FILE = 'cepheus_campaign.db'

def connect_to_database():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

def close_connection(conn):
    """Close the connection to the SQLite database."""
    conn.close()

def set_active_crew():
    """Sets the active_crew variable. Should be the first function called at start of session"""
    active_crew_id = input()

def get_crews():
    """Retrieve all crews from the database."""
    # Establish connection to the SQLite database
    conn = sqlite3.connect('cepheus_campaign.db')
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
    conn = sqlite3.connect('cepheus_campaign.db')
    cursor = conn.cursor()

    # Query the database to retrieve the crew name
    cursor.execute('''SELECT crew_name FROM Crews WHERE crew_id = ?''', (crew_id,))
    crew_name = cursor.fetchone()[0]  # Fetch the crew name

    # Close the connection
    conn.close()

    return crew_name

def get_roles():
    """Fetch roles from the database."""
    conn = sqlite3.connect('cepheus_campaign.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT role_id, role_name, default_salary FROM Roles''')
    roles = cursor.fetchall()
    conn.close()
    return roles


def add_crew(crew_name):
    """Add a new crew to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Crews (crew_name) VALUES (?)''', (crew_name,))
    conn.commit()
    close_connection(conn)

def add_role(role_name, default_salary):
    """Add a new role to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Roles (role_name, default_salary) VALUES (?, ?)''', (role_name, default_salary))
    conn.commit()
    close_connection(conn)


#More direct input. For more user-friendly version, use 'Hire Crew'
def add_crew_member(crew_id, member_name, role_id, member_salary):
    """Add a new crew member to the database."""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO CrewMembers (crew_id, member_name, role_id, member_salary) VALUES (?, ?, ?, ?)''',
                   (crew_id, member_name, role_id, member_salary))
    conn.commit()
    close_connection(conn)


def hire_crew():
    """Walk the user through the process of hiring a new crew member."""
    print("Hiring a New Crew Member")
    print("=========================")

    # Check if there is an active crew
    if active_crew_id == True:
        active_crew_name = get_crew_name(active_crew_id)
        print(f"Hiring a new crew member to crew '{active_crew_name}'.")
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

    # Prompt the user for crew member name
    member_name = input("Enter the name of the new crew member: ")

    # Display roles table with IDs, role names, and salaries
    roles = get_roles()  # Get roles from the database
    headers = ["ID", "Name", "Salary"]
    role_table = tabulate(roles, headers=headers, tablefmt="grid")
    print(role_table)

    # Prompt the user to input the ID of the desired role
    role_id = input("Enter the ID of the desired role: ")

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
    confirm_message = f"Hire {role_name} {member_name} with a salary of {member_salary}? (yes/no) "
    confirm = input(confirm_message)
    
    if confirm.lower() == 'yes':
        # Add the new crew member to the database
        add_crew_member(crew_id=active_crew_id, member_name=member_name, role_id=role_id, member_salary=member_salary)
        print(f"Successfully hired {member_name} as a crew member with role ID {role_id} to crew '{active_crew_name}'.")
    else:
        print("Hiring canceled.")

# Example usage:
if __name__ == "__main__":
    hire_crew()