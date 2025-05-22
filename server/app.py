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
    match = get_match_from_session()
    publish_match_update(match)
    return Response(status=204) 

@app.route('/creatures/<id>/moves', methods=['GET'])
def get_creature_moves(id):
    """Returns a list of possible moves for the creature"""
    # TODO: get creature from db by id instead of using mock
    match = get_match_from_session()
    creature = match.find_creature_in_match(id)
    positions = match.board.get_positions_in_range(creature.position, creature.speed)
    return jsonify([pos.to_simple_dict() for pos in positions])

@app.route('/creatures/<creature_id>/actions/<action_id>/targets', methods=['GET'])
def get_action_targets(creature_id, action_id):
    """Returns a list of valid targets for the action"""
    app.logger.debug(f"searching for possible targets of action {action_id} from creature {creature_id}")
    match = get_match_from_session()
    creature = match.find_creature_in_match(creature_id)
    action = creature.find_action_of_creature(action_id)
    positions = match.board.get_positions_in_range(creature.position, action.reach)
    return jsonify([pos.to_simple_dict() for pos in positions])
    # get pos in range using the action's range and creature's position

@app.route('/creatures/<creature_id>/actions/<action_id>/affected', methods=['GET'])
def get_action_affected(creature_id, action_id):
    """Returns a list of positions affected by the action"""
    match = get_match_from_session()
    creature = match.find_creature_in_match(creature_id)
    action = creature.find_action_of_creature(action_id)
    target = match.board[int(request.args.get("target_x"))][int(request.args.get("target_y"))]
    app.logger.debug(f"Finding affected positions for {action.id} from {creature.position} to {target}")
    positions = action.get_affected_positions(creature.position, target)
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

def get_match_from_session():
    # TODO: use database instead of test players
    player_name = session.get("player_name")
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    app.logger.debug(f"Finding active match of player {player.name}")
    return get_active_match_of_player(player)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
