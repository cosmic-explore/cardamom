import os
import json
import redis
from flask import Flask, Response, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from constants import TEST_MATCH_CHANNEL
from classes.player import get_test_player_1, get_test_player_2
from game_logic.command_handler import command_from_dict, submit_command
from game_logic.match_handler import attempt_join_match, get_active_match_of_player, start_match, publish_match_update

app = Flask(__name__)

#configure redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://redis:6379') # docker adds "redis" to the DNS
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-origin cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = os.getenv('SECRET_KEY', default='DEV_SECRET_KEY')
server_session = Session(app)
redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# configure cors
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

def event_stream(channel):
    """Streams events from the given redis channel"""
    app.logger.debug(f"starting listener for {channel}")
    redis_listener = redis_connection.pubsub()
    redis_listener.subscribe(channel)
    for message in redis_listener.listen():
        app.logger.debug(f"Broadcasting message on channel {channel}")
        # convert to str because data must be bytes
        yield f"data: {json.dumps(message['data'])}\n\n"

@app.route('/')
def hello_world():
    return '<h1>Hello from Flask & Docker</h1>'

@app.route('/login', methods=['POST'])
def login():
    """Currently allows a user to login as one of the two test players"""
    # TODO: implement actual login
    request_data = request.get_json()
    player_name = request_data["player_name"]
    app.logger.debug(f"Logging in player {player_name}")
    session["player_name"] = player_name
    player = get_test_player_1() if session.get("player_name") == "Safari" else get_test_player_2()
    app.logger.debug(f"Logged in {player.name}")
    return jsonify(player.to_simple_dict())

@app.route('/match/join', methods=['GET'])
def join_match():
    # TODO: implement for real - the current implementation is to test related functionality
    # get player, add them to the match, and return match data
    player_name = session.get("player_name")
    app.logger.debug(f"found player {player_name} from session")
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    match = attempt_join_match(player)
    if match is not None:
        if match.player_1 is not None and match.player_2 is not None:
            start_match(match)
        return Response(event_stream(TEST_MATCH_CHANNEL), mimetype="text/event-stream")
    else:
        return Response(status=500)
    
@app.route('/match/refresh', methods=['GET'])
def refresh_match():
    """Send match data and start match after both players have connected"""
    # TODO: implement for real - the current implementation is to test related functionality
    player_name = session.get("player_name")
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    app.logger.debug(f"Finding active match of player {player.name}")
    match = get_active_match_of_player(player)
    publish_match_update(match)
    return Response(status=204) 

@app.route('/creature/moves/<id>', methods=['GET'])
def get_creature_moves(id):
    """Returns a list of possible moves for the creature"""
    # TODO: get creature from db by id instead of using mock
    player_name = session.get("player_name")
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    match = get_active_match_of_player(player)
    creature = next(c for c in match.player_1.creatures + match.player_2.creatures if c.nickname == id)
    positions = match.board.get_positions_in_range(creature.position, creature.speed)
    return jsonify([pos.to_simple_dict() for pos in positions])
    
@app.route('/match/submit', methods=['POST'])
def submit_commands():
    request_data = request.get_json()
    commands = command_from_dict(request_data["commands"])
    player_id = request_data["player_id"]
    match_id = request_data["match_id"]
    submit_command(player_id, commands, match_id)
    redis_connection.publish(TEST_MATCH_CHANNEL, f"player {player_id} commands submitted")
    return Response(status=204)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
