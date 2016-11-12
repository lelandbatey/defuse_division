#!/usr/bin/env python3

from pprint import pprint
import logging
import time

from game.server.server import Server
import game
# from game import game

# bout = game.Bout(max_players=1)
# client = bout.add_player()

# pprint(bout.json())

logformat='%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d:%(message)s'
logging.basicConfig(format=logformat, level=logging.DEBUG)

srv = Server('127.0.0.1', 44444)
bout = game.game.Bout(max_players=1, player_constructor=srv.create_player)

while True:
    bout.add_player()

# time.sleep(10)

