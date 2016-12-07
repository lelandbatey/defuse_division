'''
Module multiplayer_menu displays a curses menu allowing the user to input info
about connecting to a multiplayer minesweeper server, or select a server on the
local network (if there are any).
'''

from threading import Lock
import logging
import curses

from .. import ui, curses_colors as colors
from ...client.client import zeroconf_info
from ...concurrency import concurrent
from ...sound import sound

UPDATE_LOCALSERVERS = True


@concurrent
def update_locallist(listb, refresh_lock):
    global UPDATE_LOCALSERVERS
    cached = dict()
    durable_duration = 5
    while UPDATE_LOCALSERVERS:
        toremove = []
        for item in cached:
            if cached[item] > durable_duration:
                toremove.append(item)
            cached[item] += 1
        for item in toremove:
            del cached[item]
        info = zeroconf_info()
        for item in info:
            cached[item] = 0
        if not UPDATE_LOCALSERVERS: break
        logging.debug('Acquiring refresh lock for updating list of local servers.')
        refresh_lock.acquire()
        listb.update_items(cached.keys())
        refresh_lock.release()
        logging.debug('Releasing refresh lock after updating locla server list')


def multiplayer_menu(stdscr):
    global UPDATE_LOCALSERVERS
    if not curses.has_colors():
        curses.start_color()
    colors.colors_init()
    curses.curs_set(0)

    refresh_lock = Lock()

    bottom, _ = stdscr.getmaxyx()
    stdscr.addstr(bottom - 1, 0, "Press 'escape' to return to main menu")

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
    for ch in "44444":
        port_txtbx.addstr(0, port_txtbx.keypos, ch)
        port_txtbx.keypos += 1
    port_txtbx.refresh()


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
        sound.SAMPLES.move_click.play()
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
        # If Ctrl+Backspace or Escape
        elif key in ['\x08', '\x1b']:
            # Return to the prior menu
            UPDATE_LOCALSERVERS = False
            return 'BACK'
    UPDATE_LOCALSERVERS = False
    return rv
