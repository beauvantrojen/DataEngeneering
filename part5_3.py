import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_data():
    conn = sqlite3.connect("flights_database.db")
    query = """
    SELECT f.dep_time, f.arr_delay, f.origin, w.wind_speed, w.temp, w.precip
    FROM flights f
    JOIN weather w ON f.origin = w.origin 
        AND f.year = w.year 
        AND f.month = w.month 
        AND f.day = w.day
    WHERE f.arr_delay IS NOT NULL;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = get_data()

st.markdown('<h1 style="text-align:center; color:black; font-size:50px; font-weight:bold; font-family:Trebuchet MS; border-bottom: 5px solid #8B008B; padding-bottom:10px;">✈️ Flight Delay Analysis</h1>', unsafe_allow_html=True)

# Time of Day Analysis
df["hour"] = (df["dep_time"] // 100).astype(int)
avg_delay_by_hour = df.groupby("hour")["arr_delay"].mean()

st.markdown("### Average Delay Across Different Hours", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=avg_delay_by_hour.index, y=avg_delay_by_hour.values, marker="o", ax=ax)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Average Delay (minutes)")
st.pyplot(fig)

st.write("This graph illustrates how the average flight delay varies at different hours of the day.")

# Weather Factors Analysis
st.markdown("### Wind Speed vs Delay", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(x=df["wind_speed"], y=df["arr_delay"], ax=ax, alpha=0.5, color="blue")
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
sns.lineplot(x=df_rain["precip"], y=df_rain["arr_delay"], ax=ax, marker="o", color="green")
ax.set_title("Precipitation vs Delay")
ax.set_xlabel("Precipitation (inches)")
ax.set_ylabel("Arrival Delay (min)")
st.pyplot(fig)

st.write("☔ This graph examines the relationship between rainfall and arrival delays.")

# Auto-run Streamlit when script is executed
if __name__ == "__main__":
    import os
    os.system("streamlit run " + __file__)