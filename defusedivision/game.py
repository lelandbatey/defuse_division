import logging
import random
import curses
import queue

from .minesweeper.minefield import MineField
from .minesweeper.contents import Contents


class Conveyor(object):
    """
    Abstract class Conveyor describes the basic contract for communicating about games of Minesweeper.
    """

    def get_state(self):
        raise NotImplementedError

    def send_input(self, inpt):
        raise NotImplementedError


class Keys:
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    PROBE = 'PROBE'
    FLAG = 'FLAG'


DIRECTIONKEYS = [Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT]


def _move_select(direction, field):
    """
    Function _move_select changes the 'selected' field of a MineField depending
    on the direction provided. 'direction' must be a curses.KEY_* instance,
    either UP, DOWN, LEFT, or RIGHT. If moving the selected cell would move to
    an out of bounds position, we do nothing.
    """
    startloc = field.selected
    delta = [0, 0]
    if direction == Keys.UP:
        delta = [0, -1]
    elif direction == Keys.DOWN:
        delta = [0, 1]
    elif direction == Keys.RIGHT:
        delta = [1, 0]
    elif direction == Keys.LEFT:
        delta = [-1, 0]

    # Filter out-of-bounds deltas
    x, y = startloc
    nx, ny = [x + delta[0], y + delta[1]]
    if nx < 0 or nx >= field.width:
        nx = x
    if ny < 0 or ny >= field.height:
        ny = y

    field.selected = [nx, ny]


def create_foothold(field):
    """
    Function create_foothold will remove mines from around the currently
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
    if cell.flagged:
        return True
    # Create a foothold for the first probe
    if _first_probe(field):
        create_foothold(field)
    cell.probe()

    if cell.contents == Contents.mine:
        return False
    return True


def _flag_selected(field):
    x, y = field.selected
    cell = field.board[x][y]
    cell.flagged = not cell.flagged


def check_win(mfield):
    flags = 0
    correct_flags = 0
    for h in range(mfield.height):
        for w in range(mfield.width):
            c = mfield.board[w][h]
            if c.contents == Contents.mine and c.flagged:
                correct_flags += 1
            if c.flagged:
                flags += 1
    if correct_flags == mfield.mine_count and flags == correct_flags:
        return True
    return False


class Player(Conveyor):
    """
    Class Player contains the minefield that a particular player is playing
    against, as well as passthrough-methods to send input to a parent Bout.
    """

    def __init__(self, name, bout, mine_count=None, height=None, width=None):
        # self._args = args
        self.name = name
        self.bout = bout
        self.stateq = queue.Queue()
        self.mfield = MineField(
            height=height, width=width, mine_count=mine_count)
        self.living = True
        self.victory = False

    def send_input(self, inpt):
        # Just pass the input to the parent bout, but with info saying that
        # this input comes from this player
        self.bout.send_input({'player': self.name, 'input': inpt})

    def get_state(self):
        return self.stateq.get()

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

    `player_constructor` is a callable which accepts the same arguments as
    class `Player`, and returns a `Player`-like object. Allows a Bout to use a
    Player which gets it's input from anywhere.
    """

    def __init__(self,
                 max_players=2,
                 minefield_size=(12, 12),
                 mine_count=None,
                 player_constructor=None):
        self.max_players = max_players
        self.minefield_size = minefield_size
        self.mine_count = mine_count
        self.players = dict()
        self.ready = False
        if player_constructor is None:
            player_constructor = Player
        self.player_constructor = player_constructor

    def send_input(self, inpt_event):
        '''
        Method send_input is the final stop for an inpt_event, as those events
        are used here by the Bout to modify the state of the game.
        '''
        player = self.players[inpt_event['player']]
        field = player.mfield
        inpt = inpt_event['input']

        if isinstance(inpt, dict):
            # Change the name of a player
            if 'change-name' in inpt:
                newname = inpt['change-name']
                while newname in self.players:
                    newname = newname + str(random.randint(0, 100))
                oldname = player.name
                logging.info('Changing player name from: "{}" to "{}"'.format(
                    oldname, newname))
                player.name = newname
                self.players[newname] = player
                del self.players[oldname]
            if 'new-minefield' in inpt:
                info = inpt['new-minefield']
                height = info['height']
                width = info['width']
                mine_count = info['mine_count']
                new_mfield = MineField(
                    height=height, width=width, mine_count=mine_count)
                player.mfield = new_mfield

        if inpt in DIRECTIONKEYS:
            _move_select(inpt, field)
            self._push_selected(player.name, field.selected)
            return

        if inpt == Keys.PROBE:
            if not _probe_selected(field):
                player.living = False

        if inpt == Keys.FLAG:
            _flag_selected(field)

        if check_win(field):
            player.victory = True

        self._push_state()

    def _push_state(self):
        '''
        Method _push_state put's the state of this bout into every Player's
        stateq.
        '''
        for _, v in self.players.items():
            v.stateq.put(('new-state', self.json()))

    def _push_selected(self, playername, selected):
        '''
        Method _push_selected pushes a state to all Players updating one
        players selected position.
        '''
        for _, v in self.players.items():
            v.stateq.put(('update-selected', (playername, selected)))

    def add_player(self):
        '''
        Method add_player creates a new player object for this Bout, and
        returns a reference to that player. If there are already
        self.max_players players set to play in this bout, then returns None.
        '''
        if self.max_players <= len(self.players):
            return None
        pname = "Player{}-{}".format(
            len(self.players) + 1, random.randint(0, 10000))
        width, height = self.minefield_size
        player = self.player_constructor(
            pname,
            self,
            mine_count=self.mine_count,
            height=height,
            width=width)
        self.players[pname] = player
        logging.info('Adding player: "{}" {}'.format(pname, player))
        if len(self.players) >= self.max_players:
            self.ready = True
        self._push_state()
        return player

    def remove_player(self, playername):
        '''
        Method remove_player removes a player with the given name from this
        Bout's collection of players. If no player exists with the given name,
        does nothing.
        '''
        logging.info('Removing player: "{}"'.format(playername))
        if playername in self.players:
            del self.players[playername]
        if len(self.players) < self.max_players:
            self.ready = False
        self._push_state()

    def json(self):
        jplayers = {k: v.json() for k, v in self.players.items()}
        return {"players": jplayers, 'ready': self.ready}
