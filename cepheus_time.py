from datetime import datetime, timedelta
import sqlite3
import json
import cepheus_config as c_con
import tabulate



c_con.config

##TO DO:
##Check for monthly payments
##Check for Monthly Maintenance (include "last maintenance" datestamp in starships)
##  -Give warning "X days until maintenance due."
##Check for ageing
##  -Notify "Birthday in X days" when within 1 month.
##  -Notify "Ageing Check: birthday within x days" on 4 year birthdays
##  -"Happy Birthday. You are {Age} years old" when birthday arrives.
##      -Add "Make an ageing check" on ageing check birthdates. 



def advance_time(days):
    c_con.validate_active_crew()
    conn = c_con.connect_to_database()
    cursor = conn.cursor()

    cursor.execute('''SELECT current_date FROM Crews WHERE crew_id = ?''', (c_con.config.active_crew_id,))
    begin_date = datetime.strptime(cursor.fetchone()[0],'%Y-%m-%d')
    end_date = begin_date + timedelta(days = days)
    #INSERT ALL FINANCIAL AND TIME RELATED CHECKS HERE

    end_date_str = end_date.strftime('%Y-%m-%d')    
    cursor.execute('''UPDATE Crews SET current_date = ? WHERE crew_id = ?''', (end_date_str, c_con.config.active_crew_id))
    conn.commit()
    
    conn.close()
