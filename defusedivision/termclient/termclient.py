"""
Module termclient implements a curses display for a game of minesweeper. It
waits on a variety of events, either a new game state or input from the user.
In the case of input from the user, an action for that input is sent to the
game. In the case of a new game state, the display on screen is re-drawn.

At this time, the design of termclient is based on a Golang-esque concurrent
actor model.
"""
from threading import Lock
import logging
import curses
import queue

import time
import sys

from . import curses_colors, display
from ..concurrency import concurrent
from .. import game
from ..game import Bout, Keys
from ..sound import sound
from ..client import client as netclient

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
        outqueue.put(out)


def color_attr():
    idx = [0]

    def next_color():
        possible = sorted(curses_colors.CURSES_COLORPAIRS.keys())
        key = possible[idx[0]]
        val = curses_colors.CURSES_COLORPAIRS[key]
        cp = curses.color_pair(val)
        idx[0] = (idx[0] + 1) % len(possible)
        return cp

    return next_color


def key_name(ch):
    vals_to_names = {v: k for k, v in curses.__dict__.items() if "KEY" in k}
    if ch in vals_to_names:
        return vals_to_names[ch]
    if ch < 127:
        return chr(ch)
    return "!NOTFOUND!"


def board_termsize(board_width, board_height):
    '''
    Function board_termsize returns the height and width of a grid of
    characters needed to display a board with the given input dimensions.
    '''
    cwidth = 3
    termwidth = ((cwidth + 1) * board_width) + 1
    termheight = (board_height * 2) + 1
    return termwidth, termheight


def draw_state(stdscr, state, me):
    """
    draw_state draws the state of a MineField onto a curses window.
    """
    startx, starty = 1, 1
    stdscr.erase()

    xoffset = 0
    players = state['players']
    for idx, pname in enumerate(sorted(players.keys())):
        player = players[pname]
        field = player['minefield']

        width, height = board_termsize(field['width'], field['height'])
        namey = starty + height
        middlefmt = "{{: ^{}}}"
        disp_name = middlefmt.format(width).format(pname)[:width]
        if pname == me:
            attr = curses_colors.get_colorpair('green-black')
        else:
            attr = curses.A_NORMAL

        for cell in field['cells']:
            glyphs = display.assemble_glyphs(cell, player)
            for g in glyphs:
                stdscr.addstr(g.y + starty, g.x + startx + xoffset, g.strng,
                              g.attr)
        # If a user has died, draw a big 'you're dead' message in the middle of
        # their board
        if not state['players'][pname]['living']:
            dead = middlefmt.format(width).format('WASTED')
            h = height // 2
            stdscr.addstr(h, startx+xoffset, dead, curses_colors.get_colorpair('yellow-red'))
        stdscr.addstr(namey, startx + xoffset, disp_name, attr)
        xoffset += width


def draw_end_msg(stdscr, msg):
    height, width = stdscr.getmaxyx()
    y = height - 2
    fmt = "{{:^{}}}".format(width)
    msg = fmt.format(msg)
    stdscr.addstr(y, 0, msg)


def draw_readymsg(stdscr, state):
    player = sorted(state['players'].keys())[0]
    field = state['players'][player]['minefield']
    _, yoffset = board_termsize(0, field['height'])
    ready = state['ready']
    # Ready message is yellow on red if not ready, blue on green if we are
    # ready
    attr = display.get_colorpair('yellow-red')
    if ready:
        attr = display.get_colorpair('blue-green')

    readymsg = "Good to go!" if ready else "Not ready yet : ("
    stdscr.move(yoffset + 1, 0)
    # stdscr.clrtobot()

    stdscr.addstr(yoffset + 2, 0, readymsg, attr)


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


def build_keymap(args):
    """
    Function build_keymap returns a dictionary from curses keys to game.Keys.
    """
    if args.vimkeys:
        return {
            ord('k'): Keys.UP,
            ord('j'): Keys.DOWN,
            ord('h'): Keys.LEFT,
            ord('l'): Keys.RIGHT,
            ord(' '): Keys.PROBE,
            ord('f'): Keys.FLAG,
        }
    return {
        curses.KEY_UP: Keys.UP,
        curses.KEY_DOWN: Keys.DOWN,
        curses.KEY_LEFT: Keys.LEFT,
        curses.KEY_RIGHT: Keys.RIGHT,
        ord('\n'): Keys.PROBE,
        ord('f'): Keys.FLAG,
    }


def extract_contents(stdscr):
    '''
    Function extract_contents returns the contents of a curses window, without
    attributes.
    '''
    contents = []
    height, width = stdscr.getmaxyx()
    for line in range(height):
        contents.append(stdscr.instr(line, 0))
    contents = [row.decode('utf-8').rstrip() for row in contents]
    return '\n'.join(contents)


