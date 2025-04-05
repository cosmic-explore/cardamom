"""This script is an entry-point for testing the game logic."""

import sys
import json
import redis
sys.path.append(".")
from threading import Thread
from time import sleep
from constants import TEST_MATCH_CHANNEL, TEST_MATCH_ID
from classes.player import get_test_player_1, get_test_player_2
from classes.command import Command
from command_handler import submit_command
from match_handler import attempt_join_match, get_active_match_by_id, publish_match_update

redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Begin draft game setup

player_1 = get_test_player_1()
player_2 = get_test_player_2()
creature_1 = player_1.creatures[0]
creature_2 = player_2.creatures[0]

match_listener = redis_connection.pubsub()
match_listener.subscribe(TEST_MATCH_CHANNEL)

attempt_join_match(player_1, TEST_MATCH_ID)
attempt_join_match(player_2, TEST_MATCH_ID)
match = get_active_match_by_id(TEST_MATCH_ID)

print(match.to_simple_dict())

# publish_match_update(match)

# # submit_command(1, Command(creature_1, match.board[0][9], creature_1.actions[0], creature_2.position), TEST_MATCH_ID)
# # submit_command(2, Command(creature_2, match.board[0][0], creature_2.actions[0], creature_1.position), TEST_MATCH_ID)

# def do_later():
#     def do_work():
#         sleep(2)
#         publish_match_update(match)

#     thread = Thread(target=do_work)
#     thread.start()

# def generator():
#     for message in match_listener.listen():
#         yield message

# do_later()

# for message in generator():
#     print(message)



# set creature positions manually
# creature_1.set_position(board[5][5])
# creature_2.set_position(board[6][5])