import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# === Apply Page Configuration ===
st.set_page_config(
    page_title="Flight Statistics Dashboard",
    page_icon="✈️",
    layout="wide"
)

# === Load Airport Data ===
airports_df = pd.read_csv("airports.csv")

# === Sidebar Section ===
st.sidebar.header("Flight Selection ✈️")
departure_airport = st.sidebar.selectbox("Select Departure Airport", airports_df["name"].unique())
arrival_airport = st.sidebar.selectbox("Select Arrival Airport", airports_df["name"].unique())

# === Connect to Database ===
conn = sqlite3.connect("flights_database.db")

# Prevent selecting the same airport
if departure_airport == arrival_airport:
    st.warning("⚠️ Please select a different destination airport.")
else:
    # SQL Query for Flight Statistics
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

    # === Dashboard Header ===
    st.markdown(f"""
    <h1 style='text-align: center; color: #4CAF50;'>Flight Statistics Dashboard</h1>
    <h3 style='text-align: center;'>From {departure_airport} 🛫 to {arrival_airport} 🛬</h3>
    <hr>
    """, unsafe_allow_html=True)

    if df_flight_stats.empty:
        st.warning("No flight data available for the selected route.")
    else:
        # === Summary Metrics ===
        total_flights = df_flight_stats["num_flights"].sum()
        avg_dep_delay = df_flight_stats["avg_dep_delay"].mean()
        avg_arr_delay = df_flight_stats["avg_arr_delay"].mean()
        earliest_dep = df_flight_stats["earliest_dep"].min()
        latest_dep = df_flight_stats["latest_dep"].max()

        # Display Key Metrics in Columns
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Flights", total_flights, "📊")
        col2.metric("Avg Departure Delay (min)", f"{avg_dep_delay:.2f}", "⏳")
        col3.metric("Avg Arrival Delay (min)", f"{avg_arr_delay:.2f}", "🚦")

        # === Interactive Bar Chart ===
        fig = px.bar(
            df_flight_stats,
            x="carrier",
            y="num_flights",
            color="carrier",
            title="Number of Flights per Airline",
            labels={"carrier": "Airline", "num_flights": "Number of Flights"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # === Pie Chart for Airline Distribution ===
        fig_pie = px.pie(
            df_flight_stats,
            names="carrier",
            values="num_flights",
            title="Flight Distribution by Airline"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # === Expandable Flight Data Table ===
        with st.expander("📋 View Flight Data Table"):
            st.dataframe(df_flight_stats.style.format({"avg_dep_delay": "{:.2f}", "avg_arr_delay": "{:.2f}"}))

        # === Map: Show Airport Locations ===
        st.markdown("### 🌍 Departure & Arrival Airport Locations")
        airports_filtered = airports_df[airports_df["name"].isin([departure_airport, arrival_airport])]
        fig_map = px.scatter_mapbox(
            airports_filtered,
            lat="lat",
            lon="lon",
            text="name",
            zoom=3,
            mapbox_style="open-street-map",
            title="Airport Locations"
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # === Top Destinations from Departure Airport ===
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
            st.markdown("### 🌟 Top 5 Destinations from Departure Airport")
            st.dataframe(df_top_destinations)

# === Custom Styling ===
st.markdown("""
<style>
    .stMetric label {
        font-size: 18px;
        font-weight: bold;
        color: #4CAF50;
    }
    .stDataFrame {
        border: 2px solid #4CAF50;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
