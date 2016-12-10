"""
Module display concerns itself with the displaying of the game board.
"""

import logging
import curses

from ..minesweeper.contents import Contents
from . import curses_colors


def get_colorpair(pair_name):
    val = curses_colors.CURSES_COLORPAIRS[pair_name]
    return curses.color_pair(val)


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
        self.attr = get_colorpair('white-black')

    def __str__(self):
        return self.strng

    def __repr__(self):
        return str(self.__dict__)


def _upleft(cx, cy, cell, field):
    x, y = cx - 1, cy - 1
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
    x, y, = cx - 1, cy + 1
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
    x, y = cx + len(cell['contents']), cy - 1
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
    x, y = cx + len(cell['contents']), cy + 1
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


def contacts_color(contacts):
    if contacts == -1:
        return get_colorpair('black-green')
    elif contacts == 0:
        return get_colorpair('black-black')
    elif contacts == 1:
        return get_colorpair('green-black')
    elif contacts == 2:
        return get_colorpair('cyan-black')
    elif contacts == 3:
        return get_colorpair('yellow-black')
    elif contacts >= 4:
        return get_colorpair('magenta-black')
    else:
        return get_colorpair('white-black')


def build_contents(cell, player):
    """
    Function build_contents returns a Glyph representing the contents of a
    cell, based on the state of that cell and the player who owns that cell.
    """
    x = ((1 + len(cell['contents'])) * cell['x']) + 1
    y = (2 * cell['y']) + 1
    rv = Glyph(x, y, cell['contents'])
    rv.attr = get_colorpair('black-white')

    # Probed cells show the number of cells they touch and an appropriate color
    if cell['probed']:
        mine_contacts = sum(
            [int(v == True) for _, v in cell['neighbors'].items()])
        # print(mine_contacts)
        rv.strng = " {} ".format(mine_contacts)
        rv.attr = contacts_color(mine_contacts)

    # If our cell's selected, mark it red
    if [cell['x'], cell['y']] == player['minefield']['selected']:
        # logging.error("Selected x,y: {} {}".format(cell['x'], cell['y']))
        rv.attr = get_colorpair('white-red')

    if not cell['probed']:
        rv.strng = Contents.empty
    if cell['flagged']:
        rv.strng = Contents.flag

    if not player['living']:
        if cell['contents'] == Contents.mine:
            rv.strng = Contents.mine
    return rv


def assemble_glyphs(cell, player):
    state = player['minefield']
    cwidth = len(cell['contents'])
    # Starting cell position is:
    #     ((length_in_dimension+1)*n) + 1
    # ypos = lambda y: (2*y)+1
    # xpos = lambda x: ((1+cwidth)*x)+1

    # The x position on the curses field where the glyph will be drawn
    x = ((1 + cwidth) * cell['x']) + 1
    y = (2 * cell['y']) + 1

    contents_glyph = build_contents(cell, player)

    borders = [
        # Top border
        Glyph(x, y + 1, "─" * cwidth),
        # Bottom border
        Glyph(x, y - 1, "─" * cwidth),
        # Left and right
        Glyph(x - 1, y, "│"),
        Glyph(x + cwidth, y, "│"),
    ]
    corners = [func(x, y, cell, state)
               for func in (_upleft, _upright, _downright, _downleft)]
    # if state['selected'] == [0, 0]:
    rv = borders + corners + [contents_glyph]
    # else:
        # rv = [contents_glyph]
    return rv
