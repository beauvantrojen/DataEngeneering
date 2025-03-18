import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from datetime import datetime

# Database path
DB_PATH = "flights_database.db"

# Function to get user-selected flight date
def get_flight_date():
    return st.date_input(
        "Select a day in 2023",
        datetime(2023, 1, 1),
        min_value=datetime(2023, 1, 1),
        max_value=datetime(2023, 12, 31),
    )


# Fetch flight data for the selected date
def fetch_flight_data(selected_date):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT year, month, day, dep_time, sched_dep_time, arr_time, sched_arr_time, air_time, origin, dest
    FROM flights
    WHERE year = ? AND month = ? AND day = ?
    """
    params = (selected_date.year, selected_date.month, selected_date.day)
    flights_df = pd.read_sql(query, conn, params=params)
    conn.close()
    return flights_df

# Convert time fields
def convert_to_datetime(row, time_col):
    try:
        if pd.isna(row[time_col]) or row[time_col] is None:
            return None
        time_str = f"{int(row[time_col]):04d}"
        hour, minute = int(time_str[:2]), int(time_str[2:])
        return pd.Timestamp(
            year=int(row["year"]),
            month=int(row["month"]),
            day=int(row["day"]),
            hour=hour,
            minute=minute,
        )
    except (ValueError, TypeError):
        return None

# Process flight data
def process_flight_data(flights_df):
    for col in ["dep_time", "sched_dep_time", "arr_time", "sched_arr_time"]:
        flights_df[f"{col}_dt"] = flights_df.apply(lambda row: convert_to_datetime(row, col), axis=1)

    flights_df["dep_delay"] = (flights_df["dep_time_dt"] - flights_df["sched_dep_time_dt"]).dt.total_seconds() / 60
    return flights_df

# Streamlit UI
st.title("Flight Information Dashboard ✈️")
st.write("This page contains information about the flights occuring on a day of your choice.")

# Get user input
st.subheader("Select a flight date")
selected_date = get_flight_date()

# Fetch and process data
flights_df = fetch_flight_data(selected_date)

if flights_df.empty:
    st.write("❌ No flights found for the selected date.")
else:
    flights_df = process_flight_data(flights_df)

    # Calculate total number of flights
    total_flights = len(flights_df)

    # Display a styled box with the total number of flights
    st.markdown(
        f"""
        <div style="
            background-color: #f4f4f4; 
            padding: 15px; 
            border-radius: 10px; 
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
            text-align: center;
            font-size: 20px;
            font-weight: bold;
        ">
            ✈️ Total Flights on {selected_date.strftime('%B %d, %Y')}: <span style="color: purple;">{total_flights}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")  # Add a blank line of space
    st.write("")
    st.write("")
    st.write("")

    st.subheader("Amount of departing and incomming flights per airport ")
    # Departures and Arrivals Charts (Placed side by side)
    col1, col2 = st.columns(2)

    for idx, (col, title, color) in enumerate([("origin", "Departures", "purple"), ("dest", "Arrivals", "purple")]):
        count_df = flights_df[col].value_counts().reset_index()
        count_df.columns = ["Airport", f"Number of {title}"]
        chart = (
            alt.Chart(count_df)
            .mark_bar(color=color)
            .encode(
                x=alt.X("Airport:N", sort="-y"),
                y=alt.Y(f"Number of {title}:Q"),
                tooltip=["Airport", f"Number of {title}"],
            )
            .properties(width=800, height=400)  # Adjust size for side-by-side view
        )

        if idx == 0:
            with col1:
                st.write(f"**Number of {title} from Each Airport**")
                st.altair_chart(chart, use_container_width=True)
        else:
            with col2:
                st.write(f"**Number of {title} from Each Airport**")
                st.altair_chart(chart, use_container_width=True)

    # Average Delay Per Hour Chart (This should be outside the loop)
    flights_df["hour"] = flights_df["sched_dep_time_dt"].dt.hour
    avg_delay = flights_df.groupby("hour")["dep_delay"].mean().reset_index()

    delay_chart = (
        alt.Chart(avg_delay).mark_line(color="purple").encode(
            x=alt.X("hour:O", title="Hour of Day"),
            y=alt.Y("dep_delay:Q", title="Average Delay (minutes)"),
            tooltip=["hour", "dep_delay"],
        )
        + alt.Chart(avg_delay).mark_circle(color="purple").encode(
            x="hour:O",
            y="dep_delay:Q",
            tooltip=["hour", "dep_delay"],
        )
    )

    st.subheader("**Average Departure Delay Throughout the Day**")
    st.altair_chart(delay_chart, use_container_width=True)

    # Airtime Distribution Chart (This should also be outside the loop)
    airtime_counts = flights_df["air_time"].dropna().value_counts().reset_index()
    airtime_counts.columns = ["Airtime (minutes)", "Number of Flights"]

    airtime_chart = (
        alt.Chart(airtime_counts)
        .mark_bar(color="purple")
        .encode(
            x=alt.X("Airtime (minutes):Q", bin=alt.Bin(maxbins=50), title="Airtime (minutes)"),
            y=alt.Y("Number of Flights:Q", title="Count of Flights"),
            tooltip=["Airtime (minutes)", "Number of Flights"],
        )
        .properties(width=800, height=500)
    )

    st.subheader("**Distribution of Flights by Airtime**")
    st.altair_chart(airtime_chart, use_container_width=True)