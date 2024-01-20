
import argparse

import pandas as pd
from sqlalchemy import create_engine
from time import time



def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    csv_filename = params.csv_filename


    # Create an engine for the postgresql. This will be used to check that the data types are 
    # correct, and to ingest the df into the psql db
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Load the first 10 rows to get the header
    df_head = pd.read_csv(csv_filename, nrows=10)

    # Change the type of two DATETIME columns which are now TEXT
    df_head.tpep_pickup_datetime = pd.to_datetime(df_head.tpep_pickup_datetime)
    df_head.tpep_dropoff_datetime = pd.to_datetime(df_head.tpep_dropoff_datetime)

    # Check that now everything is ok on the side of data types. Note that here
    # we use the engine created with sqlalchemy
    print(' ')
    print(f'Ingesting data into postgresql://{user}:{password}@{host}:{port}/{db}')
    print('using the following schema:')
    print(pd.io.sql.get_schema(df_head, name=table_name, con=engine))


    # ------------  Whole ingestion routine -------------------

    # Write the header - we can then check it inside pgcli using "\d ny_taxi"
    df_head.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    # The df has ~1.4M rows, so we will ingest it 100000 rows at a time with an iterator

    # Create an iterator to feed the db 100000 rows at a time
    df_iter = pd.read_csv(csv_filename, iterator=True, chunksize=100000)

    while True:
        try:
            t_start = time()

            df = next(df_iter)

            # fix the type of these two fields. Should be datetime
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name = table_name, con=engine, if_exists='append')

            t_end = time()
            
            print('inserted another chunk... it took %.3f seconds' % (t_end - t_start))
        except StopIteration:
            print('all rows ingested')
            break
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest csv data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='pw for postgres')
    parser.add_argument('--host', help='hostname for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write the data')
    parser.add_argument('--csv_filename', help='csv filename')

    args = parser.parse_args()

    main(args)