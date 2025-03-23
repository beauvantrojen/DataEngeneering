import numpy as np
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from datetime import datetime

st.set_page_config(
    page_title="NYC Flights Dashboard", layout="wide", initial_sidebar_state="expanded"
)
conn = sqlite3.connect("flights_database.db")
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Flight Route Statistics", "Delay Analysis", "Time-based Statistics"],
)

if page == "Overview":
    st.markdown(
        f"""
    <h1 style='text-align: center; color:rgb(19, 19, 31);'>🗽 NYC Flights Dashboard – Overview</h1>
    <hr>
    """,
        unsafe_allow_html=True,
    )

    query_total = "SELECT COUNT(*) as total FROM flights"
    df_total = pd.read_sql_query(query_total, conn)
    total_flights = df_total.loc[0, "total"]
    query_daily_avg = """
        SELECT AVG(daily_count) AS avg_daily
        FROM (
            SELECT year, month, day, COUNT(*) AS daily_count
            FROM flights
            GROUP BY year, month, day
        )
    """
    df_daily_avg = pd.read_sql_query(query_daily_avg, conn)
    avg_daily_flights = df_daily_avg.loc[0, "avg_daily"]

    query_air_time = """
        SELECT 
            AVG(air_time) AS avg_air_time, 
            MIN(air_time) AS min_air_time, 
            MAX(air_time) AS max_air_time
        FROM flights
    """
    df_airtime = pd.read_sql_query(query_air_time, conn)
    avg_air_time = df_airtime.loc[0, "avg_air_time"]
    min_air_time = df_airtime.loc[0, "min_air_time"]
    max_air_time = df_airtime.loc[0, "max_air_time"]

    query_distance = """
        SELECT 
            AVG(distance) AS avg_distance, 
            MIN(distance) AS min_distance, 
            MAX(distance) AS max_distance
        FROM flights
    """
    df_distance = pd.read_sql_query(query_distance, conn)
    avg_distance = df_distance.loc[0, "avg_distance"]
    min_distance = df_distance.loc[0, "min_distance"]
    max_distance = df_distance.loc[0, "max_distance"]

    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

    with row1_col1:
        st.metric("Total Flights", total_flights)
    with row1_col2:
        st.metric("Average Flight Duration (min)", f"{round(avg_air_time, 2)}")
    with row1_col3:
        st.metric("Min Flight Duration (min)", f"{round(min_air_time, 2)}")
    with row1_col4:
        st.metric("Max Flight Duration (min)", f"{round(max_air_time, 2)}")

    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

    with row2_col1:
        st.metric("Average Flights per Day", round(avg_daily_flights))
    with row2_col2:
        st.metric("Average Distance (miles)", f"{round(avg_distance, 2)}")
    with row2_col3:
        st.metric("Min Distance (miles)", f"{round(min_distance, 2)}")
    with row2_col4:
        st.metric("Max Distance (miles)", f"{round(max_distance, 2)}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### **Distribution of Flights Across NYC Airports**")
        query_origin = "SELECT origin, COUNT(*) as count FROM flights GROUP BY origin"
        df_origin = pd.read_sql_query(query_origin, conn)

        fig_origin = px.pie(
            df_origin,
            names="origin",
            values="count",
        )
        fig_origin.update_layout(width=500)
        st.plotly_chart(fig_origin, use_container_width=False)

    with col2:
        st.markdown("##### **Number of Flights by Departure Airport**")
        query_departure_airport = (
            "SELECT origin, COUNT(*) as flight_count FROM flights GROUP BY origin"
        )
        df_departure_airport = pd.read_sql_query(query_departure_airport, conn)

        fig_departure_airport = px.bar(
            df_departure_airport,
            x="origin",
            y="flight_count",
            labels={"origin": "Departure Airport", "flight_count": "Number of Flights"},
        )
        fig_departure_airport.update_layout(width=500)
        st.plotly_chart(fig_departure_airport, use_container_width=False)

    col_delay_stats, col_delay_breakdown = st.columns(2)

    with col_delay_stats:
        st.markdown("##### **Delay Statistics**")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        df_delays = pd.read_sql_query("SELECT dep_delay, arr_delay FROM flights", conn)
        df_delays = df_delays.dropna(subset=["dep_delay", "arr_delay"])

        dep_mean = df_delays["dep_delay"].mean()
        dep_median = df_delays["dep_delay"].median()
        dep_min = df_delays["dep_delay"].min()
        dep_max = df_delays["dep_delay"].max()
        dep_std = df_delays["dep_delay"].std()

        arr_mean = df_delays["arr_delay"].mean()
        arr_median = df_delays["arr_delay"].median()
        arr_min = df_delays["arr_delay"].min()
        arr_max = df_delays["arr_delay"].max()
        arr_std = df_delays["arr_delay"].std()

        delay_summary = pd.DataFrame(
            {
                "Metric": ["Mean", "Median", "Min", "Max", "Std Dev"],
                "Departure Delay": [
                    round(dep_mean, 2),
                    round(dep_median, 2),
                    round(dep_min, 2),
                    round(dep_max, 2),
                    round(dep_std, 2),
                ],
                "Arrival Delay": [
                    round(arr_mean, 2),
                    round(arr_median, 2),
                    round(arr_min, 2),
                    round(arr_max, 2),
                    round(arr_std, 2),
                ],
            }
        )
        st.dataframe(delay_summary, width=450)

    with col_delay_breakdown:
        st.markdown("##### **Percentage Breakdown of Departure Delays**")
        conditions = [
            (df_delays["dep_delay"] <= 0),
            (df_delays["dep_delay"] > 0) & (df_delays["dep_delay"] <= 15),
            (df_delays["dep_delay"] > 15),
        ]
        categories = ["On-time", "1-15 min delayed", ">15 min delayed"]
        df_delays["delay_category"] = np.select(
            conditions, categories, default="Unknown"
        )
        delay_cat = df_delays["delay_category"].value_counts().reset_index()
        delay_cat.columns = ["Delay Category", "Count"]
        delay_cat["Percentage"] = (
            delay_cat["Count"] / delay_cat["Count"].sum() * 100
        ).round(2)

        fig_delay_cat = px.pie(
            delay_cat,
            names="Delay Category",
            values="Count",
        )

        fig_delay_cat.update_layout(width=500)
        st.plotly_chart(fig_delay_cat, use_container_width=False)

    query_carrier = (
        "SELECT carrier, COUNT(*) as flight_count FROM flights GROUP BY carrier"
    )
    df_carrier = pd.read_sql_query(query_carrier, conn)
    st.markdown("##### **Flight Count by Carrier**")
    fig_carrier = px.bar(
        df_carrier,
        x="carrier",
        y="flight_count",
        labels={"carrier": "Carrier", "flight_count": "Number of Flights"},
    )
    st.plotly_chart(fig_carrier, use_container_width=True)

    df_times = pd.read_sql_query(
        """
        SELECT year, month, day, dep_time, arr_time
        FROM flights
    """,
        conn,
    )

    def convert_to_datetime(row, time_col):
        try:
            if pd.isna(row[time_col]) or row[time_col] is None:
                return None
            time_value = int(row[time_col])
            time_str = f"{time_value:04d}"
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

    df_times["dep_time_dt"] = df_times.apply(
        lambda r: convert_to_datetime(r, "dep_time"), axis=1
    )
    df_times["arr_time_dt"] = df_times.apply(
        lambda r: convert_to_datetime(r, "arr_time"), axis=1
    )

    df_times["dep_hour"] = df_times["dep_time_dt"].dt.hour
    df_times["arr_hour"] = df_times["arr_time_dt"].dt.hour
    df_times["flight_date"] = df_times.apply(
        lambda r: pd.Timestamp(
            year=int(r["year"]), month=int(r["month"]), day=int(r["day"])
        ),
        axis=1,
    )

    df_dep_counts = (
        df_times.dropna(subset=["dep_hour"])
        .groupby(["flight_date", "dep_hour"])
        .size()
        .reset_index(name="dep_count")
    )
    df_arr_counts = (
        df_times.dropna(subset=["arr_hour"])
        .groupby(["flight_date", "arr_hour"])
        .size()
        .reset_index(name="arr_count")
    )

    df_dep_counts = df_dep_counts.rename(columns={"dep_hour": "hour"})
    df_arr_counts = df_arr_counts.rename(columns={"arr_hour": "hour"})

    df_combined = pd.merge(
        df_dep_counts, df_arr_counts, on=["flight_date", "hour"], how="outer"
    )
    df_combined["dep_count"] = df_combined["dep_count"].fillna(0)
    df_combined["arr_count"] = df_combined["arr_count"].fillna(0)
    df_combined["total"] = df_combined["dep_count"] + df_combined["arr_count"]

    stats = df_combined.groupby("hour")[["dep_count", "arr_count", "total"]].agg(
        ["mean", "std"]
    )
    stats.columns = ["_".join(col) for col in stats.columns]
    stats = stats.reset_index()

    stats = stats.rename(
        columns={
            "hour": "Hour",
            "dep_count_mean": "Mean_Departures",
            "dep_count_std": "Std_Departures",
            "arr_count_mean": "Mean_Arrivals",
            "arr_count_std": "Std_Arrivals",
            "total_mean": "Mean_Total",
            "total_std": "Std_Total",
        }
    )

    stats["Time_Label"] = stats["Hour"].apply(
        lambda h: f"{int(h):02d}:00 - {int(h):02d}:59"
    )

    fig = go.Figure()
    st.markdown(
        "##### **Mean Hourly Numbers of Flight Departures and Arrivals (with Std. Dev.)**"
    )
    fig.add_trace(
        go.Bar(
            x=stats["Time_Label"],
            y=stats["Mean_Departures"],
            name="departure",
            error_y=dict(
                type="data",
                array=stats["Std_Departures"],
                visible=True,
                thickness=1,
                width=0,
            ),
            width=0.3,
            marker=dict(line=dict(width=0.5)),
        )
    )
    fig.add_trace(
        go.Bar(
            x=stats["Time_Label"],
            y=stats["Mean_Arrivals"],
            name="arrival",
            error_y=dict(
                type="data",
                array=stats["Std_Arrivals"],
                visible=True,
                thickness=1,
                width=0,
            ),
            width=0.3,
            marker=dict(line=dict(width=0.5)),
        )
    )
    fig.add_trace(
        go.Bar(
            x=stats["Time_Label"],
            y=stats["Mean_Total"],
            name="total",
            error_y=dict(
                type="data",
                array=stats["Std_Total"],
                visible=True,
                thickness=1,
                width=0,
            ),
            width=0.3,
            marker=dict(line=dict(width=0.5)),
        )
    )
    fig.update_layout(
        barmode="group",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Flights",
        legend_title="Flight Type",
        bargap=0.2,
        bargroupgap=0.0,
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "Flight Route Statistics":

    airports_df = pd.read_csv("airports.csv")

    st.sidebar.header("Flight Selection ✈️")
    departure_airport = st.sidebar.selectbox(
        "Select Departure Airport", airports_df["name"].unique()
    )
    arrival_airport = st.sidebar.selectbox(
        "Select Arrival Airport", airports_df["name"].unique()
    )

    if departure_airport == arrival_airport:
        st.warning("⚠️ Please select a different destination airport.")
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

        df_flight_stats = pd.read_sql_query(
            query, conn, params=(departure_airport, arrival_airport)
        )

        st.markdown(
            f"""
    <h1 style='text-align: center; color: #4CAF50;'>Flight Statistics Dashboard</h1>
    <h3 style='text-align: center;'>From {departure_airport}  to {arrival_airport} </h3>
    <hr>
    """,
            unsafe_allow_html=True,
        )

        if df_flight_stats.empty:
            st.warning("No flight data available for the selected route.")
        else:
            total_flights = df_flight_stats["num_flights"].sum()
            avg_dep_delay = df_flight_stats["avg_dep_delay"].mean()
            avg_arr_delay = df_flight_stats["avg_arr_delay"].mean()
            earliest_dep = df_flight_stats["earliest_dep"].min()
            latest_dep = df_flight_stats["latest_dep"].max()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Flights", total_flights, "📊")
            col2.metric("Avg Departure Delay (min)", f"{avg_dep_delay:.2f}", "⏳")
            col3.metric("Avg Arrival Delay (min)", f"{avg_arr_delay:.2f}", "🚦")

            fig = px.bar(
                df_flight_stats,
                x="carrier",
                y="num_flights",
                color="carrier",
                title="Number of Flights per Airline",
                labels={"carrier": "Airline", "num_flights": "Number of Flights"},
            )
            st.plotly_chart(fig, use_container_width=True)

            fig_pie = px.pie(
                df_flight_stats,
                names="carrier",
                values="num_flights",
                title="Flight Distribution by Airline",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            with st.expander("📋 View Flight Data Table"):
                st.dataframe(
                    df_flight_stats.style.format(
                        {"avg_dep_delay": "{:.2f}", "avg_arr_delay": "{:.2f}"}
                    )
                )

            st.markdown("### 🌍 Departure & Arrival Airport Locations")
            airports_filtered = airports_df[
                airports_df["name"].isin([departure_airport, arrival_airport])
            ]
            fig_map = px.scatter_map(
                    airports_filtered,
                    lat="lat",
                    lon="lon",
                    text="name",
                    zoom=3,
                    title="Airport Locations",
            )
            st.plotly_chart(fig_map, use_container_width=True)

            query_top_destinations = """
        SELECT dest, COUNT(*) as num_flights
        FROM flights
        WHERE origin = (SELECT faa FROM airports WHERE name = ?)
        GROUP BY dest
        ORDER BY num_flights DESC
        LIMIT 5
        """
            df_top_destinations = pd.read_sql_query(
                query_top_destinations, conn, params=(departure_airport,)
            )

            if not df_top_destinations.empty:
                st.markdown("### 🌟 Top 5 Destinations from Departure Airport")
                st.dataframe(df_top_destinations)

    st.markdown(
        """
 <style>
    .stMetric label {
        font-size: 18px;
        font-weight: bold;
        color: #4CAF50;
    }
    .stDataFrame {
        border: 2px solid;
        border-radius: 10px;
    }
 </style>
 """,
        unsafe_allow_html=True,
    )

elif page == "Delay Analysis":

    def get_data():
        try:
            query = """
            SELECT f.dep_time, f.arr_delay, f.origin, w.wind_speed, w.temp, w.precip
            FROM flights f
            JOIN weather w ON f.origin = w.origin 
                AND f.year = w.year 
                AND f.month = w.month 
                AND f.day = w.day
            WHERE f.arr_delay IS NOT NULL;
            LIMIT 10000;
            """
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Failed to load delay analysis data: {e}")
            return pd.DataFrame()

    if df.empty:
        st.warning("No delay data available.")
        st.stop()

    if df.empty:
        st.warning("No delay data available.")
        st.stop()

    st.markdown(
        '<h1 style="text-align:center; color:black; font-size:50px; font-weight:bold; font-family:Trebuchet MS; border-bottom: 5px solid #8B008B; padding-bottom:10px;">✈️ Flight Delay Analysis</h1>',
        unsafe_allow_html=True,
    )

    df["hour"] = (df["dep_time"] // 100).astype(int)
    avg_delay_by_hour = df.groupby("hour")["arr_delay"].mean()

    st.markdown("### Average Delay Across Different Hours", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        x=avg_delay_by_hour.index, y=avg_delay_by_hour.values, marker="o", ax=ax
    )
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Average Delay (minutes)")
    st.pyplot(fig)

    st.write(
        "This graph illustrates how the average flight delay varies at different hours of the day."
    )

    st.markdown("### Wind Speed vs Delay", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        x=df["wind_speed"], y=df["arr_delay"], ax=ax, alpha=0.5, color="blue"
    )
    ax.set_title("Wind Speed vs Delay")
    ax.set_xlabel("Wind Speed (mph)")
    ax.set_ylabel("Arrival Delay (min)")
    st.pyplot(fig)

    st.write("🌬️ This graph shows how wind speed impacts arrival delays.")

    st.markdown("### Temperature vs Delay", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(x=df["temp"], y=df["arr_delay"], ax=ax, alpha=0.5, color="red")
    ax.set_title("Temperature vs Delay")
    ax.set_xlabel("Temperature (°F)")
    ax.set_ylabel("Arrival Delay (min)")
    st.pyplot(fig)

    st.write("🌡️ This graph visualizes the effect of temperature on flight delays.")

    st.markdown("### Rain vs Delay", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    df_rain = df.groupby("precip")["arr_delay"].mean().reset_index()
    sns.lineplot(
        x=df_rain["precip"], y=df_rain["arr_delay"], ax=ax, marker="o", color="green"
    )
    ax.set_title("Precipitation vs Delay")
    ax.set_xlabel("Precipitation (inches)")
    ax.set_ylabel("Arrival Delay (min)")
    st.pyplot(fig)

    st.write(
        "☔ This graph examines the relationship between rainfall and arrival delays."
    )


elif page == "Time-based Statistics":
    st.markdown(
        f"""
    <h1 style='text-align: center; color:rgb(19, 19, 31);'> Time-based Statistics</h1>
    <hr>
    """,
        unsafe_allow_html=True,
    )

    def get_flight_date():
        return st.date_input(
            "Select a day in 2023",
            datetime(2023, 1, 1),
            min_value=datetime(2023, 1, 1),
            max_value=datetime(2023, 12, 31),
        )

    def fetch_flight_data(selected_date):
        conn = sqlite3.connect("flights_database.db")
        query = """
     SELECT year, month, day, dep_time, sched_dep_time, arr_time, sched_arr_time, air_time, origin, dest
     FROM flights
     WHERE year = ? AND month = ? AND day = ?
     """
        params = (selected_date.year, selected_date.month, selected_date.day)
        flights_df = pd.read_sql(query, conn, params=params)
        return flights_df

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

    def process_flight_data(flights_df):
        for col in ["dep_time", "sched_dep_time", "arr_time", "sched_arr_time"]:
            flights_df[f"{col}_dt"] = flights_df.apply(
                lambda row: convert_to_datetime(row, col), axis=1
            )

        flights_df["dep_delay"] = (
            flights_df["dep_time_dt"] - flights_df["sched_dep_time_dt"]
        ).dt.total_seconds() / 60
        return flights_df

    st.write(
        "This page contains information about the flights occuring on a day of your choice."
    )
    st.subheader("Select a flight date")
    selected_date = get_flight_date()

    flights_df = fetch_flight_data(selected_date)

    if flights_df.empty:
        st.write("❌ No flights found for the selected date.")
    else:
        flights_df = process_flight_data(flights_df)

        total_flights = len(flights_df)

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
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    st.subheader("Amount of departing and incomming flights per airport ")

    col1, col2 = st.columns(2)

    for idx, (col, title, color) in enumerate(
        [("origin", "Departures", "purple"), ("dest", "Arrivals", "purple")]
    ):
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
            .properties(width=800, height=400)
        )

        if idx == 0:
            with col1:
                st.write(f"**Number of {title} from Each Airport**")
                st.altair_chart(chart, use_container_width=True)
        else:
            with col2:
                st.write(f"**Number of {title} from Each Airport**")
                st.altair_chart(chart, use_container_width=True)

    flights_df["hour"] = flights_df["sched_dep_time_dt"].dt.hour
    avg_delay = flights_df.groupby("hour")["dep_delay"].mean().reset_index()

    delay_chart = alt.Chart(avg_delay).mark_line(color="purple").encode(
        x=alt.X("hour:O", title="Hour of Day"),
        y=alt.Y("dep_delay:Q", title="Average Delay (minutes)"),
        tooltip=["hour", "dep_delay"],
    ) + alt.Chart(avg_delay).mark_circle(color="purple").encode(
        x="hour:O",
        y="dep_delay:Q",
        tooltip=["hour", "dep_delay"],
    )
    st.subheader("**Average Departure Delay Throughout the Day**")
    st.altair_chart(delay_chart, use_container_width=True)

    airtime_counts = flights_df["air_time"].dropna().value_counts().reset_index()
    airtime_counts.columns = ["Airtime (minutes)", "Number of Flights"]

    airtime_chart = (
        alt.Chart(airtime_counts)
        .mark_bar(color="purple")
        .encode(
            x=alt.X(
                "Airtime (minutes):Q",
                bin=alt.Bin(maxbins=50),
                title="Airtime (minutes)",
            ),
            y=alt.Y("Number of Flights:Q", title="Count of Flights"),
            tooltip=["Airtime (minutes)", "Number of Flights"],
        )
        .properties(width=800, height=500)
    )

    st.subheader("**Distribution of Flights by Airtime**")
    st.altair_chart(airtime_chart, use_container_width=True)
