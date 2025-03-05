import sqlite3

#Creating database for inserted revenues and expenses

with sqlite3.connect('finance_tracker_database.db') as Connection:
    cursor = Connection.cursor()

    cursor.execute(
        'CREATE TABLE IF NOT EXIST revenues_expenses (id INTEGER PRIMARY KEY, revenue BOOLEAN, date TEXT);'
    )
    