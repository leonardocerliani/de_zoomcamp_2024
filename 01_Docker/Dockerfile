FROM python:3.9

# psycopg2 is a postgres db adapter for python: sqlalchemy needs it
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY yellow_tripdata_2021-01.csv yellow_tripdata_2021-01.csv
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]


