import sqlite3
import pandas as pd

connection = sqlite3.connect("fligths_database.db")
cursor = connection.cursor()

cursor.execute("SELECT name FROM sqlite_master Where type ='table'")
tables = cursor.fetchall

print("Tables in the database:", tables)