import sqlite3

connection = sqlite3.connect('database.db')

connection.execute( 
    'CREATE TABLE IF NOT EXISTS encrypts (name_file TEXT, gen_key TEXT, used BOOLEAN)')

connection.commit()
connection.close()