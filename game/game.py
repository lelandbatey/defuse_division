import curses
import queue

from .minesweeper.minefield import MineField

_DIRECTIONKEYS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT,
                  curses.KEY_RIGHT]


def _move_select(direction, field):
    startloc = field.selected
    delta = [0, 0]
    if direction == curses.KEY_UP:
        delta = [0, -1]
    elif direction == curses.KEY_DOWN:
        delta = [0, 1]
    elif direction == curses.KEY_RIGHT:
        delta = [1, 0]
    elif direction == curses.KEY_LEFT:
        delta = [-1, 0]

    # Filter out-of-bounds deltas
    x, y = startloc
    nx, ny = [x + delta[0], y + delta[1]]
    if nx < 0 or nx >= field.width:
        nx = x
    if ny < 0 or ny >= field.height:
        ny = y

    field.selected = [nx, ny]


class Game(object):
    """
    Class Game holds information on the state of the game (won/lost) as well as
    all the players playing currently.
    """

    def __init__(self):
        self.mfield = MineField()
        self.stateq = queue.Queue()

    def send_input(self, inpt):
        # Do nothing with the input arguments, only send them along
        if inpt in _DIRECTIONKEYS:
            _move_select(inpt, self.mfield)
        self.stateq.put(self.mfield.json())

    def get_state(self, *args):
        return self.stateq.get()
