import os
import json
import redis
from flask import Flask, Response, request
from flask_session import Session
from constants import TEST_MATCH_CHANNEL
from classes.player import get_test_player_1, get_test_player_2
from game_logic.command_handler import command_from_dict, submit_command
from game_logic.match_handler import attempt_join_match, get_active_match_of_player, start_match, publish_match_update

app = Flask(__name__)

#configure redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')
app.secret_key = os.getenv('SECRET_KEY', default='DEV_SECRET_KEY')
server_session = Session(app)
redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def event_stream(channel):
    print(f"starting listener for {channel}")
    redis_listener = redis_connection.pubsub()
    redis_listener.subscribe(channel)
    for message in redis_listener.listen():
        # convert to str because data must be bytes
        yield json.dumps({
            "data": message["data"]
        }) 

@app.route('/')
def hello_world():
    return '<h1>Hello from Flask & Docker</h1>'

@app.route('/match/join', methods=['POST'])
def join_match():
    # TODO: implement for real - the current implementation is to test related functionality
    request_data = request.get_json()
    # get player, add them to the match, and return match data
    player_name = request_data["player_name"]
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    if attempt_join_match(player):
        return Response(event_stream(TEST_MATCH_CHANNEL), mimetype="text/event-stream")
    else:
        return Response(status=500)
    
@app.route('/match/join/confirm', methods=['POST'])
def confirm_join_match():
    """Send match data and start match after both players have connected"""
    # TODO: implement for real - the current implementation is to test related functionality
    # TODO: add validation
    request_data = request.get_json()
    player_name = request_data["player_name"]
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    match = get_active_match_of_player(player)
    publish_match_update(match)
    if match.player_1 is not None and match.player_2 is not None:
        start_match(match)
    return Response(status=204) 
    
@app.route('/match/submit', methods=['POST'])
def submit_commands():
    request_data = request.get_json()
    commands = command_from_dict(request_data["commands"])
    player_id = request_data["player_id"]
    match_id = request_data["match_id"]
    submit_command(player_id, commands, match_id)
    redis_connection.publish(TEST_MATCH_CHANNEL, f"player {player_id} commands submitted")
    return Response(status=204)

@app.route('/login', methods=['POST'])
def login():
    """Currently allows a user to login as one of the two test players"""
    # TODO: implement actual login
    request_data = request.get_json()
    player_name = request_data["username"]
    player = get_test_player_1() if player_name == "Safari" else get_test_player_2()
    player_json = json.dumps(player.to_simple_dict())
    return Response(player_json, mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
