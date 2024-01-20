# Docker and Postgres

## Intro to Docker
[video](https://www.youtube.com/watch?v=EYNwNlOrpr0)

### Python container from the command line
To run a python container, we can simply do it from the command line, providing the `-it` argument to make it interactive:

```bash
docker run --rm -it python:3.9
```
If it's not present locally, docker will pull the container from dockerhub.

However let's say we want to use Pandas, which is not installed in this image. In this case we need to install it manually once we are inside the container.

```bash
docker run --rm -it python:3.9 bash

# and from inside the container:
pip install pandas
```

However when we exit the container, Pandas will not be anymore present.

### Custom image with Dockerfile
To ensure the persistence of the installed packages - among other things - we can define a Dockerfile.

Docker will first pull the python image, and then install pandas

**NB**

```bash
# Dockerfile

FROM python:3.9

RUN pip install pandas

ENTRYPOINT [ "bash" ]
```

We build the image and then we run it:

```bash
docker build -f Dockerfile_initial -t test:pandas .
docker run --rm -it -t test:pandas
```

### Running a local python script inside the container
Of course right now the container is not very useful, since it's not really doing anything.

Let's suppose that we want our container to carry out a very specific action: run a pipeline defined by a python script called `pipeline.py` that we will load in the current folder.

To this aim, we can specify in the Dockerfile that every time the (soon-to-be-built) corresponding image is run, it should first copy the file from the directory where we run the image.

Also, we will instruct docker to run the command for executing the pipeline, instead of entering bash. Therefore we can also remove the interactivity.

Finally, to make it a bit more interesting, we can also pass an argument to the python script.


```python
# pipeline.py

import sys
import pandas as pd

day = sys.argv[1]
print(f'job finished succesfully for day = {day}')
```

```bash
# Dockerfile_initial

FROM python:3.9

RUN pip install pandas

WORKDIR /app
COPY pipeline.py pipeline.py

ENTRYPOINT [ "python", "pipeline.py" ]
```

```bash
docker build -t test:pandas .
docker run --rm -t test:pandas "2024-15-01"
```


##  Ingesting NY Taxi Data into Postgres
[video](https://www.youtube.com/watch?v=2JM-ziJt0WI)

We previously used a docker container to carry out a specific task and then stop.

Now we want to use a container to run a service. Specifically, we want the container to serve a database of NY taxi rides using Postgres.

### Running a Postgres container from the commandline
First let's run it from the command line to see what parameters we need to provide. Later we will write the corresponding specifications into the Dockerfile

```bash
docker run --rm \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    -t postgres:13
```

Of note, here we define a few environmental variables that Postgres requires, as well as the port where we will find our db service.


We also specify volume mapping from a local folder to a folder inside the Postgres container. This is necessary for data persistance: once we ingest the data inside Postgres, we want it to be available even when we stop and restart the container.

We can now inspect the db using `pgcli` : a terminal-based db client which can be [installed](https://www.pgcli.com/install) using pip.

```
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

### Ingesting the NYC taxi data (ipynb version)
Now that we have our Postgres server running, we need to ingest the data in it.

The rides for the NYC Taxi for different years can be found on the [official website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) in Parquet format.

Here we use a csv file, which can be downloaded using wget:
```
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```
Use gunzip to extract the csv.

We will then write an ingestion script using Python. In addition to the explanation in the video, here I will also create a specific python virtual environment for the operation and install juoyter in it.

```
python3 -m venv docker-venv
source docker-venv/bin/activate
pip install pandas jupyter sqlalchemy
```


The details of the ingestion script are in the `do_ingest_csv_to_Postgres.ipynb` notebook. Just note that sqlalchemy will probably complain about not finding `psycopg2`. If this is the case, you can install it with the following:

```bash
sudo apt-get install libpq-dev
pip install psycopg2

```

Once the csv is fully ingested, we can inspect it in pgcli using the following commands  (besides regular SQL).

**db name : ny_taxi** \
**table : yellow_taxi_data**

```
\dt : shows the available tables
\d [db_name]  : shows the schema of selected db
```
Note: in pgcli, a suggestion is confirmed with the right arrow key


```
pgcli -h localhost -p 5432 -u root -d ny_taxi

Server: PostgreSQL 13.13 (Debian 13.13-1.pgdg120+1)
Version: 3.3.1
Home: http://pgcli.com
root@localhost:ny_taxi> \dt
+--------+------------------+-------+-------+
| Schema | Name             | Type  | Owner |
|--------+------------------+-------+-------|
| public | yellow_taxi_data | table | root  |
+--------+------------------+-------+-------+
SELECT 1
Time: 0.026s
root@localhost:ny_taxi> \d yellow_taxi_data
+-----------------------+------------------+-----------+
| Column                | Type             | Modifiers |
|-----------------------+------------------+-----------|
| index                 | bigint           |           |
| VendorID              | bigint           |           |
| tpep_pickup_datetime  | text             |           |
| tpep_dropoff_datetime | text             |           |
| passenger_count       | bigint           |           |
| trip_distance         | double precision |           |
| RatecodeID            | bigint           |           |
| store_and_fwd_flag    | text             |           |
| PULocationID          | bigint           |           |
| DOLocationID          | bigint           |           |
| payment_type          | bigint           |           |
| fare_amount           | double precision |           |
| extra                 | double precision |           |
| mta_tax               | double precision |           |
| tip_amount            | double precision |           |
| tolls_amount          | bigint           |           |
| improvement_surcharge | double precision |           |
| total_amount          | double precision |           |
| congestion_surcharge  | double precision |           |
+-----------------------+------------------+-----------+
Indexes:
    "ix_yellow_taxi_data_index" btree (index)

Time: 0.024s
root@localhost:ny_taxi> select count(*) from yellow_taxi_data
+---------+
| count   |
|---------|
| 1369765 |
+---------+
SELECT 1
Time: 0.065s

```

### Ingesting the NYC taxi data (script version)
I generally prefer python scripts to jupyter notebook - mostly because I come from RStudio, where a notebook is text only, and you don't need to learn many shortcuts to navigate the nb and can execute single lines or selections.

This might change soon now that I discovered that the second of the above features (the most important for me) is actually available in jupyterlab (although they made it [as difficult as possible to enable it](https://stackoverflow.com/questions/56460834/how-to-run-a-single-line-or-selected-code-in-a-jupyter-notebook-or-jupyterlab-ce))

Here's the same logic of the nb, but in a regulard python script:

```python
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
```


## Connecting pgAdmin and Postgres
[video](https://www.youtube.com/watch?v=hCAIVe9N0ow)

We are now running Postgres in a container. We will run also pgAdmin in a container, and connect them.

```bash
docker run --rm -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4
```

Once the container starts, we can go to `localhost:8080` and login with the credentials we defined in the the docker run command.

Now we can right-click on the Servers and Register our server (it was previously Create >> Server) with the following parameters:

```
hostname : localhost
port : 5432
user : root
pw : root
```

**This is where the important part comes:** when we try to save the server details, we will get an error, because the localhost of the container where pgAdmin is running is different from the localhost of the container where Postgres is running.

In order for the Postgres server and pgAdmin tool to talk to each other, we need to place them in the same network.

To this aim, we need to create a docker network, and then modify our two docker run containers so that they connect to that network.

After stopping the two running containers (if you still have them running) we run:

```bash
# Network
docker network create pg-network

# Postgres server
# --network=pg-network : the name we gave it above
# --name pg-database : the name by means of which the network will be discoverable by pgAdmin
docker run --rm \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    -t postgres:13


# pgAdmin
docker run --rm -it   \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com"   \
    -e PGADMIN_DEFAULT_PASSWORD="root"   \
    -p 8080:80   \
    --network=pg-network \
    dpage/pgadmin4
```

Now we can go again in `localhost:8080`, connect and register the postgres server. Importantly, in Connection >> Host name/address we will now put `pg-database`

```
hostname : pg-database
port : 5432
user : root
pw :
```

At this point we can go to Local Docker >> ny_taxi >> Schemas >> Tables >> yellow_taxi_data, right click and start to write SQL queries


## Putting the ingestion script into Docker
[video](https://www.youtube.com/watch?v=B1WwATwf-vY)

Now we want to create a python script `ingest_data.py` that will take in arguments (e.g. db_name, user, pw) and run when the docker containers are fired up, to ingest the data from the csv into postgres.

We use `arparse` to allow taking input arguments.

To test the script we can first drop the table (in pgAdmin or pgcli).

The final - heavily commented - script is below. A cleaner version by Alvaro Navas can be found [here](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/1_intro/ingest_data.py).

If you created a specific python virtual env, don't forget to activate it before running the script (in my case `source docker-env/bin/activate`)

```python

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
```

Now we need to create a new Dockerfile which contains the instruction to run the `ingest_data.py` script as the container is started. Note that in this Dockerfile we will need to first pip install the python libraries we need to run the ingestion script.

Differently from what explained in the video, I will not install wget since I am using the local, already downloaded csv file.

```bash
# Dockerfile ingestion
FROM python:3.9

# psycopg2 is a postgres db adapter for python: sqlalchemy needs it
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]
```

Build the image
```bash
docker build -f Dockerfile_ingestion -t taxi_ingest:v001 .
```

**NB**: the `ny_taxi_postgres_data`, which contains the postgres db, is created by `root`, therefore I experienced a `cannot stat` error when building this new image as `$USER`. Even putting this directory in `.dockerignore` didn't work. The solution was to sudo rm the directory first - it will be re-created by the ingestion script anyway.

Now we can run the `taxi_ingest:v001` by passing the argument that the `ingest_data.py` requires. Also, remember that we need to be in the `pg-network` network.

```bash

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pg-database \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --csv_filename=yellow_tripdata_2021-01.csv

```

Almost miracolously, everything went fine and the whole csv file was ingested in the postgres db. You can check it with pgcli:

```
pgcli -h localhost -u root -p 5432 -d ny_taxi

root@localhost:ny_taxi> \dt
+--------+-------------------+-------+-------+
| Schema | Name              | Type  | Owner |
|--------+-------------------+-------+-------|
| public | yellow_taxi_trips | table | root  |
+--------+-------------------+-------+-------+

root@localhost:ny_taxi> select count(*) from yellow_taxi_trips
+---------+
| count   |
|---------|
| 1369765 |
+---------+
```



## Everything, altogether at the same time with docker-compose
[video](https://www.youtube.com/watch?v=hKI6PkPhpa0)

With `docker-compose` we can running all the services we need just by specifying a yaml file

```bash
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
```

Note that the network name is not specified since docker-compose takes care of creating a network shared by all specified services.

When configuring pgAdmin, the name to use is `pgdatabase`

Also, when we run the pgAdmin service, the postgres server would need to be configured from scratch. To avoid this, we can map locally the container directory where pgAdmin stores the information about registered servers. This is achieved by the line above

```bash
volumes:
  - "./data_pgadmin:/var/lib/pgadmin"
```

One issue is that the owner of this directory is the user `pgadmin` which might not be present locally. For some reasons, I discovered that in these cases we should use `999` as owner. Therefore we need to create the directory and then change the ownership and priviledges accordingly as shown below:

```bash
mkdir data_pgadmin
sudo chown 999:root data_pgadmin
sudo chmod 775 data_pgadmin
```

When this is done, we can start the services with `docker-compose up` and access the postgres db as well as pgAdmin as before. The first time we need to register the server in pgAdmin, but from the second time these information will persist in the `$PWD/data_pgadmin` directory.

To stop the containers launched by docker-compose we can simply do Ctrl-C or more properly `docker-compose down`



EOF
