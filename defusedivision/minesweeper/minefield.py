import random
import json

from .contents import Contents
from .cell import Cell


def json_dump(indata):
    """Creates prettified json representation of passed in object."""
    return json.dumps(indata, sort_keys=True, indent=4, \
     separators=(',', ': '))#, cls=date_handler)


def jp(indata):
    """Prints json representation of object"""
    print(json_dump(indata))


def cell_neighbors(mfield, x, y):
    """
    Function cell_neighbors returns all the neighboring cells for a cell at a
    given x, y coordinate. Returns a dictionary of strings representing compass
    directions to their neighbor cell.
    """
    deltas = {
        "N": (0, -1),
        "NE": (1, -1),
        "E": (1, 0),
        "SE": (1, 1),
        "S": (0, 1),
        "SW": (-1, 1),
        "W": (-1, 0),
        "NW": (-1, -1),
    }
    rv = dict()
    for k in deltas.keys():
        delt = deltas[k]
        nx, ny = map(lambda a, b: a + b, (x, y), delt)
        if nx in range(mfield.width) and ny in range(mfield.height):
            rv[k] = mfield.board[nx][ny]
        else:
            rv[k] = None
    return rv


class MineField(object):
    def __init__(self, width=12, height=12, mine_count=None):
        if width is None:
            self.width = 12
        else:
            self.width = width
        if height is None:
            self.height = 12
        else:
            self.height = height
        self.mine_count = mine_count
        self.board = [
            [Cell(w, h) for h in range(0, self.height)] for w in range(0, self.width)
        ]
        self._populate_mines()
        self._set_neighbors()

        self.selected = [0, 0]

    def _populate_mines(self):
        """
        Method _populate_mines populates the cells of this minefield with
        mines. Applies a random selection of simple constraints to where mines
        may be placed, though about half of the mines are purely randomly
        placed.
        """
        if self.mine_count is None:
            self.mine_count = int(0.15 * (self.height * self.width))
        count = self.mine_count
        selectionfuncs = [
            lambda y: not (y % 2),
            lambda y: bool(y % 2),
            lambda y: not (y % 3),
        ]
        yconstraint, xconstraint = random.sample(selectionfuncs * 2, 2)
        for x in range(count):
            while True:
                rx, ry = random.randint(0, self.width - 1), random.randint(
                    0, self.height - 1)

                if random.randint(0, 1):
                    if yconstraint(ry):
                        continue
                    if xconstraint(rx):
                        continue
                c = self.board[rx][ry]
                if c.contents == Contents.empty:
                    c.contents = Contents.mine
                    break

    def _set_neighbors(self):
        """
        Method _set_neighbors populates each Cells 'neighbors' field with a
        dictionary of neighboring cells. The keys to the dictionary are strings
        representing the compass direction where that Cell sits relative to the
        current cell. If there is not a Cell at the compass position, then that
        key has a value of None in the dictionary.
        """
        for h in range(self.height):
            for w in range(self.width):
                c = self.board[w][h]
                c.neighbors = cell_neighbors(self, w, h)

    def selected(self):
        raise NotImplementedError
        # return [self.board[w][h]
        #         for h in range(self.height) for w in range(self.width)
        #         if self.board[w][h].selected]

    def create_foothold(self):
        """
        generally called when the user makes first selection. Clear out any
        mines within 2 spaces of the existing selection and move them elsewhere
        onto the board. This prevents losing on the first probe and (usually)
        enables a corridor to open up on which the user may begin working
        """
        sel = self.selected()
        cell = sel[0]
        if cell.contents == Contents.mine:
            cell.contents = Contents.empty
        for adj in cell.get_adjacent():
            if adj.contents == Contents.mine:
                adj.contents = Contents.empty
        self.set_mine_contacts()

    def json(self):
        """
        Method json returns a json serializable object representing this
        minefield.
        """
        rv = {
            "selected": self.selected,
            "height": self.height,
            "width": self.width,
            "mine_count": self.mine_count,
            "cells": [cell.json() for row in self.board for cell in row],
        }
        return rv

    def __str__(self):
        return json_dump(self.json())
