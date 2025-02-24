import numpy as np
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

connection = sqlite3.connect("flights_database.db")
cursor = connection.cursor()

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return 6371 * c  

# Bullet point 1
def compare_distances():
    query = """
    SELECT f.origin, f.dest, f.distance, 
           a1.lat AS origin_lat, a1.lon AS origin_lon,
           a2.lat AS dest_lat, a2.lon AS dest_lon
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    WHERE f.origin = 'JFK'
    """
    
    df = pd.read_sql_query(query, connection)

    miles_to_km = 1.60934
    df["distance_km"] = df["distance"] * miles_to_km
    
    df["computed_distance_km"] = df.apply(
        lambda row: haversine(row["origin_lat"], row["origin_lon"],
                              row["dest_lat"], row["dest_lon"]),
        axis=1
    )
    
    # Scatter plot: DB distance (converted to km) vs computed geodesic distance.
    plt.figure(figsize=(10, 6))
    plt.scatter(df["distance_km"], df["computed_distance_km"], alpha=0.5,
                label='DB distance (km) vs Geodesic (km)')
    max_val = max(df["distance_km"].max(), df["computed_distance_km"].max())
    plt.plot([0, max_val], [0, max_val], color='red', linestyle='--')
    plt.xlabel("Distance in DB (km)")
    plt.ylabel("Computed Geodesic Distance (km)")
    plt.title("Comparison of Flight Distances")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Histogram of the difference between the two distances (in km)
    df["difference"] = df["distance_km"] - df["computed_distance_km"]
    plt.figure(figsize=(10, 6))
    plt.hist(df["difference"], bins=30, edgecolor='black')
    plt.xlabel("Difference (DB km - Geodesic km)")
    plt.ylabel("Number of Flights")
    plt.title("Distribution of Distance Differences")
    plt.show()

#Bullet point 9
def plot_distance_vs_arr_delay():
    query = "SELECT distance, arr_delay FROM flights WHERE arr_delay IS NOT NULL"
    df = pd.read_sql_query(query, connection)
    plt.figure(figsize=(10, 6))
    plt.scatter(df["distance"], df["arr_delay"], alpha=0.3)
    plt.xlabel("Distance (miles)")
    plt.ylabel("Arrival Delay (minutes)")
    plt.title("Distance vs. Arrival Delay")
    plt.grid(True)
    plt.show()
    corr = df["distance"].corr(df["arr_delay"])
    print("Correlation between distance and arrival delay:", corr)

#Bullet point 10
def update_plane_speed():
    # (distance in miles; air_time in minutes; converting to mph)
    query = """
    SELECT tailnum, AVG((distance * 1.15078 / air_time) * 60) as avg_speed
    FROM flights
    WHERE air_time > 0
    GROUP BY tailnum
    """
    speeds = pd.read_sql_query(query, connection)
    cur = connection.cursor()
    for idx, row in speeds.iterrows():
        cur.execute("UPDATE planes SET speed = ? WHERE tailnum = ?", (row["avg_speed"], row["tailnum"]))
    connection.commit()

def check_plane_speeds():
    query = "SELECT tailnum, speed FROM planes LIMIT 10"
    speeds_df = pd.read_sql_query(query, connection)
    print(speeds_df)

def analyze_inner_product_vs_air_time():
    query = """
            SELECT flight, air_time, dep_time
            FROM flights
            WHERE air_time IS NOT NULL AND dep_time IS NOT NULL
            LIMIT 200
            """
    
    df = pd.read_sql_query(query, connection)
    inner_products = []
    air_times = []
    
    for idx, row in df.iterrows():
        ip = inner_product_flight_wind(row["flight"])
        if ip is not None:
            inner_products.append(ip)
            air_times.append(row["air_time"])
    if not inner_products:
        return
    
    plt.figure(figsize=(10, 6))
    plt.scatter(inner_products, air_times, alpha=0.6)
    plt.xlabel("Inner Product (flight direction · wind vector)")
    plt.ylabel("Air Time (minutes)")
    plt.title("Relationship between Inner Product and Air Time")
    plt.grid(True)
    plt.show()
    inner_arr = np.array(inner_products)
    air_arr = np.array(air_times)
    avg_positive = air_arr[inner_arr > 0].mean() if np.any(inner_arr > 0) else None
    avg_negative = air_arr[inner_arr < 0].mean() if np.any(inner_arr < 0) else None
    print("Average air time (positive inner product):", avg_positive)
    print("Average air time (negative inner product):", avg_negative)
        


if __name__ == "__main__":
    compare_distances()
    #plot_distance_vs_arr_delay()
    #update_plane_speed()
    #check_plane_speeds()