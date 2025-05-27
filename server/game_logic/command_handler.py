import sys
import json
import redis
import logging
from constants import NULL_STR
from classes.command import Command
from connection_util.redis_util import match_from_json, commands_from_json
from game_logic.match_handler import publish_match_update, update_match_redis

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)    

def submit_commands(player_number, commands, match):
    """Cache an array of commands in redis. If all other players have submitted
    commands, adjucate the next turn."""
    logging.debug(f"Submitting the following commands for player {player_number} in match {match.id}:")
    logging.debug([c.to_simple_dict() for c in commands])
    redis_connection.set(f"{match.id}_{player_number}_commands", json.dumps([command.to_simple_dict() for command in commands]))
    submitted_commands = {
        "player_1": redis_connection.get(f"{match.id}_1_commands"),
        "player_2": redis_connection.get(f"{match.id}_2_commands")
    }
    logging.debug(f"New command state for match {match.id}:")
    logging.debug(submitted_commands)
    if all([command != NULL_STR for command in [
        submitted_commands["player_1"],
        submitted_commands["player_2"]]
    ]):
        adjudicate_commands(match)

def adjudicate_commands(match):
    """Execute the commands, cache the new Match state in redis, reset the
    command cache for the match, and alert players that a new turn has begun"""
    print("Adjudicating!")
    player_1_commands = commands_from_json(redis_connection.get(f"{match.id}_1_commands"), match)
    player_2_commands = commands_from_json(redis_connection.get(f"{match.id}_2_commands"), match)

    match.play_turn({"player_1": player_1_commands, "player_2": player_2_commands})
    logging.debug("New match state after turn:")
    match.display_game()
    logging.debug(match.to_simple_dict())
    redis_connection.set(f"{match.id}_1_commands", NULL_STR)
    redis_connection.set(f"{match.id}_2_commands", NULL_STR)
    publish_match_update(match)