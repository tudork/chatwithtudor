import re, sqlite3
conn = sqlite3.connect('database.db')

c = conn.cursor()
c.execute('''CREATE TABLE users
           (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE,
           password TEXT NOT NULL, score INTEGER, timestamp DATE)''')


c.execute('''SELECT password FROM users''')
print(c.fetchall())