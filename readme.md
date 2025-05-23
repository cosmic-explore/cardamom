# Setup

The game consists of a React client, a Flask server to handle game logic, a Redis server to cache active games, and a Postgres database, all of which run in seperate docker containers that are managed by `compose.yaml`.

1. Clone this repository
2. Download, install, and run [Docker Desktop](https://docs.docker.com/desktop/), or just Docker Engine if you prefer
3. Navigate to the repository in your terminal and run `docker compose up -d`

All done! You should be able to connect to the flask server at [localhost:8888](http://localhost:8888) and the database at port `5432` with username `dev_user` and password `dev_password`.

You can run `docker exec -it container-name bash` (replace the container-name) to run bash in the containers and navigate around.

### Running

Navigate to the client at [localhost:5173](http://localhost:5173) and then login with a username of your choice to interact with the UI.
You can script games for testing by accessing the container that hosts the flask server and editing/running `game_logic/draft_game.py`.

# Todo

### general

-   host project

### client

-   ~~login~~
-   ~~join game~~
-   ~~display game~~
-   play game
-   real account authentication
-   see open games
-   everything else

### backend

-   ~~add basic game logic: matches, players, creatures, winning~~
-   ~~use redis pub/sub to alert players when a turn has progressed~~
-   ~~server routes to communicate with client~~
-   oauth authentication for players
-   seed database
-   connect server with the postgres database
-   tests

### development todos

-   ~~frontend linting~~
-   backend linting
