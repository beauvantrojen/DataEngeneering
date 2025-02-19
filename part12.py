import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sqlite3

airports_df = pd.read_csv("airports.csv")

fig_world = px.scatter_geo(airports_df,
                           lat="lat",
                           lon="lon",
                           hover_name="name",
                           title="Global Airport Locations",
                           color="alt")
fig_world.show()

us_airports = airports_df[airports_df['tzone'].str.contains("America", na=False)]

fig_us = px.scatter_geo(us_airports,
                        lat="lat",
                        lon="lon",
                        hover_name="name",
                        title="US Airport Locations",
                        color="alt")

fig_us.update_layout(geo=dict(scope="usa"))
fig_us.show()


def plot_flight_path_us(faa_code):

    nyc = airports_df[airports_df['faa'] == "JFK"][["lat", "lon"]].values[0]
    
    target_airport = airports_df[airports_df['faa'] == faa_code]
    target_coords = target_airport[["lat", "lon"]].values[0]

    is_us_airport = "America" in target_airport["tzone"].values[0]

    fig = px.scatter_geo(airports_df, lat="lat", lon="lon", hover_name="name",
                         title=f"Flight Path: JFK to {faa_code}", opacity=0.5)

    fig.add_scattergeo(lat=[nyc[0], target_coords[0]], lon=[nyc[1], target_coords[1]],
                       mode="lines", line=dict(width=2, color="red"))

    if is_us_airport:
        fig.update_layout(geo=dict(scope="usa"))

    fig.show()


def plot_multiple_flights(faa_codes):

    nyc = airports_df[airports_df['faa'] == "JFK"][["lat", "lon"]].values[0]
    
    fig = px.scatter_geo(airports_df, lat="lat", lon="lon", hover_name="name",
                         title="Multiple Flight Paths from JFK", opacity=0.5)
    
    for code in faa_codes:
        target_airport = airports_df[airports_df['faa'] == code]
        if not target_airport.empty:
            target_coords = target_airport[["lat", "lon"]].values[0]
            fig.add_scattergeo(lat=[nyc[0], target_coords[0]], lon=[nyc[1], target_coords[1]],
                               mode="lines", line=dict(width=2, color="blue"))
    
    fig.show()

# euclidean distance 
jfk = airports_df[airports_df['faa'] == "JFK"][["lat", "lon"]].values[0]
airports_df["euclidean_distance"] = np.sqrt((airports_df["lat"] - jfk[0])**2 + (airports_df["lon"] - jfk[1])**2)

plt.hist(airports_df["euclidean_distance"], bins=30, edgecolor='black')
plt.xlabel("Euclidean Distance from JFK")
plt.ylabel("Number of Airports")
plt.title("Distribution of Euclidean Distances from JFK")
plt.show()

# geodesic distance 
earth_radius_km = 6371

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return earth_radius_km * c

airports_df["geodesic_distance_km"] = airports_df.apply(
    lambda row: haversine(jfk[0], jfk[1], row["lat"], row["lon"]), axis=1
)

plt.hist(airports_df["geodesic_distance_km"], bins=30, edgecolor='black')
plt.xlabel("Geodesic Distance (km) from JFK")
plt.ylabel("Number of Airports")
plt.title("Distribution of Geodesic Distances from JFK")
plt.show()


time_zone_counts = airports_df['tzone'].value_counts()

plt.figure(figsize=(12, 6))
plt.bar(time_zone_counts.index, time_zone_counts.values)
plt.xticks(rotation=90)
plt.xlabel("Time Zones")
plt.ylabel("Number of Airports")
plt.title("Distribution of Airports Across Time Zones")
plt.show()


plot_flight_path_us("LAX") 
#plot_flight_path_us("TZR")  
# plot_multiple_flights(["LAX", "ORD", "ATL"])


