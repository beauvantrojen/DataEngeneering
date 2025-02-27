import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#returns statistics of a given airport
def airport_statistics(df, airport):
    
    airport_df = df[df["origin"] == airport]
    if airport_df.empty:
        print(f"⚠️ No data available for airport: {airport}")
        return None

    stats = airport_df[["air_time", "distance", "wind_speed", "temp", "precip"]].describe()
    return stats


#plot wind speed against airports simairly to bullet point 6
def plot_wind_speed(df,airport):

    airport_df = df[df["origin"] == airport]

    plt.figure(figsize=(10, 5))
    sns.histplot(airport_df["wind_speed"], bins=15, kde=True)
    plt.xlabel("Wind Speed (mph)")
    plt.ylabel("Frequency")
    plt.title(f"Wind Speed Distribution at {airport}")
    plt.show()

#Compares delyas across different airports
def compare_airports(df, airports):
    filtered_df = df[df["origin"].isin(airports)]

    plt.figure(figsize=(12, 6))
    sns.boxplot(x="origin", y="delay", data=filtered_df)
    plt.xlabel("Airport")
    plt.ylabel("Flight Delay (minutes)")
    plt.title("Flight Delays Across Airports")
    plt.show()

#This method groups average data by airport
def grouped_airport_data(df):
    grouped = df.groupby("origin").agg(
        avg_air_time=("air_time", "mean"),
        avg_distance=("distance", "mean"),
        avg_temp=("temp", "mean"),
        avg_wind_speed=("wind_speed", "mean"),
        avg_precip=("precip", "mean"),
    )
    return grouped