## Putting all together with docker-compose
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
