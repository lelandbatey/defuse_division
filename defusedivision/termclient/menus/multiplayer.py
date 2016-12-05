'''
Module multiplayer_menu displays a curses menu allowing the user to input info
about a connecting to a multiplayer minesweeper server.
'''

from threading import Lock
import curses

from .. import ui, curses_colors as colors
from ...client.client import zeroconf_info
from ...concurrency import concurrent

UPDATE_LOCALSERVERS = True


@concurrent
def update_locallist(listb, refresh_lock):
    global UPDATE_LOCALSERVERS
    while UPDATE_LOCALSERVERS:
        info = zeroconf_info()
        if not UPDATE_LOCALSERVERS: break
        refresh_lock.acquire()
        listb.update_items(info)
        refresh_lock.release()


def multiplayer_menu(stdscr):
    global UPDATE_LOCALSERVERS
    if not curses.has_colors():
        curses.start_color()
    colors.colors_init()
    curses.curs_set(0)

    refresh_lock = Lock()

    bottom, _ = stdscr.getmaxyx()
    stdscr.addstr(bottom - 1, 0, "Ctrl+Backspace to return to main menu")

    x, y = ui.xycenter(stdscr, " ")
    hostwidth = max(20, x // 2)
    portwidth = 8
    x, y = ui.xycenter(stdscr, " " * (hostwidth + portwidth))
    y -= 5
    x -= 1
    stdscr.addstr(y - 2, x, "Hostname:")
    stdscr.addstr(y - 2, x + hostwidth + 3, "Port:")
    stdscr.addstr(y, x + hostwidth + 1, ":")
    stdscr.addstr(y + 3, x, "Local Servers:")
    stdscr.refresh()
    hostname_txtbx = ui.Textbox(stdscr, 'hostname', x, y, hostwidth, 1)
    port_txtbx = ui.Textbox(stdscr, 'port', x + hostwidth + 3, y, portwidth, 1)


    listb = ui.ListBox(stdscr, 'localservers', x, y + 5,
                       hostwidth + portwidth + 3, 5)
    update_locallist(listb, refresh_lock)

    buttons = ui.UIList()
    buttons.children += [hostname_txtbx, port_txtbx, listb]

    buttons.get_current().select()
    rv = {"hostname": None, "port": None}
    while True:
        cur = buttons.get_current()
        refresh_lock.acquire()
        refresh_lock.release()
        key = cur.getkey()
        if key == 'KEY_BTAB' or key == 'KEY_LEFT':
            buttons.select_prior()
        elif key == '\t' or key == 'KEY_RIGHT':
            buttons.select_next()
        elif key == '\n':
            if cur.label == 'localservers':
                info = cur.get_selection()
                rv['hostname'] = info.address
                rv['port'] = info.port
            else:
                rv['hostname'] = hostname_txtbx.get_contents().strip()
                rv['port'] = port_txtbx.get_contents().strip()
            break
        elif key == '\x08':
            # Return to the prior menu
            UPDATE_LOCALSERVERS = False
            return 'BACK'
    UPDATE_LOCALSERVERS = False
    return rv