"""
Module display concerns itself with the displaying of the game board.
"""

from ..minesweeper.contents import Contents

def left_edge(cell, field):
    return cell['x'] == 0

def right_edge(cell, field):
    return cell['x'] == field['width'] - 1

def top_edge(cell, field):
    return cell['y'] == 0

def bottom_edge(cell, field):
    return cell['y'] == field['height'] - 1

class Glyph(object):
    """
    Class Glyph contains data for a single symbol or unit which shall be drawn
    to a curses window.
    """
    def __init__(self, x, y, strng):
        self.x = x
        self.y = y
        self.strng = strng
    def __str__(self):
        return self.strng
    def __repr__(self):
        return str(self.__dict__)

def _upleft(cx, cy, cell, field):
    x, y = cx-1, cy-1
    if top_edge(cell, field):
        if left_edge(cell, field):
            return Glyph(x, y, "┌")
        else:
            return Glyph(x, y, "┬")
    else:
        if left_edge(cell, field):
            return Glyph(x, y, "├")
        else:
            return Glyph(x, y, "┼")

def _downleft(cx, cy, cell, field):
    x, y, = cx-1, cy+1
    if bottom_edge(cell, field):
        if left_edge(cell, field):
            return Glyph(x, y, "└")
        else:
            return Glyph(x, y, "┴")
    else:
        if left_edge(cell, field):
            return Glyph(x, y, "├")
        else:
            return Glyph(x, y, "┼")

def _upright(cx, cy, cell, field):
    x, y = cx+len(cell['contents']), cy-1
    if top_edge(cell, field):
        if right_edge(cell, field):
            return Glyph(x, y, "┐")
        else:
            return Glyph(x, y, "┬")
    else:
        if right_edge(cell, field):
            return Glyph(x, y, "┤")
        else:
            return Glyph(x, y, "┼")
def _downright(cx, cy, cell, field):
    x, y = cx+len(cell['contents']), cy+1
    if bottom_edge(cell, field):
        if right_edge(cell, field):
            return Glyph(x, y, "┘")
        else:
            return Glyph(x, y, "┴")
    else:
        if right_edge(cell, field):
            return Glyph(x, y, "┤")
        else:
            return Glyph(x, y, "┼")

def assemble_glyphs(cell, field):
    cwidth = len(cell['contents'])
    # Starting cell position is:
    #     ((length_in_dimension+1)*n) + 1
    # ypos = lambda y: (2*y)+1
    # xpos = lambda x: ((1+cwidth)*x)+1

    # The x position on the curses field where the glyph will be drawn
    x = ((1+cwidth) * cell['x']) + 1
    y = (2 * cell['y']) + 1

    contents_glyph = Glyph(x, y, cell['contents'])
    borders = [
        # Top border
        Glyph(x, y+1, "─"*cwidth),
        # Bottom border
        Glyph(x, y-1, "─"*cwidth),
        # Left and right
        Glyph(x-1, y, "│"),
        Glyph(x+cwidth, y, "│"),
    ]
    corners = [func(x, y, cell, field) for func in (_upleft, _upright, _downright, _downleft)]
    rv = borders + corners + [contents_glyph]
    import sys
    with open('log', 'a') as f:
        print(rv, file=f)
    return rv
