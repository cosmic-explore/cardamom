
import logging
logging.basicConfig(level=logging.DEBUG)

import json
import redis
from sqlalchemy import select, and_, or_
from constants import MATCH_UPDATE, COMMAND_UPDATE, NULL_STR
from classes.match import Match
from classes.board import Board
from classes.creature import CreatureState
from connection_util.redis_util import game_notification, match_from_json, commands_from_json_and_match

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def initialize_match(db, player_1, player_2):
    """Initialize a match, store it in the db, and cache it in redis"""
    match = Match(player_1, player_2, turn_number=0)
    board = Board(10, 10, match=match)
    
    # store the match in postgres
    db.session.add_all([match, board])
    db.session.commit()
    logging.debug(f"Created match {match.id}")
    
    # store match data in redis for fast access
    update_match_redis(match)
    clear_match_commands(match) # inits the redis keys for the match commands
    for player in [player_1, player_2]:
        if player is not None:
            set_redis_player_active_match(player, match)
    
    return match

def start_match(db, match):
    """place creatures and inform players the match has started"""
    logging.debug(f"Match {match.id} is starting!")
    match.start_game()
    clear_match_commands(match)
    update_and_store_match(db, match)
    # redis_connection.publish(match.get_redis_channel(), game_notification(MATCH_START, None)) # currently unused by client
    publish_match_state(match)

def update_and_store_match(db, match):
    update_match_postgres(db, match)
    update_match_redis(match)

def update_match_redis(match):
    logging.debug(f"Updating match f{match.id} in redis")
    redis_connection.set(f"MATCH_{str(match.id)}", json.dumps(match.to_simple_dict()))

def update_match_postgres(db, match):
    logging.debug(f"Updating match f{match.id} in postgres")
    db.session.merge(match)
    db.session.commit()

def publish_match_state(match):
    match_redis_channel = match.get_redis_channel()
    logging.debug(f"publishing match update on channel {match_redis_channel}")
    redis_connection.publish(match_redis_channel, game_notification(MATCH_UPDATE, redis_connection.get(match_redis_channel)))

def attempt_join_match(db, player):
    """Add a player to an open match, or create an open match if one does not
    exist."""
    # search for an open match
    
    # TODO: search redis first

    #search postgres
    open_match = db.session.scalars(select(Match).where(
        and_(
            Match.player_2_id == None,
            Match.active == True
        )
    )).first()

    if open_match is not None:
        logging.debug(f"Found open match {open_match.id}")
        logging.debug(f"Adding player {player.name} to match {open_match.id}")
        open_match.player_2 = player
        return open_match
    else: # create a new match
        return initialize_match(db, player, None)

def get_active_match_of_player(db, player):
    """Searches Redis, then Postgres"""
    # search redis
    match_redis_key = redis_connection.get(player.get_redis_active_match_key())
    if match_redis_key is not None:
        logging.debug(f"Found match redis key {match_redis_key} for {player.name}")
        match_json = redis_connection.get(match_redis_key)
        match = match_from_json(match_json)
        if match is None:
            return match
        elif match.is_player_in_match(player):
            logging.debug(f"{player.name} is in match {match.id}")
            return match
        else:
            return None
    else:
        # search postgres
        logging.debug(f"Match for {player.name} not found in redis, searching postgres")
        match = db.session.scalars(
            select(Match).where(and_(
                or_(Match.player_1_id == player.id, Match.player_2_id == player.id),
                Match.active == True))
        ).one_or_none()
        if match is None:
            return match
        elif match.is_player_in_match(player):
            logging.debug(f"Found match {match.id} for {player.name} in postgres")
            # re-store the match in redis
            update_match_redis(match)
            clear_match_commands(match)
            redis_connection.set(player.get_redis_active_match_key(), match.get_redis_channel())
            return match
        else:
            return None
        
def set_redis_player_active_match(player, match):
    redis_connection.set(player.get_redis_active_match_key(), match.get_redis_channel())

def get_active_match_by_id(match_id):
    """Finds and returns match with given ID in redis"""
    logging.debug(f"looking for match {match_id} in redis")
    match_json = redis_connection.get(match_id)
    return None if match_json is None else match_from_json(match_json)


### COMMAND SUBMISSION


def clear_match_commands(match, player_number=None):
    """Clear player commands from redis cache by setting their value to the NULL_STR constant"""
    logging.debug(f"Clearing stored commands for match {match.id}")
    if player_number is not None:
        set_player_commands(match, player_number, NULL_STR)
    else:
        # clear all commands
        set_player_commands(match, 1, NULL_STR)
        set_player_commands(match, 2, NULL_STR)

def get_player_commands(match, player_number):
    redis_json = redis_connection.get(get_match_player_command_key(match, player_number))
    if redis_json == NULL_STR:
        return []
    elif redis_json == None:
        # redis may have dropped the command key
        clear_match_commands(match, player_number=player_number)
        return []
    else:
        return commands_from_json_and_match(redis_json, match)

def set_player_commands(match, player_number, commands):
    redis_connection.set(f"{get_match_player_command_key(match, player_number)}", commands)

def get_match_command_state(match):
    """Returns the command submission state for the requested match"""
    state = {
        key: value != [] for key, value in get_match_commands(match).items()
    }
    return state

def get_match_commands(match):
    return {
        "player_1": get_player_commands(match, 1),
        "player_2": get_player_commands(match, 2)
    }

def submit_commands(db, player_number, commands, match):
    """Cache an array of commands in redis. If all other players have submitted
    commands, adjudicate the next turn"""
    logging.debug(f"Submitting the following commands for player {player_number} in match {match.id}:")
    logging.debug([c.to_simple_dict() for c in commands])
    set_player_commands(match, player_number, json.dumps([command.to_simple_dict() for command in commands]))
    match_command_state = get_match_command_state(match)
    logging.debug(f"New command state for match {match.id}:")
    logging.debug(match_command_state)
    if all([command_state == True for command_state in match_command_state.values()]):
        adjudicate_commands(db, match)
    else:
        publish_command_update(match)

def adjudicate_commands(db, match):
    """Execute the commands, cache the new Match state in redis, reset the
    command cache for the match, and alert players that a new turn has begun"""
    logging.debug(f"Adjudicating turn {match.turn_number} for match {match.id}")

    # retrieve the match and command creature states from postgres so that saving works properly
    db_match = db.session.scalars(select(Match).where(Match.id == match.id)).one()
    
    db_match.play_turn(get_match_commands(db_match))
    update_and_store_match(db, db_match)
    clear_match_commands(db_match)

    publish_match_state(db_match)
    publish_command_update(db_match)

def get_match_player_command_key(match, player_number):
    return f"{str(match.id)}_{player_number}_commands"

def publish_command_update(match):
    # TODO: use the channel of the player's match
    logging.debug(f"publishing match command status on channel {match.get_redis_channel()}")
    redis_connection.publish(match.get_redis_channel(), game_notification(COMMAND_UPDATE, get_match_command_state(match)))
