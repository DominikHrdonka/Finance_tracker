import sqlite3

#Creating database for the whole project

"""
NOTE:
- if the DB is not yet on your local machine, it will be created in the directory,
from which you are running the code
"""
with sqlite3.connect('finance_tracker_database.db') as Connection:
    cursor = Connection.cursor()

    #Creating table for revenues and expanses if the database is not yet on your local machine

    cursor.execute(
        'CREATE TABLE IF NOT EXIST revenues_expenses (id INTEGER PRIMARY KEY, revenue BOOLEAN, date TEXT);'
    )

    #Mock data to add to revenues_expenses table
    mock_data = [
        (True, '2025-03-5'),
        (False, '2025-01-24'),
        (True, '2025-03-03'),
        (False, '2024-12-31')
    ]

    #Adding the mock data to revenues_expenses table ONLY IF the table is empty

    cursor.execute(
        'SELECT COUNT(*) FROM revenues_expenses;'
    )

    row_count = cursor.fetchone()[0]
    
    if row_count == 0:
        cursor.executemany(
            'INSERT INTO revenues_expenses (revenue, date) VALUES (?, ?);', mock_data
        )

        Connection.commit()

    