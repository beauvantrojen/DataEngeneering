import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sqlite3
import math

#For each flight, the origin from which it leaves can be fount in the variable origin in the table . Identify all different airports in NYC from
#which flights depart and save a contain the information about those
#airports from airports

def get_nyc_airports(db_path='flights_database.db'):
    conn = sqlite3.connect(db_path)

    query_origins = """
        SELECT DISTINCT origin
        FROM flights
    """
    origins_df = pd.read_sql_query(query_origins, conn)
    origin_codes = origins_df['origin'].tolist()
 
    query_airports = f"""
        SELECT *
        FROM airports
        WHERE faa IN (
            SELECT DISTINCT origin
            FROM flights
        )
    """
    nyc_airports_df = pd.read_sql_query(query_airports, conn)
    conn.close()
    
    return nyc_airports_df

nyc_airports = get_nyc_airports('flights_database.db')

print(nyc_airports)

#Write a function that takes a month and day and an airport in NYC as input,
#and produces a figure similar to the one from part 1 containing all destinations
#of flights on that day.

def plot_destinations_on_date(month, day, origin_airport, db_path='flights_database.db'):
    """
    Creates a map with lines from the given origin_airport in NYC
    to all destinations for flights on the specified (month, day).
    """
    conn = sqlite3.connect(db_path)
   
    query = """
        SELECT
            a.lat AS origin_lat,
            a.lon AS origin_lon,
            b.lat AS dest_lat,
            b.lon AS dest_lon,
            f.dest AS dest_code
        FROM flights f
        JOIN airports a ON f.origin = a.faa
        JOIN airports b ON f.dest   = b.faa
        WHERE f.month = ?
          AND f.day   = ?
          AND f.origin = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(month, day, origin_airport))
    conn.close()
    
    if df.empty:
        print(f"No flights found on {month}/{day} from {origin_airport}.")
        return
    
    # We can make a scatter_geo figure with lines
    # Each row is a single flight. You can choose to group by unique destinations, etc.
    fig = px.scatter_geo(
        df,
        lat="dest_lat", lon="dest_lon",
        hover_name="dest_code",
        title=f"All destinations from {origin_airport} on {month}/{day}"
    )
    
    # Add lines from origin → each destination
    # One approach is to add each flight as a separate trace:
    for _, row in df.iterrows():
        fig.add_scattergeo(
            lat=[row["origin_lat"], row["dest_lat"]],
            lon=[row["origin_lon"], row["dest_lon"]],
            mode='lines',
            line=dict(width=1, color='blue'),
            showlegend=False
        )
    
    fig.update_layout(
        geo=dict(
            scope="world",  # or "usa" if you want to zoom in
            projection_type="equirectangular",
            showland=True,
        )
    )
    
    fig.show()

plot_destinations_on_date(1, 21, "EWR")

# 4 Also write a function that returns statistics for that day, i.e. how many flights,
#how many unique destinations, which destination is visited most often, etc.

def get_flight_stats(month, day, origin_airport, db_path='flights_database.db'):
   
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT dest,
               COUNT(*) AS flights_to_dest
        FROM flights
        WHERE month = ?
          AND day   = ?
          AND origin = ?
        GROUP BY dest
        ORDER BY flights_to_dest DESC
    """
    df = pd.read_sql_query(query, conn, params=(month, day, origin_airport))
    conn.close()
    
    total_flights = df['flights_to_dest'].sum()
    unique_destinations = df.shape[0]
    top_destination = df.iloc[0]['dest']
    top_count = df.iloc[0]['flights_to_dest']

    least_destination = df.iloc[-1]['dest']
    least_count = df.iloc[-1]['flights_to_dest']
    
    avg_flights = round(total_flights / unique_destinations) if unique_destinations else 0
    min_flights = df['flights_to_dest'].min()
    median_flights = df['flights_to_dest'].median()
    
    return {
        "total_flights": total_flights,
        "unique_destinations": unique_destinations,
        "top_destination": top_destination,
        "top_destination_count": top_count,
        "least_destination": least_destination,
        "least_destination_count": least_count,
        "average_flights_per_destination": avg_flights,
        "minimum_flights_to_a_destination": min_flights,
        "median_flights_to_destination": median_flights
    }
#example
stats = get_flight_stats(1, 15, "JFK")
s = "Statistics:"
print("\033[1m" + s + "\033[0m")
for key, value in stats.items():
    print(f"{key}: {value}")

# 5 Write a function that, given a departing airport and an arriving airport, returns a dict describing how many times each plane type was used for that flight
#trajectory. For this task you will need to match the columns to type
#in the table planes and match this to the tailnum s in the table .

