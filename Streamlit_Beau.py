import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

airports_df = pd.read_csv("airports.csv")

departure_airport = st.sidebar.selectbox("Select Departure Airport", airports_df["name"].unique())
arrival_airport = st.sidebar.selectbox("Select Arrival Airport", airports_df["name"].unique())

conn = sqlite3.connect("flights_database.db")

if departure_airport == arrival_airport:
    st.warning("Please select a different destination airport.")
else:
    query = """
    SELECT carrier, COUNT(*) as num_flights, AVG(dep_delay) as avg_dep_delay, 
           AVG(arr_delay) as avg_arr_delay, MIN(dep_time) as earliest_dep, 
           MAX(dep_time) as latest_dep
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

        total_flights = df_flight_stats["num_flights"].sum()
        avg_dep_delay = df_flight_stats["avg_dep_delay"].mean()
        avg_arr_delay = df_flight_stats["avg_arr_delay"].mean()
        earliest_dep = df_flight_stats["earliest_dep"].min()
        latest_dep = df_flight_stats["latest_dep"].max()

        st.write(f"#### Total Flights: {total_flights}")
        st.write(f"#### Average Departure Delay: {avg_dep_delay:.2f} minutes")
        st.write(f"#### Average Arrival Delay: {avg_arr_delay:.2f} minutes")
        st.write(f"#### Earliest Departure Time: {earliest_dep}")
        st.write(f"#### Latest Departure Time: {latest_dep}")

        fig, ax = plt.subplots()
        ax.bar(df_flight_stats["carrier"], df_flight_stats["num_flights"], color="skyblue")
        ax.set_title(f"Number of Flights per Airline ({departure_airport} to {arrival_airport})")
        ax.set_xlabel("Airline")
        ax.set_ylabel("Number of Flights")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.pie(df_flight_stats["num_flights"], labels=df_flight_stats["carrier"], autopct="%1.1f%%", startangle=140)
        ax2.set_title("Flight Distribution by Airline")
        st.pyplot(fig2)

        query_top_destinations = """
        SELECT dest, COUNT(*) as num_flights
        FROM flights
        WHERE origin = (SELECT faa FROM airports WHERE name = ?)
        GROUP BY dest
        ORDER BY num_flights DESC
        LIMIT 5
        """
        df_top_destinations = pd.read_sql_query(query_top_destinations, conn, params=(departure_airport,))
        
        if not df_top_destinations.empty:
            st.write(f"### Top 5 Destinations from {departure_airport}")
            st.dataframe(df_top_destinations)

