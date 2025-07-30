import sys
import json
import redis
import logging
from constants import COMMAND_UPDATE, NULL_STR, TEST_MATCH_CHANNEL
from connection_util.redis_util import commands_from_json_and_match, game_notification
from game_logic.match_handler import publish_match_update

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)    

def submit_commands(player_number, commands, match):
    """Cache an array of commands in redis. If all other players have submitted
    commands, adjudicate the next turn"""
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
    else:
        publish_command_update(match)

def adjudicate_commands(match):
    """Execute the commands, cache the new Match state in redis, reset the
    command cache for the match, and alert players that a new turn has begun"""
    print("Adjudicating!")
    match.play_turn({"player_1": get_player_commands(match, 1), "player_2": get_player_commands(match, 2)})
    logging.debug("New match state after turn:")
    match.display_game()
    logging.debug(match.to_simple_dict())
    redis_connection.set(f"{match.id}_1_commands", NULL_STR)
    redis_connection.set(f"{match.id}_2_commands", NULL_STR)
    publish_match_update(match)
    publish_command_update(match)

def get_player_commands(match, player_number):
    redis_str = redis_connection.get(f"{match.id}_{player_number}_commands")
    if redis_str == NULL_STR:
        return []
    else:
        return commands_from_json_and_match(redis_str, match)

def get_command_state(match):
    """Returns the command submission state for the requested match"""
    return {
        "player_1": redis_connection.get(f"{match.id}_1_commands") != NULL_STR,
        "player_2": redis_connection.get(f"{match.id}_2_commands") != NULL_STR
    }

def publish_command_update(match):
    # TODO: use the channel of the player's match
    logging.debug(f"publishing match command status on channel {TEST_MATCH_CHANNEL}")
    redis_connection.publish(TEST_MATCH_CHANNEL, game_notification(COMMAND_UPDATE, get_command_state(match)))