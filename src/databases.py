import sqlite3

#Creating database for the whole project

"""
NOTE:
- need to figure out the path to the DB - it will be different on every machine
"""
with sqlite3.connect('finance_tracker_database.db') as Connection:
    cursor = Connection.cursor()

    #Creating table for revenues and expanses

    cursor.execute(
        'CREATE TABLE IF NOT EXIST revenues_expenses (id INTEGER PRIMARY KEY, revenue BOOLEAN, date TEXT);'
    )
    