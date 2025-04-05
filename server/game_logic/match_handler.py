
import json
import redis
from constants import TEST_MATCH_ID, NULL_STR, TEST_MATCH_CHANNEL
from classes.match import Match
from classes.board import Board
from connection_util.redis_util import match_from_json

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def initialize_match(player_1, player_2, match_id=TEST_MATCH_ID):
    """Initialize a match and cache it in redis"""
    board = Board(10, 10)
    match = Match(board, player_1, player_2)
    update_match_redis(match)
    clear_match_commands(match_id)

def start_match(match):
    """place creatures and inform players the match has started"""
    match.init_creature_positions()
    redis_connection.publish(TEST_MATCH_CHANNEL, f"Match Start")
    publish_match_update(match)

def update_match_redis(match):
    # TODO: remove next line
    match.id = TEST_MATCH_ID
    print(match.to_simple_dict())
    redis_connection.set(str(match.id), json.dumps(match.to_simple_dict()))

def publish_match_update(match):
    update_match_redis(match)
    redis_connection.publish(TEST_MATCH_CHANNEL, redis_connection.get(match.id))

def clear_match_commands(match_id):
    """Clear player commands from redis cache"""
    redis_connection.set(f"{match_id}_1_commands", NULL_STR)
    redis_connection.set(f"{match_id}_2_commands", NULL_STR)

def attempt_join_match(player, match_id=TEST_MATCH_ID):
    """Add a player to an open match, or create an open match if one does not
    exist."""
    # TODO: implement for real - the current implementation is to test related functionality
    match = get_active_match_by_id(match_id)
    if match is None:
        print("match was none")
        initialize_match(player, None)
        return True
    elif match.player_2 is None:
        print("update player 2")
        match.player_2 = player
        update_match_redis(match)
        return True
    else: # match is already full
        return False

def get_active_match_of_player(player):
    """Returns the active match of the player"""
    # TODO: implement for real - the current implementation is to test related functionality
    return get_active_match_by_id(TEST_MATCH_ID)
    

def get_active_match_by_id(match_id):
    """Finds and returns match with given ID in redis"""
    print(f"looking for match {match_id} in redis")
    match_json = redis_connection.get(match_id)
    return None if match_json is None else match_from_json(match_json)