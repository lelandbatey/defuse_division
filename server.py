#!/usr/bin/env python3

from pprint import pprint
import logging
import time

from game.server.server import Server
import game

logformat='%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d:%(message)s'
logging.basicConfig(format=logformat, level=logging.INFO)

srv = Server('127.0.0.1', 44444)
bout = game.game.Bout(max_players=2, player_constructor=srv.create_player)

while True:
    bout.add_player()
    if len(bout.players) >= bout.max_players:
        time.sleep(0.3)


