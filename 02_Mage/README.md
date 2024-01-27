# Mage

The repo with the links to all videos and slides is [at this link](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration#221----intro-to-orchestration). Here there will be only some notes for the practical part.

## Configuring Mage
[video](https://www.youtube.com/watch?v=tNiV7Wp08XE)

We will be running Mage from a docker container. Matt has prepared the docker compose yaml for us in [this repo](https://github.com/mage-ai/mage-zoomcamp).

Go ahead and clone it in the local dir.

```bash
git clone https://github.com/mage-ai/mage-zoomcamp.git
```

after that `cp dev.env .env`, because we will have some secrets in the .env, which is also in the .gitignore (we don't want to share secrets with anybody ;))

Then we can run `docker compose build` (NB: 3.49GB!)

At some point in the future, we will be prompted to update Mage. To do so:

```bash
docker pull mageai/mageai:latest
```

Finally, we can fire up the pulled image with `docker compose up`

At this point, we should have Mage available at `localhost:6789`

For this course, we are running the Postgres and the core Mage service.

Follow up: a [~3 min demo video](https://www.youtube.com/watch?v=stI-gg4QBnI&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) featuring the "hello world" of the data world (i.e. the Titanic dataset)


## Configuring Postgres
[video](https://www.youtube.com/watch?v=pmhI-ezd3BE)
Here we will configure the PSQL connection so that it can talk to the PSQL server/db which exists in the container we are using for the course.

We can quickly check that the postgres server is running in a couple of ways: first, simply by checking the output of `docker ps`. Also - at the risk of being pedantic - we can enter the container with a shell and then connect with `psql`

```bash
docker exec -it [container name/ID] sh
psql -h localhost -p 5432 -U postgres -d postgres
```

To use the postgres server in our pipeline, we first need to define a profile where we pass our credentials.

Note that in the `postgres` section of the `docker-compose.yml` file we specify a file of **environmental variables** `.env`. This is a way to prevent sharing our uname/pw with the rest of the world, provided that we put the `.env` file in out `.gitignore`.

Now we can go to the Mage gui, open Files and edit the `io_config.yaml`.
At the bottom we can create a `dev` environment where we specify how to retrieve our credentials. This is done in [Jinja](https://en.wikipedia.org/wiki/Jinja_(template_engine)) style using the `env_var()` function:

```bash
dev:
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: "{{ env_var('POSTGRES_DBNAME') }}"
  POSTGRES_SCHEMA: "{{ env_var('POSTGRES_SCHEMA') }}" # Optional
  POSTGRES_USER: "{{ env_var('POSTGRES_USER') }}"
  POSTGRES_PASSWORD: "{{ env_var('POSTGRES_PASSWORD') }}"
  POSTGRES_HOST: "{{ env_var('POSTGRES_HOST') }}"
  POSTGRES_PORT: "{{ env_var('POSTGRES_PORT') }}"
```

gif
![](imgs/create_basic_pipeline.gif)

mov
![](imgs/create_basic_pipeline.mov)

webm
![](imgs/create_basic_pipeline.webm)

















EOF
