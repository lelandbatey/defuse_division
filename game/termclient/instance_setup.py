
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

def create_client(args):