def move_select(direction, field):
    """
    Function _move_select changes the 'selected' field of a MineField depending
    on the direction provided. 'direction' must be a curses.KEY_* instance,
    either UP, DOWN, LEFT, or RIGHT. If moving the selected cell would move to
    an out of bounds position, we do nothing.
    """
    startloc = field['selected']
    delta = [0, 0]
    if direction == game.Keys.UP:
        delta = [0, -1]
    elif direction == game.Keys.DOWN:
        delta = [0, 1]
    elif direction == game.Keys.RIGHT:
        delta = [1, 0]
    elif direction == game.Keys.LEFT:
        delta = [-1, 0]

    # Filter out-of-bounds deltas
    x, y = startloc
    nx, ny = [x + delta[0], y + delta[1]]
    if nx < 0 or nx >= field['width']:
        nx = x
    if ny < 0 or ny >= field['height']:
        ny = y

    field['selected'] = [nx, ny]


class FakeStdscr(object):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.par_height, self.par_width = stdscr.getmaxyx()
        self.pad = curses.newpad(self.par_height + 200, self.par_width + 200)
        self.pad.keypad(1)

    def refresh(self):
        # Reset the parent height on each refresh, to allow proper redrawing on
        # terminal resize
        self.par_height, self.par_width = self.stdscr.getmaxyx()
        self.pad.refresh(0, 0, 0, 0, self.par_height - 1, self.par_width - 1)

    def getmaxyx(self):
        return self.stdscr.getmaxyx()

    def __getattr__(self, attr):
        if hasattr(self.pad, attr):
            return getattr(self.pad, attr)
        else:
            raise AttributeError(attr)


def main(stdscr, client, args):
    if not curses.has_colors():
        curses.start_color()
    curses_colors.colors_init()
    curses.curs_set(0)

    actual_stdscr = stdscr
    stdscr = FakeStdscr(stdscr)

    keymap = build_keymap(args)

    eventq = queue.Queue()
    refresh_lock = Lock()

    def getinput():
        return stdscr.getch()

    input_reader(eventq, getinput)
    state_change_reader(eventq, client.get_state)

    state = {'players':{}}
    waitkeyframe = False
    while True:
        try:
            event = eventq.get()
        except KeyboardInterrupt:
            break
        if event[0] == "user-input":
            # Handle terminal resizing during game by redrawing the window
            if event[1] == curses.KEY_RESIZE:
                eventq.put(('new-state', state))
                continue
            # Don't send input once we've lost
            if not state['players'][client.name]['living']:
                continue
            # Map input onto game.Keys before sending it
            if event[1] in keymap.keys():
                k = keymap[event[1]]
                if waitkeyframe:
                    continue
                if k in game.DIRECTIONKEYS:
                    sound.SAMPLES.move_click.play()
                    move_select(k, state['players'][client.name]['minefield'])
                    eventq.put(('new-state', state))
                elif k in [game.Keys.PROBE, game.Keys.FLAG]:
                    sound.SAMPLES.probe.play()
                    waitkeyframe = True
                client.send_input(keymap[event[1]])

            else:
                client.send_input(event[1])

        elif event[0] == "new-state":
            waitkeyframe = False
            for oldplayer in state['players']:
                if oldplayer in event[1]['players']:
                    if state['players'][oldplayer]['living'] != event[1]['players'][oldplayer]['living']:
                        sound.SAMPLES.explosion.play()
                        if oldplayer == client.name:
                            sound.SAMPLES.you_lose.play()

            state = event[1]
            refresh_lock.acquire()
            draw_state(stdscr, state, client.name)
            # Print a 'you lose' message and exit
            if all_dead(state):
                draw_end_msg(stdscr, "Eliminated by mines, you lose!")
                stdscr.refresh()
                time.sleep(3)
                break
            # Print a 'Winner' message and exit
            victor = victorious(state)
            if victor:
                if victor == client.name:
                    sound.SAMPLES.you_win.play()
                else:
                    sound.SAMPLES.you_lose.play()
                draw_end_msg(stdscr, "{} wins!".format(victor))
                stdscr.refresh()
                time.sleep(3)
                break
            # Display the ready state of the bout
            # draw_readymsg(stdscr, state)
            stdscr.refresh()
            refresh_lock.release()
        elif event[0] == 'update-selected':
            pname, selected = event[1]
            player = state['players'][pname]
            player['minefield']['selected'] = selected
            eventq.put(('new-state', state))
    return extract_contents(stdscr)
