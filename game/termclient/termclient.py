"""
Module termclient implements a curses display for a game of minesweeper. It
waits on a variety of events, either a new game state or input from the user.
In the case of input from the user, an action for that input is sent to the
game. In the case of a new game state, the display on screen is re-drawn.

At this time, the design of termclient is based on a Golang-esque concurrent
actor model.
"""
import curses
import queue

import time
import sys

from . import curses_colors, display
from ..minesweeper.minefield import MineField
from ..concurrency import concurrent
from ..game import Bout

DEBUG = False


@concurrent
def input_reader(outqueue, getch):
    """
    input_reader waits for user input from curses, then places whatever that
    input is into outqueue.
    """
    while True:
        out = getch()
        outqueue.put(("user-input", out))


@concurrent
def state_change_reader(outqueue, getstate):
    """
    state_change_reader calls getstate (a blocking function call) and when it
    returns, places it's output into outqueue.
    """
    while True:
        out = getstate()
        outqueue.put(('new-state', out))


def color_attr():
    idx = [0]

    def next_color():
        possible = sorted(curses_colors.CURSES_COLORPAIRS.keys())
        key = possible[idx[0]]
        # print(possible)
        val = curses_colors.CURSES_COLORPAIRS[key]
        cp = curses.color_pair(val)
        idx[0] = (idx[0] + 1) % len(possible)
        return cp

    return next_color


def key_name(ch):
    vals_to_names = {v: k for k, v in curses.__dict__.items() if "KEY" in k}
    # print(vals_to_names)
    if ch in vals_to_names:
        return vals_to_names[ch]
    if ch < 127:
        return chr(ch)
    return "!NOTFOUND!"


def draw_state(stdscr, state):
    """
    draw_state draws the state of a MineField onto a curses window.
    """
    startx, starty = 1, 1

    players = state['players']
    for pname in players:
        player = players[pname]
        field = player['minefield']
        for cell in field['cells']:
            glyphs = display.assemble_glyphs(cell, player)
            for g in glyphs:
                stdscr.addstr(g.y + starty, g.x + startx, g.strng, g.attr)


def draw_end_msg(stdscr, msg):
    height, width = stdscr.getmaxyx()
    y = height - 2
    fmt = "{{:^{}}}".format(width)
    msg = fmt.format(msg)
    stdscr.addstr(y, 0, msg)


def all_dead(state):
    """
    Function all_dead returns True if all players in the current bout have a
    'living' attribute of False.
    """
    players = state['players']
    for pname in players:
        player = players[pname]
        if player['living']:
            return False
    return True


def victorious(state):
    """
    Function victorious returns the name of the first player it finds which has
    'victory' of True. If no player has a victory, return None
    """
    players = state['players']
    for pname in players:
        player = players[pname]
        if player['victory']:
            return pname


def extract_contents(stdscr):
    contents = []
    height, _ = stdscr.getmaxyx()
    for line in range(height):
        contents.append(stdscr.instr(line, 0))
    contents = [row.decode('utf-8') for row in contents]
    return '\n'.join(contents)


def main(stdscr, args):
    if not curses.has_colors():
        curses.start_color()
    curses_colors.colors_init()
    curses.curs_set(0)

    # args = parse_cli_args()

    eventq = queue.Queue()

    bout = Bout(args)
    client = bout.players['player1']

    input_reader(eventq, stdscr.getch)
    state_change_reader(eventq, client.get_state)

    while True:
        try:
            event = eventq.get()
        except KeyboardInterrupt:
            break
        if event[0] == "user-input":
            # print(event[1], key_name(event[1]))
            client.send_input(event[1])

        elif event[0] == "new-state":
            state = event[1]
            draw_state(stdscr, state)
            stdscr.refresh()
            # Print a 'you lose' message and exit
            if all_dead(state):
                draw_end_msg(stdscr, "Eliminated by mines, you lose!")
                break
            # Print a 'Winner' message and exit
            victor = victorious(state)
            if victor:
                draw_end_msg(stdscr, "{} wins!".format(victor))
                break
    return extract_contents(stdscr)
