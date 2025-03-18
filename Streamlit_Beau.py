import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

airports_df = pd.read_csv("airports.csv")

departure_airport = st.sidebar.selectbox("Select Departure Airport", airports_df["name"].unique())
arrival_airport = st.sidebar.selectbox("Select Arrival Airport", airports_df["name"].unique())

conn = sqlite3.connect("flights_database.db")

query = """
SELECT carrier, COUNT(*) as num_flights, AVG(dep_delay) as avg_delay
FROM flights
WHERE origin = (SELECT faa FROM airports WHERE name = ?)
AND dest = (SELECT faa FROM airports WHERE name = ?)
GROUP BY carrier
"""

df_flight_stats = pd.read_sql_query(query, conn, params=(departure_airport, arrival_airport))
st.write(f"### Flight Statistics from {departure_airport} to {arrival_airport}")

if df_flight_stats.empty:
    st.warning("No flight data available for the selected route.")
else:
    st.dataframe(df_flight_stats) 

    fig, ax = plt.subplots()
    ax.bar(df_flight_stats["carrier"], df_flight_stats["num_flights"], color="skyblue")

    ax.set_title(f"Number of Flights per Airline ({departure_airport} to {arrival_airport})")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Number of Flights")

    plt.xticks(rotation=45)

    st.pyplot(fig)
