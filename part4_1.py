import sqlite3
import pandas as pd

database = sqlite3.connect("flights_database.db")
dataframe = pd.read_sql("SELECT * FROM flights", database)

print(dataframe.isnull().sum()) 

database.close()

# as there is a lot of data missing in the columns dep_time, arr_time and tailnum, i decide to give it the value '-' as they are too big to delte all instances
# and as the values can not be made up as that would be misinformation. The dep_delay and air_time could be made up but that would again be false information.
# so i fill the missing values with "NA"
dataframe = dataframe.fillna("NA")




