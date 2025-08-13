import logging
logging.basicConfig(level=logging.DEBUG)

import os
import json
import redis
from flask import Flask, Response, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from connection_util.postgres_util import create_and_seed_postgres
from classes.base import db
from classes.player import Player
from classes.command import Command
from game_logic.match_handler import (
    attempt_join_match,
    get_active_match_of_player,
    start_match,
    publish_match_state,
    get_player_commands,
    publish_command_update,
    submit_commands
)

app = Flask(__name__)

# TODO: deployment-ready config

# configure sqlalchemy
# docker adds "database" to the DNS
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://dev_user:dev_password@database:5432/dev_user"
db.init_app(app)
create_and_seed_postgres(app, db)

# configure redis
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
    logging.debug(f"starting listener for {channel}")
    redis_listener = redis_connection.pubsub()
    redis_listener.subscribe(channel)
    for message in redis_listener.listen():
        logging.debug(f"Broadcasting message on channel {channel}")
        # convert to str because data must be bytes
        yield f"data: {json.dumps(message['data'])}\n\n"

def channel_subscription_stream(channel_name):
    return Response(event_stream(channel_name), mimetype="text/event-stream")

@app.route('/')
def hello_world():
    return '<h1>Hello from Flask & Docker</h1>'

@app.route('/login', methods=['POST'])
def login():
    """Currently allows a user to login as one of the two test players"""
    # TODO: implement actual login
    request_data = request.get_json()
    player_name = request_data["player_name"]
    logging.debug(f"Logging in player {player_name}")
    player = Player.find_by_name(db, player_name)
    if player is None:
        return Response(status=404)
    else:
        session["player_name"] = player_name
        logging.debug(f"Logged in {player.name}")
        return jsonify(player.to_simple_dict())

@app.route('/match/join', methods=['GET'])
def join_match():
    """ get player, add them to a match, and return match data """
    player_name = session.get("player_name")
    if player_name is None:
        return Response(status=500)
    logging.debug(f"found player {player_name} from session")
    player = Player.find_by_name(db, player_name)

    # TODO: add a separate route for rejoining the current match
    current_match = get_active_match_of_player(db, player)
    if current_match is not None:
        logging.debug(f"{player.name} is already in a match")
        return channel_subscription_stream(current_match.get_redis_channel())
    else:
        match = attempt_join_match(db, player)
        if match is not None:
            if match.player_1 is not None and match.player_2 is not None and match and match.turn_number == 0:
                start_match(db, match)
            return channel_subscription_stream(match.get_redis_channel())
        else:
            return Response(status=500)
    
@app.route('/match/refresh', methods=['GET'])
def refresh_match():
    """Resend match data"""
    match = get_match_from_session()
    if match is None:
        return Response(status=500)
    publish_match_state(match)
    publish_command_update(match)
    return Response(status=204) 

@app.route('/creaturestates/<id>/moves', methods=['GET'])
def get_creature_moves(id):
    """Returns a list of possible moves for the creature"""
    match = get_match_from_session()
    creature_state = match.find_creature_state(id)
    positions = match.board.get_positions_in_range(creature_state.position, creature_state.creature.speed)
    return jsonify([pos.to_simple_dict() for pos in positions])

@app.route('/creaturestates/<id>/moves/route', methods=['GET'])
def get_move_route(id):
    x_pos = int(request.args.get("target_x"))
    y_pos = int(request.args.get("target_y"))
    logging.debug(f"searching for route of creature state {id} to {x_pos},{y_pos}")
    match = get_match_from_session()
    creature_state = match.find_creature_state(id)
    destination = match.board[x_pos][y_pos]
    positions = creature_state.get_planned_move_path(destination)
    return jsonify([pos.to_simple_dict() for pos in positions])
    
@app.route('/creaturestates/<creature_state_id>/actions/<action_id>/targets', methods=['GET'])
def get_action_targets(creature_state_id, action_id):
    """Returns a list of valid targets for the action"""
    logging.debug(f"searching for possible targets of action {action_id} from creature {creature_state_id}")
    match = get_match_from_session()
    creature_state = match.find_creature_state(creature_state_id)
    action = creature_state.creature.find_action_of_creature(action_id)
    positions = match.board.get_positions_in_range(creature_state.position, action.reach)
    return jsonify([pos.to_simple_dict() for pos in positions])

@app.route('/creaturestates/<creature_state_id>/actions/<action_id>/affected', methods=['GET'])
def get_action_affected(creature_state_id, action_id):
    """Returns a list of positions affected by the action"""
    match = get_match_from_session()
    creature_state = match.find_creature_state(creature_state_id)
    action = creature_state.creature.find_action_of_creature(action_id)
    target = match.board[int(request.args.get("target_x"))][int(request.args.get("target_y"))]
    logging.debug(f"Finding affected positions for {action.id} from {creature_state.position} to {target}")
    positions = action.get_affected_positions(creature_state.position, target)
    return jsonify([pos.to_simple_dict() for pos in positions])

@app.route('/match/submit', methods=['POST'])
def submit_match_commands():
    request_data = request.get_json()
    match = get_match_from_session()
    player = get_player_from_session()
    logging.debug(f"Received commands for {player.name} for match {match.id}")
    logging.debug(request_data["commands"])
    commands = [Command.from_dict_and_match(c, match) for c in request_data["commands"]]
    submit_commands(db, match.get_player_number(player), commands, match)
    return Response(status=204)

@app.route('/match/commands', methods=['GET'])
def get_stored_commands():
    player = get_player_from_session()
    match = get_match_from_session()
    logging.debug(f"Retreiving stored commands for player {player.name} in match {match.id}")
    player_number = match.get_player_number(player)
    return jsonify([command.to_simple_dict() for command in get_player_commands(match, player_number)])

def get_player_from_session():
    player_name = session.get("player_name")
    return Player.find_by_name(db, player_name)

def get_match_from_session():
    player = get_player_from_session()
    logging.debug(f"Finding active match of player {player.name}")
    return get_active_match_of_player(db, player)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
