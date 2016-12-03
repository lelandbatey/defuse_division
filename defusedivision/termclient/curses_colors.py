"""
Module curses_colors provides simple access to curses color-pair attributes.
The curses color-numbers from 120 to 184 are defined as being
foreground-background combinations of the 8 base curses colors (red, blue,
cyan, black, green, white, yellow, magenta).

A simple example is as follows:

    >>> import curses
    >>> import curses_colors
    >>> stdscr = curses.initscr()
    >>> curses_color.colors_init()
    >>> green_black_attr = curses_color.CURSES_COLORPAIRS['black-green']
    >>> stdscr.addstr(0, 0, "test", curses.color_pair(green_black_attr))

A more elaborate example may be found in the implementation for curses_color,
in a function called `_test`.
"""

import curses

CURSES_COLORPAIRS = dict()

BASE_CURSES_COLORS = {
    'red': curses.COLOR_RED,
    'blue': curses.COLOR_BLUE,
    'cyan': curses.COLOR_CYAN,
    'black': curses.COLOR_BLACK,
    'green': curses.COLOR_GREEN,
    'white': curses.COLOR_WHITE,
    'yellow': curses.COLOR_YELLOW,
    'magenta': curses.COLOR_MAGENTA,
}


def colors_init():
    """
    Initializes all color pairs possible into the dictionary CURSES_COLORPAIRS.
    Thus, getting an attribute for a black foreground and a green background
    would look like:
        >>> curses_color.colors_init()
        >>> green_black_attr = curses_color.CURSES_COLORPAIRS['black-green']
        >>> stdscr.addstr(0, 0, "test", curses.color_pair(green_black_attr))
    """
    if len(CURSES_COLORPAIRS): return
    assert curses.has_colors(
    ), "Curses wasn't configured to support colors. Call curses.start_color()"
    start_number = 120
    for fg in BASE_CURSES_COLORS.keys():
        for bg in BASE_CURSES_COLORS.keys():
            pair_num = len(CURSES_COLORPAIRS) + start_number
            curses.init_pair(pair_num, BASE_CURSES_COLORS[fg],
                             BASE_CURSES_COLORS[bg])
            pair_name = "{}-{}".format(fg, bg)
            CURSES_COLORPAIRS[pair_name] = pair_num


def get_colorpair(pair_name):
    '''
    Returns the color attribute for the given foreground-background attribute,
    ready for use in a call to addstr.
    '''
    val = CURSES_COLORPAIRS[pair_name]
    return curses.color_pair(val)

def _test(stdscr):
    import time

    colors_init()
    label_width = max([len(k) for k in CURSES_COLORPAIRS.keys()])
    cols = 4
    for idx, k in enumerate(CURSES_COLORPAIRS.keys()):
        label = "{{:<{}}}".format(label_width).format(k)
        x = (idx % cols) * (label_width + 1)
        y = idx // cols

        pair = curses.color_pair(CURSES_COLORPAIRS[k])
        stdscr.addstr(y, x, label, pair)
        time.sleep(0.1)
        stdscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(_test)
