# About the game

This is a turn-based strategy game in which players must battle each other using a host of "creatures," each of which has unique abilities and attributes. Victory is achieved when all of the opponent's creatures have been defeated.

# Setup

The game runs on four docker containers (managed by `compose.yaml`):

-   A React app built with Vite that uses radix-ui and tailwind.css
-   A Flask server to handle game and user logic
-   A Redis server to cache active games
-   A Postgres database

To set it up locally, take the following steps.

1. Clone this repository
2. Download, install, and run [Docker Desktop](https://docs.docker.com/desktop/), or just Docker Engine if you prefer
3. Navigate to the repository in your terminal and run `docker compose up -d client`

All done! You should be able to connect to the flask server at [localhost:8888](http://localhost:8888) and the database at port `5432` with username `dev_user` and password `dev_password`.

You can run `docker exec -it container-name bash` (replace the container-name) to run bash in the containers and navigate around.

### Running

Navigate to the client at [localhost:5173](http://localhost:5173) and then login with a username of your choice to interact with the UI.
You can script games for testing by accessing the container that hosts the flask server and editing/running `game_logic/draft_game.py`.

# Todo

### general

-   [x] ~~host project for play-testing~~
-   [ ] design fun and balanced creatures and abilities
-   [ ] real accounts and authentication

### client

-   [x] ~~login~~
-   [x] ~~join game~~
-   [x] ~~display game~~
-   [x] ~~play game~~
-   [x] ~~show when other player's commands are submitted and when the user's have cleared~~
-   [x] ~~play out turns in real time before showing final result~~
-   [x] ~~let user rewatch the current turn~~
-   [x] ~~show when game is over~~
-   [x] ~~show finished games~~
-   [x] ~~add visuals for abilities~~
-   [x] ~~show move range based on position at end of move if creature will move~~
-   [x] ~~let player choose turn to rewatch~~
-   [ ] let player step through turns tick by tick
-   [ ] turn log with textual description game history
-   [ ] display the player's owned creatures on the main page
-   [ ] lobby for open games

### backend

-   [x] ~~add basic game logic: matches, players, creatures, winning~~
-   [x] ~~use redis pub/sub to alert players when a turn has progressed~~
-   [x] ~~server routes to communicate with client~~
-   [x] ~~store each match tick~~
-   [x] ~~connect server with the postgres database and remove all mocked code~~
-   [x] ~~seed database with test data~~
-   [x] ~~proper logic for ending the game~~
-   [x] ~~endpoint for player game history~~
-   [x] ~~make all action within a match tick simultaneous~~
-   [x] ~~store ability location and data for each tick~~
-   [ ] create registry of open matches in redis
-   [ ] endpoint for open game lobby
-   [ ] provide useful error messages from server endpoints

### development todos

-   [ ] debugger workflow for docker containers
-   [ ] tests
-   [x] ~~automated deployment pipeline~~
