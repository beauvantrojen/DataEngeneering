import sqlite3
import pandas as pd
import numpy as np

#3. Convert the (schedueled and actual) arrival departure and departure moments
#to datetime objects.
db_path = "flights_database.db"
conn = sqlite3.connect(db_path)
query = """
SELECT year, month, day, dep_time, sched_dep_time, arr_time, sched_arr_time, air_time
FROM flights;
"""
flights_df = pd.read_sql(query, conn)

def convert_to_datetime(row, time_col):
    try:
        if pd.isna(row[time_col]) or row[time_col] is None:
            return None
        time_value = int(row[time_col]) 
        time_str = f"{time_value:04d}"  
        hour, minute = int(time_str[:2]), int(time_str[2:])
        return pd.Timestamp(year=int(row["year"]), month=int(row["month"]), day=int(row["day"]), hour=hour, minute=minute)
    except (ValueError, TypeError):
        return None  

flights_df["dep_time_dt"] = flights_df.apply(lambda row: convert_to_datetime(row, "dep_time"), axis=1)
flights_df["sched_dep_time_dt"] = flights_df.apply(lambda row: convert_to_datetime(row, "sched_dep_time"), axis=1)
flights_df["arr_time_dt"] = flights_df.apply(lambda row: convert_to_datetime(row, "arr_time"), axis=1)
flights_df["sched_arr_time_dt"] = flights_df.apply(lambda row: convert_to_datetime(row, "sched_arr_time"), axis=1)

print("Sample converted flights data:")
print(flights_df.sample(10))

##csv_path = "converted_flights.csv"
##flights_df.to_csv(csv_path, index=False)
##csv_path

#4. Write a function that checks whether the data in is in order. That
#is, verify that the air time , dep time ,   etc. match for each
#flight. If not, think of ways to resolve it if this is not the case.

conn = sqlite3.connect("flights_database.db")

def check_flight_order():
    query = """
    SELECT flight, dep_time, sched_dep_time, arr_time, sched_arr_time, air_time
    FROM flights
    WHERE dep_time IS NOT NULL AND arr_time IS NOT NULL AND air_time IS NOT NULL
    """
    flights_df = pd.read_sql(query, conn)

    for col in ["dep_time", "sched_dep_time", "arr_time", "sched_arr_time"]:
        flights_df[col] = pd.to_datetime(flights_df[col], format='%H%M', errors='coerce')
    flights_df["computed_air_time"] = (flights_df["arr_time"] - flights_df["dep_time"]).dt.total_seconds() / 60
    issues = flights_df[(flights_df["computed_air_time"].notnull()) & 
                        (abs(flights_df["computed_air_time"] - flights_df["air_time"]) > 5)]
    
    
    if not issues.empty:
        print("Inconsistent flights detected:")
        print(issues.sample(10).to_string(index=False)) 
    else:
        print("All flight data appears to be in order.")
    
    return issues

check_flight_order()
