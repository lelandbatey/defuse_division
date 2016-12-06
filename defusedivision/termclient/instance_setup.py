'''
Module instance_setup contains logic for the different ways to initialize
minesweeper. For example, running purely as a server; or forking and running a
server while also running a client. Each mode of operation may require vastly
different initialization procedures, and the setup and management of each mode
is the responsibility of this module.

Different possible modes:

    1. Create a server, and also create a client. Have the client connect to
    the server, and when the bout is completed, close out the client and
    shut-down the server.
    2. Run only the server. Once a bout is completed, send a "bout completed"
    message to both clients and disconnect them, but return to waiting for a
    new state.
    3. Run only the client, and connect to a remote server.

'''

import time

from .. import game, concurrency
from ..server import server
from ..client import client as netclient
from ..minesweeper import contents


def field_size(scr_w, scr_h, cellwidth=3):
    '''
    Field size returns the largest minefield dimensions which will fit in a
    terminal screen of the given size.
    '''
    x = (scr_w - 2) // (1 + cellwidth)
    y = (scr_h - 2) // 2
    return x, y


TOO_LARGE_ERR = '''
Press any key to continue. But first, here's a warning you should read:

The default minefield size of {} is too large for your current terminal window.
Instead, we'll use the largest minefield size that will fit in your terminal,
which is {}.'''

TOO_LARGE_MULTIPLAYER_WARNING = TOO_LARGE_ERR + '''

Additionally, since we're connecting to a multiplayer server, other players may
be using a board size that's so large we may not be able to display it. If the
game crashes, that's probably why.
'''


def create_client(stdscr, args, uiopts):
    '''
    Function create_client will return a `game.Conveyor` compatible object
    representing the current player client.

    If uiopts['mode'] is 'Single player', then a local game.Server will be
    started, and a client connected to that server will be returned. For now,
    the local game.Server will only be initialized with default values.

    If uiopts['mode'] is 'Multiplayer', then use the provided
    uiopts['connection'] data to connect to the specified server and return a
    PlayerClient for that connection.

    If uiopts['mode'] is 'Host and play', ... I haven't decided how I'll do
    that one yet.
    '''
    # Change the contents of cells based on command line args

    height, width = args.height, args.width
    default_width, default_height = 16, 16
    screen_h, screen_w = stdscr.getmaxyx()
    too_tall, too_wide = False, False

    # If the user manually sets a command line flag above a safe limit, we
    # assume they know what their doing and we won't override it, which is why
    # we only use safe sizes if the height and width options are unset.
    max_width, max_height = field_size(screen_w, screen_h)
    if height is None:
        # Take a little bit off, just to make sure
        max_height -= 1
        if max_height < default_height:
            height = max_height
            too_tall = True
        else:
            height = default_height
    if width is None:
        max_width -= 1
        if max_width < default_width:
            width = max_width
            too_wide = True
        else:
            width = default_width
    if args.maxsize:
        width, height = max_width, max_height

    if uiopts['mode'] == 'Single player':
        port = 44444
        host = '127.0.0.1'
        srv = server.Server(host, port)
        if too_tall or too_wide:
            stdscr.clear()
            stdscr.refresh()
            stdscr.addstr(0, 0, TOO_LARGE_ERR.format(
                (default_width, default_height), (height, width)))
            stdscr.getch()

        bout = game.Bout(
            max_players=1,
            minefield_size=(width, height),
            mine_count=args.mines,
            player_constructor=srv.create_player)
        concurrency.concurrent(lambda: bout.add_player())()
        client = netclient.PlayerClient(host, port)
        # Auto-make a new minefield of the size we want
        if args.playername:
            client.send_input({'change-name': args.playername})
        client.send_input({
            'new-minefield': {
                'height': height,
                'width': width,
                'mine_count': None
            }
        })
        client.get_state()
        return client

    elif uiopts['mode'] == 'Multiplayer':
        port = int(uiopts['connection']['port'])
        host = uiopts['connection']['hostname']
        client = netclient.PlayerClient(host, port)

        if too_tall or too_wide:
            stdscr.clear()
            stdscr.refresh()
            err = TOO_LARGE_MULTIPLAYER_WARNING.format(
                (default_width, default_height), (height, width))
            stdscr.addstr(0, 0, err)
            stdscr.getch()

        if args.playername:
            client.send_input({'change-name': args.playername})
        client.send_input({
            'new-minefield': {
                'height': height,
                'width': width,
                'mine_count': None
            }
        })
        client.get_state()
        return client
    else:
        raise Exception("I don't know what to do for that option, sry :(")
