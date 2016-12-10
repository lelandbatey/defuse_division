from .contents import Contents


class Cell(object):
    """
    Class Cell represents a single cell on a field of cells in a game of
    minesweeper.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.contents = Contents.empty
        self.probed = False
        self.flagged = False
        self.neighbors = dict()

    def mine_contacts(self):
        """
        Method mine_contacts returns the number of mines in the neighboring
        cells.
        """
        if not len(self.neighbors):
            raise ValueError("{} has unset number of neighbors.".format(
                repr(self)))
        rv = 0
        for _, v in self.neighbors.items():
            if v and v.contents == Contents.mine:
                rv += 1
        return rv

    def probe(self):
        """
        Method probe marks this cells 'probe' field as true. Additionally, if
        this Cells mine_contacts is 0, then this probe will also recursively
        probe all neighbor cells.
        """
        self.probed = True
        if not self.mine_contacts():
            for _, cell in self.neighbors.items():
                if cell and not cell.probed:
                    cell.probe()

    def json(self):
        """
        Method json returns a json-serializable representation of this Cell
        object.
        """
        rv = {
            "x": self.x,
            "y": self.y,
            "contents": self.contents,
            "probed": self.probed,
            "flagged": self.flagged,
            "neighbors": {
                k: v.contents == Contents.mine if v else None
                for k, v in self.neighbors.items()
            },
        }
        return rv
        raise NotImplementedError

    def __repr__(self):
        return "Cell({}, {})".format(self.x, self.y)
