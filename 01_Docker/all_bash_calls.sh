#!/bin/bash

# ------- First stage: running the postgres in the docker

# Postgres server
docker run --rm \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    -t postgres:13



# ------- Second stage: running both postgres and pgadmin in the same network

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



# ------- Third stage : ingestion py script with arguments

# testing the ingestion script manually
python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --csv_filename=yellow_tripdata_2021-01.csv


# running the script inside the docker container 
# after having built the image taxi_ingest:v001
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





# EOF