import sqlite3
import pandas as pd

database = sqlite3.connect("flights_database.db")
dataframe = pd.read_sql("SELECT * FROM flights", database)

database.close()

duplicates = dataframe[dataframe.duplicated()]

if not duplicates.empty:
    print(f"Found {len(duplicates)} duplicate rows:")
    for index, row in duplicates.iterrows():
        print(f"Duplicate row {index}: {row.to_dict()}")
else:
    print("No duplicate rows found.")
