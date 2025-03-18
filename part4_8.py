import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

db_path = "flights_database.db"
conn = sqlite3.connect(db_path)

# Airports with Highest Delays
query_delays = """
SELECT origin, AVG(arr_delay) AS avg_delay
FROM flights
WHERE arr_delay IS NOT NULL
GROUP BY origin
ORDER BY avg_delay DESC;
"""
df_airport_delays = pd.read_sql_query(query_delays, conn)

plt.figure(figsize=(12, 6))
sns.barplot(x="avg_delay", y="origin", data=df_airport_delays, palette="Blues_r")
plt.xlabel("Average Arrival Delay (minutes)")
plt.ylabel("Airport")
plt.title("Airports with Highest Delays")
plt.show()

# Fastest Plane Models
query_speed = """
SELECT p.model, AVG(f.distance / (f.air_time / 60.0)) AS avg_speed
FROM flights f
JOIN planes p ON f.tailnum = p.tailnum
WHERE f.air_time > 0 AND f.distance > 0
GROUP BY p.model
ORDER BY avg_speed DESC
LIMIT 20;
"""
df_plane_speeds = pd.read_sql_query(query_speed, conn)

plt.figure(figsize=(12, 6))
sns.barplot(y="model", x="avg_speed", data=df_plane_speeds, palette="Greens_r")
plt.xlabel("Average Speed (mph)")
plt.ylabel("Plane Model")
plt.title("20 Fastest Plane Models")
plt.show()

# Most Frequent Flight Routes from NYC 
query_routes = """
SELECT origin, dest, COUNT(*) AS flight_count
FROM flights
WHERE origin IN ('JFK', 'LGA', 'EWR')
GROUP BY origin, dest
ORDER BY flight_count DESC
LIMIT 50;
"""
df_top_routes = pd.read_sql_query(query_routes, conn)

df_top_routes["route"] = df_top_routes["origin"] + " → " + df_top_routes["dest"]

plt.figure(figsize=(20, 10))
sns.barplot(x="flight_count", y="route", data=df_top_routes, palette="Reds_r")
plt.xlabel("Number of Flights")
plt.ylabel("Route")
plt.title("50 Most Frequent Routes from NYC")
plt.show()

# Impact of Weather on Delays
query = """
SELECT w.wind_speed, f.arr_delay
FROM flights f
JOIN weather w ON f.origin = w.origin AND f.year = w.year AND f.month = w.month AND f.day = w.day
WHERE f.arr_delay IS NOT NULL AND w.wind_speed IS NOT NULL;
"""
df_weather_delay = pd.read_sql_query(query, conn)

conn.close()

df_avg_delay = df_weather_delay.groupby("wind_speed")["arr_delay"].mean().reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(x="wind_speed", y="arr_delay", data=df_avg_delay, marker="o", color="b")
plt.xlabel("Wind Speed (mph)")
plt.ylabel("Average Arrival Delay (minutes)")
plt.title("Average Arrival Delay vs Wind Speed")
plt.grid(True)
plt.show()
