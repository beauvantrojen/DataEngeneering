import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

connection = sqlite3.connect("flights_database.db")

connection.execute("""
    CREATE TEMP TABLE temp_weather AS
    SELECT * FROM weather
    WHERE temp IS NOT NULL AND wind_speed IS NOT NULL AND precip IS NOT NULL;
""")

# Use the temporary table for analysis
query = """
    SELECT f.flight, f.origin, f.dep_time, f.sched_dep_time, 
           (strftime('%s', date(tw.time_hour, 'unixepoch')) + 
            (CAST(f.dep_time / 100 AS INTEGER) * 3600) + 
            ((f.dep_time % 100) * 60)) AS dep_unix, 
           tw.time_hour AS weather_unix, 
           f.air_time, f.distance, 
           tw.temp, tw.wind_speed, tw.precip, p.model
    FROM flights f
    JOIN temp_weather tw  -- Use temporary table instead of 'weather'
        ON f.origin = tw.origin 
        AND abs(
            (strftime('%s', date(tw.time_hour, 'unixepoch')) + 
            (CAST(f.dep_time / 100 AS INTEGER) * 3600) + 
            ((f.dep_time % 100) * 60)) - tw.time_hour
        ) <= 1800
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.dep_time IS NOT NULL 
    AND tw.wind_speed IS NOT NULL
    LIMIT 1000;
"""
df = pd.read_sql_query(query, connection)

def plot_wind_vs_airtime():
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df['wind_speed'], y=df['air_time'], hue=df['distance'], alpha=0.7, palette="coolwarm")
    plt.xlabel("Wind Speed (mph)")
    plt.ylabel("Air Time (minutes)")
    plt.title("Impact of Wind Speed on Air Time (Colored by Distance)")
    plt.legend(title="Distance (miles)")
    plt.show()

def precipation_vs_delays():
    df['delay'] = (pd.to_datetime(df['dep_unix'], unit='s') - pd.to_datetime(df['weather_unix'], unit='s')).dt.total_seconds() / 60
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=pd.cut(df['precip'], bins=[0, 0.1, 0.5, 1, 5, 10]), y=df['delay'])
    plt.xlabel("Precipitation (inches)")
    plt.ylabel("Flight Delay (minutes)")
    plt.title("Flight Delays vs Precipitation")
    plt.show()

def wind_speed_vs_plane_models():
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="model", y="wind_speed", data=df)
    plt.xticks(rotation=90)
    plt.xlabel("Plane Model")
    plt.ylabel("Wind Speed (mph)")
    plt.title("Wind Speed Distribution by Plane Model")
    plt.show()

def flight_distance_vs_wind_speed():
    plt.figure(figsize=(10, 6))
    sns.regplot(x=df['distance'], y=df['wind_speed'])
    plt.xlabel("Flight Distance (miles)")
    plt.ylabel("Wind Speed (mph)")
    plt.title("Flight Distance vs Wind Speed")
    plt.show()

def plane_model_vs_delay_during_wind():
    df['delay'] = (pd.to_datetime(df['dep_unix'], unit='s') - pd.to_datetime(df['weather_unix'], unit='s')).dt.total_seconds() / 60
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="model", y="delay", hue=pd.cut(df['wind_speed'], bins=[0, 10, 20, 30, 40]), data=df)
    plt.xticks(rotation=90)
    plt.xlabel("Plane Model")
    plt.ylabel("Delay (minutes)")
    plt.title("Plane Model vs Delay in Different Wind Speeds")
    plt.legend(title="Wind Speed (mph)")
    plt.show()


if __name__ == "__main__":
    #plot_wind_vs_airtime() # flight time doesn't decrease with higher wind speeds
    #precipation_vs_delays() #precipiation doesn't seem to effect the delay time
    #wind_speed_vs_plane_models() #Shows the disbrution over which plane models are used during different wind conditions, indicating that they might preform better under certain cicumstances
    #flight_distance_vs_wind_speed()# the regression line moves down meaning that longer flights experience less strong wind
    plane_model_vs_delay_during_wind()# some models experience more delay during windy conditions, other ones stay the same

connection.close()
