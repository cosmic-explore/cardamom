# Setup

The game consists of a React client, a Flask server to handle game logic, a Redis server to cache active games, and a Postgres database, all of which run in seperate docker containers that are managed by `compose.yaml`.

1. Clone this repository
2. Download, install, and run [Docker Desktop](https://docs.docker.com/desktop/), or just Docker Engine if you prefer
3. Navigate to the repository in your terminal and run `docker compose up -d`

All done! You should be able to connect to the flask server at [localhost:8888](http://localhost:8888) and the database at port `5432` with username `dev_user` and password `dev_password`.

You can run `docker exec -it container-name bash` (replace the container-name) to run bash in the containers and navigate around.

### Running

The current state of the game can be interacted with by accessing the container that hosts the flask server and running `game_logic/draft_game.py`.

# Todo

-   code linting

### client

-   everything

### backend

-   use redis pub/sub to alert players when a turn has progressed
-   server routes to be used by the client
-   oauth authentication for players
-   seed database
-   connect server with the postgres database
