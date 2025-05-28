
import json
import redis
import logging
from constants import TEST_MATCH_ID, NULL_STR, TEST_MATCH_CHANNEL
from classes.match import Match
from classes.board import Board
from connection_util.redis_util import match_from_json

logging.basicConfig(level=logging.DEBUG)

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def initialize_match(player_1, player_2, match_id=TEST_MATCH_ID):
    """Initialize a match and cache it in redis"""
    board = Board(10, 10)
    match = Match(board, player_1, player_2, turn_number=0)
    update_match_redis(match)
    clear_match_commands(match_id)
    return match

def start_match(match):
    """place creatures and inform players the match has started"""
    match.start_game()
    update_match_redis(match)
    redis_connection.publish(TEST_MATCH_CHANNEL, f"Match Start")
    publish_match_update(match)

def update_match_redis(match):
    logging.debug("Updating match in redis")
    # TODO: remove next line
    match.id = TEST_MATCH_ID
    redis_connection.set(str(match.id), json.dumps(match.to_simple_dict()))

def publish_match_update(match):
    update_match_redis(match)
    logging.debug(f"publishing match update on channel {TEST_MATCH_CHANNEL}")
    redis_connection.publish(TEST_MATCH_CHANNEL, redis_connection.get(match.id))

def clear_match_commands(match_id):
    """Clear player commands from redis cache"""
    redis_connection.set(f"{match_id}_1_commands", NULL_STR)
    redis_connection.set(f"{match_id}_2_commands", NULL_STR)

def attempt_join_match(player, match_id=TEST_MATCH_ID):
    """Add a player to an open match, or create an open match if one does not
    exist."""
    # TODO: implement for real - the current implementation is to test related functionality
    # try to get the player's active match
    logging.debug(f"Player {player.name} requesting to join match")
    match = get_active_match_of_player(player)
    if match is not None:
        logging.debug(f"{player.name} is already in a match")
        return match
    
    # join the test match
    match = get_active_match_by_id(match_id)
    if match is None:
        logging.debug("creating new match")
        return initialize_match(player, None)
    elif match.player_2 is None:
        logging.debug("joining existing match")
        match.player_2 = player
        update_match_redis(match)
        return match
    else: # match is already full
        logging.debug("match is already full")
        return None

def get_active_match_of_player(player):
    """Returns the active match of the player"""
    # TODO: implement for real - the current implementation is to test related functionality
    match = get_active_match_by_id(TEST_MATCH_ID)
    if match is None:
        return match
    elif match.is_player_in_match(player):
        return match
    else:
        return None

def get_active_match_by_id(match_id):
    """Finds and returns match with given ID in redis"""
    logging.debug(f"looking for match {match_id} in redis")
    match_json = redis_connection.get(match_id)
    return None if match_json is None else match_from_json(match_json)