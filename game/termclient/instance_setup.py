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

from .. import game, concurrency
from ..server import server
from ..client import client as netclient


def create_client(args, uiopts):
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
    if uiopts['mode'] == 'Single player':
        port = 44444
        host = '127.0.0.1'
        srv = server.Server(host, port)
        bout = game.Bout(
            max_players=1,
            minefield_size=(args.width, args.height),
            mine_count=args.mines,
            player_constructor=srv.create_player)
        concurrency.concurrent(lambda: bout.add_player())()
        client = netclient.PlayerClient(host, port)
        return client
    elif uiopts['mode'] == 'Multiplayer':
        port = int(uiopts['connection']['port'])
        host = uiopts['connection']['hostname']
        client = netclient.PlayerClient(host, port)
        return client
    else:
        raise Exception("I don't know what to do for that option, sry :(")
