'''
Module mainmenu provides a function which draws a main menu to stdscr and
allows a user to select one of several buttons displayed on the screen. The
return value of the mainmenu function is the selection made by the player.

Notes:
    The large ascii-art text saying 'Defuse Division' was generated using the
    software known as 'toilet' using the figlet font 'smmono12.tlf'.
    The bomb ascii art is of my own design.
'''

from threading import Lock
import curses
import time

from ...concurrency import concurrent
from ...sound import sound
from .. import ui, curses_colors as colors
from . import multiplayer
TITLE_TEXT = """▗▄▄         ▄▄                       .--_    
▐▛▀█       ▐▛▀                      /    `.!,
▐▌ ▐▌ ▟█▙ ▐███ ▐▌ ▐▌▗▟██▖ ▟█▙    ,-┘ └-.  -*-
▐▌ ▐▌▐▙▄▟▌ ▐▌  ▐▌ ▐▌▐▙▄▖▘▐▙▄▟▌  / ▟▖    \ '|`
▐▌ ▐▌▐▛▀▀▘ ▐▌  ▐▌ ▐▌ ▀▀█▖▐▛▀▀▘  │ ▜     |    
▐▙▄█ ▝█▄▄▌ ▐▌  ▐▙▄█▌▐▄▄▟▌▝█▄▄▌  \       /    
▝▀▀   ▝▀▀  ▝▘   ▀▀▝▘ ▀▀▀  ▝▀▀    `-...-'     
▗▄▄    █         █         █                  
▐▛▀█   ▀         ▀         ▀                  
▐▌ ▐▌ ██  ▐▙ ▟▌ ██  ▗▟██▖ ██   ▟█▙ ▐▙██▖      
▐▌ ▐▌  █   █ █   █  ▐▙▄▖▘  █  ▐▛ ▜▌▐▛ ▐▌      
▐▌ ▐▌  █   ▜▄▛   █   ▀▀█▖  █  ▐▌ ▐▌▐▌ ▐▌      
▐▙▄█ ▗▄█▄▖ ▐█▌ ▗▄█▄▖▐▄▄▟▌▗▄█▄▖▝█▄█▘▐▌ ▐▌      
▝▀▀  ▝▀▀▀▘  ▀  ▝▀▀▀▘ ▀▀▀ ▝▀▀▀▘ ▝▀▘ ▝▘ ▝▘      """

BOMB1 = """     .--_
    /    `.!,
 ,-┘ └-.  -*-
/ ▟▖    \ '|`
│ ▜     | 
\       /
 `-...-'"""
BOMB2 = """     .--_    
    /    `\:/
 ,-┘ └-.  ,x.
/ ▟▖    \ /;\ 
│ ▜     |    
\       /    
 `-...-'     """
UPDATE_BOMBSPRITE = True

OPTIONS = ["Single player", "Multiplayer", "Host and play"]


def createCenterBtn(stdscr, y, contents):
    '''
    Returns a ui.TextBox horizontally centered at the y position with contents
    as the center of the textbox.
    '''
    # Add padding to x calculation because it't added implictly with the addstr
    # offset.
    x, _ = ui.xycenter(stdscr, ' {} '.format(contents))
    rv = ui.TermBox(stdscr, contents, x, y, len(contents) + 2, 1)
    rv.textinpt.addstr(0, 1, contents)
    rv.textinpt.refresh()
    return rv


def drawbomb(stdscr, idx):
    bombs = [BOMB1, BOMB2]
    idx = (idx + 1) % len(bombs)
    b = bombs[idx]
    ttlx, _ = ui.xycenter(stdscr, TITLE_TEXT.split('\n')[0])
    for lno, line in enumerate(b.split('\n')):
        stdscr.addstr(lno, ttlx + 32, line)
    stdscr.refresh()
    return idx


@concurrent
def redraw_bomb(stdscr, refresh_lock):
    global UPDATE_BOMBSPRITE
    idx = 0
    while True:
        time.sleep(0.25)
        if UPDATE_BOMBSPRITE:
            refresh_lock.acquire()
            curses.curs_set(0)
            idx = drawbomb(stdscr, idx)
            refresh_lock.release()
        else:
            break


def mainmenu(stdscr):
    global UPDATE_BOMBSPRITE
    if curses.has_colors():
        curses.start_color()
    colors.colors_init()
    curses.curs_set(0)
    refresh_lock = Lock()
    while True:
        # Draw the title text at the top of the screen. Assumes single line TITLE_TEXT.
        title_height = len(TITLE_TEXT.split('\n'))
        ttlx, _ = ui.xycenter(stdscr, TITLE_TEXT.split('\n')[0])
        ttly = 0
        for lno, line in enumerate(TITLE_TEXT.split('\n')):
            stdscr.addstr(ttly + lno, ttlx, line)
        stdscr.refresh()
        UPDATE_BOMBSPRITE = True
        redraw_bomb(stdscr, refresh_lock)

        # Draw the buttons. Assumes single line button text.
        button_height = 3
        ttl_offset = ttly + title_height + 1
        screen_height, _ = stdscr.getmaxyx()
        screen_height = screen_height - ttl_offset
        spacing = ui.interspace(button_height, len(OPTIONS), screen_height)

        buttons = ui.UIList()
        for idx, opt in enumerate(OPTIONS):
            offset = ttl_offset + (spacing * idx) + (button_height * idx)
            btn = createCenterBtn(stdscr, offset, opt)
            buttons.children.append(btn)
        buttons.get_current().select()

        # Wait for user selection
        rv = {'mode': '', 'connection': {'hostname': None, 'port': None}}
        while True:
            cur = buttons.get_current()
            refresh_lock.acquire()
            refresh_lock.release()
            sound.SAMPLES.move_click.play()
            key = cur.getkey()
            if key == 'KEY_BTAB' or key == 'KEY_UP':
                buttons.select_prior()
            elif key == '\t' or key == 'KEY_DOWN':
                buttons.select_next()
            elif key == '\n':
                rv['mode'] = cur.label
                UPDATE_BOMBSPRITE = False
                break
        # TODO cleanup here
        if rv['mode'] == 'Multiplayer':
            refresh_lock.acquire()
            refresh_lock.release()
            stdscr.clear()
            stdscr.touchwin()
            stdscr.refresh()
            UPDATE_BOMBSPRITE = False
            conn_opts = multiplayer.multiplayer_menu(stdscr)
            if conn_opts == 'BACK':
                stdscr.clear()
                stdscr.touchwin()
                stdscr.refresh()
                continue
            rv['connection'] = conn_opts
        return rv
