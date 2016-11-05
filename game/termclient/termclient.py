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

from . import curses_colors
from ..minesweeper.minefield import MineField
from ..concurrency import concurrent

@concurrent
def input_reader(outqueue, getch):
    """
    input_reader waits for user input from curses, then places whatever that
    input is into outqueue.
    """
    while True:
        out = getch()
        outqueue.put(("user-input", out))
        # print("put it in")

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

def main(stdscr):
    if not curses.has_colors():
        curses.start_color()
    curses_colors.colors_init()

    eventq = queue.Queue()
    stateq = queue.Queue()

    input_reader(eventq, stdscr.getch)
    state_change_reader(eventq, stateq.get)

    next_color = color_attr()

    l = 0

    while True:
        event = eventq.get()
        if event[0] == "user-input":
            color = next_color()
            s = key_name(event[1])
            stdscr.addstr(0, l, s, color)
            l += len(s)
            stdscr.refresh()
            # curses.
            # display_str = event[1].
            # stdscr.
