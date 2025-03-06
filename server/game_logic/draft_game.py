"""This script is an entry-point for testing the game logic."""

import sys
import json
import redis
sys.path.append(".")
from uuid import uuid4
from classes.player import get_test_player_1, get_test_player_2
from classes.match import Match
from classes.board import Board
from classes.command import Command
from connection_util.redis_util import match_from_json, commands_from_json

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
MATCH_ID = "test_match"
NULL_STR = "DEV_NULL_STR" # Null values cannot be stored in Redis
TURN_CHANNEL = "new turn"

def initialize_game(player_1, player_2):
    """Initialize a match and cache it in redis"""
    board = Board(10, 10)
    match = Match(board, player_1, player_2)
    match.init_creature_positions()
    redis_connection.set(MATCH_ID, json.dumps(match.to_simple_dict()))
    # clear cache for player commands
    redis_connection.set(f"{MATCH_ID}_1_commands", NULL_STR)
    redis_connection.set(f"{MATCH_ID}_2_commands", NULL_STR)

def submit_command(player_number, command):
    """Cache an array of commands in redis. If all other players have submitted
    commands, adjucate the next turn."""
    redis_connection.set(f"{MATCH_ID}_{player_number}_commands", json.dumps(command.to_simple_dict()))
    submitted_commands = [
        redis_connection.get(f"{MATCH_ID}_1_commands"),
        redis_connection.get(f"{MATCH_ID}_2_commands")
    ]
    if all([command != NULL_STR for command in submitted_commands]):
        adjudicate_commands()
    
def adjudicate_commands():
    """Execute the commands, cache the new Match state in redis, reset the
    command cache for the match, and alert players that a new turn has begun"""
    print("Adjudicating!")
    match = match_from_json(redis_connection.get(MATCH_ID))
    player_1_commands = commands_from_json(redis_connection.get(f"{MATCH_ID}_1_commands"), match)
    player_2_commands = commands_from_json(redis_connection.get(f"{MATCH_ID}_2_commands"), match)
    
    match.play_turn([player_1_commands, player_2_commands])
    redis_connection.set(MATCH_ID, json.dumps(match.to_simple_dict()))    
    redis_connection.set(f"{MATCH_ID}_1_commands", NULL_STR)
    redis_connection.set(f"{MATCH_ID}_2_commands", NULL_STR)

    redis_connection.publish(TURN_CHANNEL, redis_connection.get(MATCH_ID))

player_1 = get_test_player_1()
player_2 = get_test_player_2()
creature_1 = player_1.creatures[0]
creature_2 = player_2.creatures[0]

turn_listener = redis_connection.pubsub()
turn_listener.subscribe(TURN_CHANNEL)
initialize_game(player_1, player_2)

match_json = redis_connection.get(MATCH_ID)
match = match_from_json(match_json)

submit_command(1, Command(creature_1, match.board[0][9], creature_1.actions[0], creature_2.position))
submit_command(2, Command(creature_2, match.board[0][0], creature_2.actions[0], creature_1.position))

for message in turn_listener.listen():
    print(message)

# set creature positions manually
# creature_1.set_position(board[5][5])
# creature_2.set_position(board[6][5])