import pandas as pd
from sqlalchemy import create_engine
from time import time

# Create an engine for the postgresql. This will be used to check that the data types are 
# correct, and to ingest the df into the psql db
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


# Load the first 10 rows and inspect them
df_TEST = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=10)
df_TEST

# Get the schema using pandas and see if all the data types are correct
print(pd.io.sql.get_schema(df_TEST, name='yellow_taxi_data'))

# We need to change the type of two columns which are now TEXT
df_TEST.tpep_pickup_datetime = pd.to_datetime(df_TEST.tpep_pickup_datetime)
df_TEST.tpep_dropoff_datetime = pd.to_datetime(df_TEST.tpep_dropoff_datetime)

# Check that now everything is ok on the side of data types. Note that here
# we use the engine created with sqlalchemy
print(pd.io.sql.get_schema(df_TEST, name='yellow_taxi_data', con=engine))


# ------------  Whole ingestion routine -------------------

# Write the header - we can then check it inside pgcli using "\d ny_taxi"
df_TEST.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

# The df has ~1.4M rows, so we will ingest it 100000 rows at a time with an iterator

# Create an iterator to feed the db 100000 rows at a time
df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=1e5)

while True:
# for i in range(4):
    t_start = time()

    df = next(df_iter)

    # fix the type of these two fields. Shuold be datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.to_sql(name = 'yellow_taxi_data', con=engine, if_exists='append')

    t_end = time()
    
    print('inserted another chunk... it took %.3f seconds' % (t_end - t_start))