def get_plane_type_usage(origin_airport, dest_airport, db_path='flights_database.db'):
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT p.type AS plane_type,
               COUNT(*) AS usage_count
        FROM flights f
        JOIN planes p
          ON f.tailnum = p.tailnum
        WHERE f.origin = ?
          AND f.dest   = ?
        GROUP BY p.type
        ORDER BY usage_count DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(origin_airport, dest_airport))
    conn.close()
    usage_dict = dict(zip(df['plane_type'], df['usage_count']))
    return usage_dict

#example
usage = get_plane_type_usage("LGA", "CLT")
s = "Plane type usage:"
print("\033[1m" + s + "\033[0m")
for key, value in usage.items():
    print(f"{key}: {value}")

# Write a function that computes the inner product between the flight direction and the wind speed of a given flight

def get_airport_coords(conn, faa_code):
    cursor = conn.cursor()
    cursor.execute("SELECT lat, lon FROM airports WHERE faa = ?", (faa_code,))
    row = cursor.fetchone()
    return row if row else None

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    diff_lon = lon2_rad - lon1_rad
    x = math.sin(diff_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad)
         - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(diff_lon))

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

def compute_flight_direction(conn, origin_faa, dest_faa):
    origin_coords = get_airport_coords(conn, origin_faa)
    dest_coords = get_airport_coords(conn, dest_faa)
    if not origin_coords or not dest_coords:
        return None
    return calculate_bearing(origin_coords[0], origin_coords[1],
                             dest_coords[0], dest_coords[1])

def inner_product(flight_dir_deg, wind_speed, wind_dir_deg):
    fd_rad = math.radians(flight_dir_deg)
    wd_rad = math.radians(wind_dir_deg)
    return wind_speed * math.cos(wd_rad - fd_rad)

def get_weather(conn, origin, year, month, day, hour):
    cursor = conn.cursor()
    query = """
        SELECT wind_speed, wind_dir
        FROM weather
        WHERE origin = ?
          AND year = ?
          AND month = ?
          AND day = ?
          AND hour = ?
        LIMIT 1;
    """
    cursor.execute(query, (origin, year, month, day, hour))
    row = cursor.fetchone()
    return row if row else None

def compute_inner_products_for_day(conn, origin, dest, year, month, day):
    cursor = conn.cursor()
    query = """
        SELECT dep_time, flight, tailnum, arr_time, arr_delay
        FROM flights
        WHERE origin = ?
          AND dest = ?
          AND year = ?
          AND month = ?
          AND day = ?;
    """
    cursor.execute(query, (origin, dest, year, month, day))
    flights_data = cursor.fetchall()
    if not flights_data:
        print(f"No flights found for {origin}->{dest} on {year}-{month}-{day}.")
        return []

    flight_dir = compute_flight_direction(conn, origin, dest)
    if flight_dir is None:
        print(f"Could not compute bearing for {origin}->{dest}.")
        return []

    results = []
    for (dep_time, flight_num, tailnum, arr_time, arr_delay) in flights_data:
        if not dep_time:
            continue
      
        dep_hour = dep_time // 100

        weather = get_weather(conn, origin, year, month, day, dep_hour)
        if not weather:
            continue
        wind_speed, wind_dir_deg = weather
        ip_val = inner_product(flight_dir, wind_speed, wind_dir_deg)

        results.append({
            "flight": flight_num,
            "dep_time": dep_time,
            "hour": dep_hour,
            "wind_speed": wind_speed,
            "wind_dir": wind_dir_deg,
            "bearing": flight_dir,
            "inner_product": ip_val
        })
    return results

def print_table(data):
 
    col_headers = ["Flight", "dep_time", "hour", "wind", "bearing", "inner_prod"]
    col_widths = [8, 8, 4, 18, 8, 10]

    def print_separator():
        line = "+"
        for w in col_widths:
            line += "-" * w + "+"
        print(line)


    print_separator()
    header_line = "|"
    for i, header in enumerate(col_headers):
        header_line += f"{header:^{col_widths[i]}}|"
    print(header_line)
    print_separator()

    
    for row in data:
        flight_str = str(row["flight"])
        dep_str = str(row["dep_time"])
        hour_str = str(row["hour"])
        wind_str = f"{row['wind_speed']:.1f} kts @ {row['wind_dir']:.1f}°"
        bearing_str = f"{row['bearing']:.1f}°"
        ip_str = f"{row['inner_product']:.2f}"

        row_values = [flight_str, dep_str, hour_str, wind_str, bearing_str, ip_str]
        row_line = "|"
        for i, val in enumerate(row_values):
            row_line += f"{val:<{col_widths[i]}}|"
        print(row_line)
    print_separator()


conn = sqlite3.connect("flights_database.db")

origin_faa = "JFK"
dest_faa = "LAX"
year = 2023
month = 1
day = 1

data = compute_inner_products_for_day(conn, origin_faa, dest_faa, year, month, day)
if data:
    print_table(data)

 
    