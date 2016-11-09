import random
import curses
import queue

from .minesweeper.minefield import MineField
from .minesweeper.contents import Contents

_DIRECTIONKEYS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT,
                  curses.KEY_RIGHT]


class InputMap(object):
    def __init__(self, args):
        if args.vimkeys:
            self.UP = ord('k')
            self.DOWN = ord('j')
            self.LEFT = ord('h')
            self.RIGHT = ord('l')
            self.PROBEKEY = ord(' ')
        else:
            self.UP = curses.KEY_UP
            self.DOWN = curses.KEY_DOWN
            self.LEFT = curses.KEY_LEFT
            self.RIGHT = curses.KEY_RIGHT
            self.PROBEKEY = ord('\n')
        self.FLAGKEY = ord('f')
        self.directionkeys = [self.UP, self.DOWN, self.LEFT, self.RIGHT]


def _move_select(direction, field, inputmap):
    """
    Function _move_select changes the 'selected' field of a MineField depending
    on the direction provided. 'direction' must be a curses.KEY_* instance,
    either UP, DOWN, LEFT, or RIGHT. If moving the selected cell would move to
    an out of bounds position, we do nothing.
    """
    startloc = field.selected
    delta = [0, 0]
    if direction == inputmap.UP:
        delta = [0, -1]
    elif direction == inputmap.DOWN:
        delta = [0, 1]
    elif direction == inputmap.RIGHT:
        delta = [1, 0]
    elif direction == inputmap.LEFT:
        delta = [-1, 0]

    # Filter out-of-bounds deltas
    x, y = startloc
    nx, ny = [x + delta[0], y + delta[1]]
    if nx < 0 or nx >= field.width:
        nx = x
    if ny < 0 or ny >= field.height:
        ny = y

    field.selected = [nx, ny]

def _create_foothold(field):
    """
    Function _create_foothold will remove mines from around the currently
    selected cell, ensuring that the current cell cannot have a mine, and that
    probing that cell will open up some amount of space.
    """
    x, y = field.selected
    cell = field.board[x][y]

    moved_count = 0

    safe_cells = [v for _, v in cell.neighbors.items() if v]
    safe_cells += [cell]

    for neighbor in safe_cells:
        if neighbor.contents == Contents.mine:
            neighbor.contents = Contents.empty
            moved_count += 1

    # Place a new mine for each of the mines we had to move out of the way
    while moved_count > 0:
        rx, ry = random.randint(0, field.width - 1), random.randint(
            0, field.height - 1)
        possible_mine = field.board[rx][ry]
        # Ensure any new location won't be in the desired foothold
        if not possible_mine in safe_cells:
            # Only place mines where there aren't existing mines
            if not possible_mine.contents == Contents.mine:
                possible_mine.contents = Contents.mine
                moved_count -= 1

def _first_probe(field):
    """
    Function _first_probe checks if this is the first probe of any cell in this
    minefield, returning True if it is the first probe, and False if it's not.
    """
    cells = [c for row in field.board for c in row]
    for cell in cells:
        if cell.probed:
            return False
    return True

def _probe_selected(field):
    """
    Function _probe_selected probes the currently selected cell. If the
    cell if flagged, ignore probe and return True immediately. If the
    probed cell contains a mine, return False, otherwise, returns True.
    """
    x, y = field.selected
    cell = field.board[x][y]
    if cell.flaged:
        return True
    # Create a foothold for the first probe
    if _first_probe(field):
        _create_foothold(field)
    cell.probe()

    if cell.contents == Contents.mine:
        return False
    return True


def _flag_selected(field):
    x, y = field.selected
    cell = field.board[x][y]
    cell.flaged = not cell.flaged


def check_win(mfield):
    correct_flags = 0
    for h in range(mfield.height):
        for w in range(mfield.width):
            c = mfield.board[w][h]
            if c.contents == Contents.mine and c.flaged:
                correct_flags += 1
    if correct_flags == mfield.mine_count:
        # win_game(mfield)
        return True
    return False


class Player(object):
    """
    Class Player contains the minefield that a particular player is playing
    against, as well as passthrough-methods to send input to a parent Bout.
    """

    def __init__(self, name, bout, args):
        self._args = args
        self.name = name
        self.bout = bout
        self.mfield = MineField(
            height=self._args.height,
            width=self._args.width,
            mine_count=args.mines)
        self.living = True
        self.victory = False

    def send_input(self, inpt):
        # Just pass the input to the parent bout, but with info saying that
        # this input comes from this player
        self.bout.send_input({'player': self.name, 'input': inpt})

    def get_state(self):
        return self.bout.get_state()

    def json(self):
        return {
            'name': self.name,
            'living': self.living,
            'minefield': self.mfield.json(),
            'victory': self.victory,
        }


class Bout(object):
    """
    Class Bout holds information on the state of the game (won/lost) as well as
    all the players playing currently.
    """

    def __init__(self, args):
        self.args = args
        self.inputmap = InputMap(args)
        self.stateq = queue.Queue()
        self.players = {"player1": Player("player1", self, self.args), }

        self.stateq.put(self.json())

    def send_input(self, inpt_event):
        player = self.players[inpt_event['player']]
        field = player.mfield
        inpt = inpt_event['input']

        if inpt in self.inputmap.directionkeys:
            _move_select(inpt, field, self.inputmap)

        if inpt == self.inputmap.PROBEKEY:
            if not _probe_selected(field):
                player.living = False

        if inpt == self.inputmap.FLAGKEY:
            _flag_selected(field)

        if check_win(field):
            player.victory = True

        self.stateq.put(self.json())

    def get_state(self, *args):
        return self.stateq.get()

    def json(self):
        jplayers = {k: v.json() for k, v in self.players.items()}
        return {"players": jplayers}
