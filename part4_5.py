import sqlite3
import pandas as pd
import pytz
from datetime import datetime, timedelta

def compute_local_arrival_time(db_path="flights_database.db"):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT f.flight, f.origin, f.dest, f.sched_arr_time, f.year, f.month, f.day,
           a1.tzone AS origin_tz, a2.tzone AS dest_tz
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    WHERE f.sched_arr_time IS NOT NULL
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    def convert_to_datetime(row):
        """Convert HHMM format integer to actual flight date with proper time"""
        try:
            if pd.isna(row["sched_arr_time"]) or row["sched_arr_time"] is None:
                return None
            time_str = f"{int(row['sched_arr_time']):04d}"  # Convert to HHMM format
            flight_date = f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}"
            return datetime.strptime(f"{flight_date} {time_str}", "%Y-%m-%d %H%M")
        except (ValueError, TypeError):
            return None

    df["sched_arr_time_dt"] = df.apply(convert_to_datetime, axis=1)

    def safe_timezone(tz_string):
        """Convert to pytz timezone safely, catching errors"""
        try:
            return pytz.timezone(tz_string)
        except Exception as e:
            print(f"Invalid timezone '{tz_string}': {e}")
            return None  

    df["origin_tz"] = df["origin_tz"].apply(safe_timezone)
    df["dest_tz"] = df["dest_tz"].apply(safe_timezone)

    def compute_time_difference(row):
        """Compute time difference in hours between departure and arrival airport"""
        try:
            if row["origin_tz"] is None or row["dest_tz"] is None:
                return None
            origin_time = datetime(row["year"], row["month"], row["day"], 12, 0, 0, tzinfo=row["origin_tz"])
            dest_time = origin_time.astimezone(row["dest_tz"])
            return (dest_time - origin_time).total_seconds() / 3600
        except Exception as e:
            print(f"Time difference error: {e}")
            return None

    df["time_difference_hours"] = df.apply(compute_time_difference, axis=1)

    def adjust_timezone(row):
        """Adjust arrival time to the destination's local time zone"""
        if row["sched_arr_time_dt"] is None or row["time_difference_hours"] is None:
            return None
        try:
            local_arrival_time = row["sched_arr_time_dt"] + timedelta(hours=row["time_difference_hours"])
            return local_arrival_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error adjusting time zones: {e}")
            return None

    df["local_arrival_time"] = df.apply(adjust_timezone, axis=1)

    print(df[["flight", "origin", "dest", "sched_arr_time", "time_difference_hours", "local_arrival_time"]]) 
    
    return df

df_local_arrival = compute_local_arrival_time()
