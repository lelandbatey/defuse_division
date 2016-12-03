'''
Module multiplayer_menu displays a curses menu allowing the user to input info
about a connecting to a multiplayer minesweeper server.
'''

import curses

from .. import ui, curses_colors as colors

def multiplayer_menu(stdscr):
    if not curses.has_colors():
        curses.start_color()
    colors.colors_init()
    curses.curs_set(0)

    bottom, _ = stdscr.getmaxyx()
    stdscr.addstr(bottom-1, 0, "Ctrl+Backspace to return to main menu")

    x, y = ui.xycenter(stdscr, " ")
    hostwidth = max(20, x//2)
    portwidth = 8
    x, y = ui.xycenter(stdscr, " "*(hostwidth+portwidth))
    x -= 1
    stdscr.addstr(y-2, x, "Hostname:")
    stdscr.addstr(y-2, x+hostwidth+3, "Port:")
    stdscr.addstr(y, x+hostwidth+1, ":")
    stdscr.refresh()
    hostname_txtbx = ui.Textbox(stdscr, 'hostname', x, y, hostwidth, 1)
    port_txtbx = ui.Textbox(stdscr, 'port', x+hostwidth+3, y, portwidth, 1)

    buttons = ui.UIList()
    buttons.children += [hostname_txtbx, port_txtbx]

    buttons.get_current().select()
    rv = {"hostname": None, "port": None}
    while True:
        cur = buttons.get_current()
        key = cur.getkey()
        if key == 'KEY_BTAB' or key == 'KEY_LEFT':
            buttons.select_prior()
        elif key == '\t' or key == 'KEY_RIGHT':
            buttons.select_next()
        elif key == '\n':
            rv['hostname'] = hostname_txtbx.get_contents().strip()
            rv['port'] = port_txtbx.get_contents().strip()
            break
        elif key == '\x08':
            # Return to the prior menu
            return 'BACK'
    return rv

