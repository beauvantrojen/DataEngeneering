import sqlite3
import math
import pandas as pd
import matplotlib.pyplot as plt

def haversine_distance(lat1, lon1, lat2, lon2, radius=3959):

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
  
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return radius * c

def create_comparison_table(db_path='flights_database.db'):

    conn = sqlite3.connect(db_path)
    query = """
    SELECT f.origin, f.dest, f.distance, 
           a1.lat AS orig_lat, a1.lon AS orig_lon, 
           a2.lat AS dest_lat, a2.lon AS dest_lon
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    WHERE f.origin = 'JFK'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['Computed Distance'] = df.apply(
        lambda row: haversine_distance(row['orig_lat'], row['orig_lon'], row['dest_lat'], row['dest_lon']),
        axis=1
    )
    
    df['Difference'] = abs(df['distance'] - df['Computed Distance'])
    df['distance'] = df['distance'].round(2)
    df['Computed Distance'] = df['Computed Distance'].round(2)
    df['Difference'] = df['Difference'].round(2)
    
    return df

def plot_scatter_comparison(df):
    plt.figure(figsize=(8, 6))
    
    plt.scatter(df['distance'], df['Computed Distance'], alpha=0.6, color='blue', label="Flights")

    max_val = max(df['distance'].max(), df['Computed Distance'].max())
    plt.plot([0, max_val], [0, max_val], 'r', label='y = x')
    
    plt.xlabel("Stored Distance (miles)")
    plt.ylabel("Computed Distance (miles)")
    plt.title("Scatter Plot: Stored vs. Computed Distances for JFK Flights")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df_comparison = create_comparison_table()
    
    #print only the first 25 rows in the console to reamin readability (all results are compared in scatter plot)
    print(df_comparison.head(25).to_string(index=True))
    
    #scatter plot using all results 
    plot_scatter_comparison(df_comparison)


