
'''
Module mainmenu provides a function which draws a main menu to stdscr and
allows a user to select one of several buttons displayed on the screen. The
return value of the mainmenu function is the selection made by the player.
'''

import curses

from . import ui, curses_colors as colors

TITLE_TEXT = "Defuse Division"
OPTIONS = ["Single player", "Multiplayer", "Host and play"]

def xycenter(scr, text):
    '''
    Given a curses window and a string, return the x, y coordinates to pass to
    scr.addstr() for the provided text to be drawn in the horizontal and
    vertical center of the window.
    '''
    y, x = scr.getmaxyx()
    nx = (x // 2) - (len(text) // 2)
    ny = (y // 2) - (len(text.split('\n')) // 2)
    return nx, ny

def createCenterBtn(stdscr, y, contents):
    '''
    Returns a ui.TextBox horizontally centered at the y position with contents
    as the center of the textbox.
    '''
    # Add padding to x calculation because it't added implictly with the addstr
    # offset.
    x, _ = xycenter(stdscr, ' {} '.format(contents))
    rv = ui.TermBox(stdscr, contents, x, y, len(contents)+2, 1)
    rv.textinpt.addstr(0, 1, contents)
    rv.textinpt.refresh()
    return rv

def interspace(btn_h, btn_count, scr_h):
    '''
    Given the height of a button, the number of buttons to be displayed, and
    the height of the curses window the buttons will be displayed within,
    returns the number of lines to be given between each button for maximum
    vertical spacing.
    '''
    return (scr_h - (btn_h * btn_count)) // (btn_count - 1)

def demo(bh, bc, sh):
    btn = '\n'.join(['XXXX']*bh)
    isp = interspace(bh, bc, sh)
    cnct = ['----\n']*isp
    disp = ('\n'+''.join(cnct)).join([btn]*bc)
    while len(disp.split('\n')) < sh:
        disp += '\n----'
    assert(len(disp.split('\n')) == sh)
    return disp

def mainmenu(stdscr):
    curses.start_color()
    colors.colors_init()
    curses.curs_set(0)

    # Draw the title text at the top of the screen. Assumes single line TITLE_TEXT.
    title_height = len(TITLE_TEXT.split('\n'))
    ttlx, _ = xycenter(stdscr, TITLE_TEXT)
    ttly = 1
    stdscr.addstr(ttly, ttlx, TITLE_TEXT)
    stdscr.refresh()

    # Draw the buttons. Assumes single line button text.
    button_height = 4
    ttl_offset = ttly + title_height + 1
    screen_height, _ = stdscr.getmaxyx()
    screen_height = screen_height - ttl_offset
    spacing = interspace(button_height, len(OPTIONS), screen_height)

    buttons = ui.UIList()
    for idx, opt in enumerate(OPTIONS):
        offset = ttl_offset + (spacing * idx) + (button_height * idx)
        btn = createCenterBtn(stdscr, offset, opt)
        buttons.children.append(btn)
    buttons.get_current().select()

    # Wait for user selection
    rv = ''
    while True:
        cur = buttons.get_current()
        key = cur.getkey()
        if key == 'KEY_BTAB':
            buttons.select_prior()
        elif key == '\t':
            buttons.select_next()
        elif key == '\n':
            rv = cur.label
            break
    # TODO cleanup here
    return rv


