
import unittest
import time

from .cell import Cell
from .contents import Contents
from .minefield import cell_neighbors

def make_neighbors(mine_count):
    cells = {
        "N": Cell(0, -1),
        "NE": Cell(1, -1),
        "E": Cell(1, 0),
        "SE": Cell(1, 1),
        "S": Cell(0, 1),
        "SW": Cell(-1, 1),
        "W": Cell(-1, 0),
        "NW": Cell(-1, -1),
    }
    for x in range(mine_count):
        keys = sorted(cells.keys())
        cells[keys[x]].contents = Contents.mine
    return cells

def build_test_field(height=3, width=3):
    grid = [
        [Cell(w, h) for h in range(0, height)] for w in range(0, width)
    ]

    class TstField(object):
        def __init__(self, height, width, grid):
            self.board = grid
            self.height, self.width = height, width

    field = TstField(height, width, grid)
    for h in range(height):
        for w in range(width):
            field.board[w][h].neighbors = cell_neighbors(field, w, h)
    return field

class TestCell(unittest.TestCase):
    def test_neighbors(self):
        c = Cell(1, 1)
        for x in range(0, 9):
            c.neighbors = make_neighbors(x)
            self.assertEqual(c.mine_contacts(), x)
    def test_probe(self):
        """
        Test that probing a cell that's not touching a mine recursively probes
        all cells around it.
        """
        field = build_test_field(3, 3)

        field.board[0][0].contents = Contents.mine
        field.board[2][2].probe()
        probes = [c.probed for row in field.board for c in row]
        self.assertEqual(probes, [False]+[True]*8)

    def test_probe_large(self):
        """
        Test that a cell in a large minefield will recursively probe only those
        cells adjacent to a cell with no mines around it.
        """
        field = build_test_field(5, 5)
        untouched = [(0, 0), (0, 1), (1, 1), (1, 0),]
        for x, y in untouched[::2]:
            field.board[x][y].contents = Contents.mine
        field.board[4][4].probe()
        probes = [cell.probed for row in field.board for cell in row]
        # All but the four hopefully unprobed cells should be probed
        self.assertEqual(sum(probes), len(probes)-4)
        # Check that all the hopefully unprobed cells are in fact unprobed
        self.assertEqual([field.board[x][y].probed for x, y in untouched], [False]*4)

