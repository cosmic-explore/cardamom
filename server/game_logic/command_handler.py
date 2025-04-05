import json
import redis
from constants import NULL_STR
from classes.command import Command
from connection_util.redis_util import match_from_json, commands_from_json
from game_logic.match_handler import publish_match_update

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def command_from_dict(command_dict):
    creature = None
    move_target = None
    action = None
    action_target = None
    return Command(creature, move_target, action, action_target)

def submit_command(player_number, command, match_id):
    """Cache an array of commands in redis. If all other players have submitted
    commands, adjucate the next turn."""
    redis_connection.set(f"{match_id}_{player_number}_commands", json.dumps(command.to_simple_dict()))
    submitted_commands = [
        redis_connection.get(f"{match_id}_1_commands"),
        redis_connection.get(f"{match_id}_2_commands")
    ]
    if all([command != NULL_STR for command in submitted_commands]):
        adjudicate_commands(match_id)

def adjudicate_commands(match_id):
    """Execute the commands, cache the new Match state in redis, reset the
    command cache for the match, and alert players that a new turn has begun"""
    print("Adjudicating!")
    match = match_from_json(redis_connection.get(match_id))
    player_1_commands = commands_from_json(redis_connection.get(f"{match_id}_1_commands"), match)
    player_2_commands = commands_from_json(redis_connection.get(f"{match_id}_2_commands"), match)
    
    match.play_turn([player_1_commands, player_2_commands])
    redis_connection.set(match_id, json.dumps(match.to_simple_dict()))    
    redis_connection.set(f"{match_id}_1_commands", NULL_STR)
    redis_connection.set(f"{match_id}_2_commands", NULL_STR)

    publish_match_update(match_id)