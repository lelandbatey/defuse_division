import logging
import atexit
import socket
import queue
import json

from .. import game, net
from ..concurrency import concurrent
from ..minesweeper.minefield import MineField


def local_address(fallback):
    """Returns the local address of this computer."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        interface = s.getsockname()[0]
        s.close()
    except OSError:
        interface = fallback
        logging.info(
            'Cannot connect to network determine interface, using fallback "{}"'.
            format(fallback))

    return interface


@concurrent
def localnet_register(host, port):
    '''
    Runs a never-exiting thread which only registers a local network service
    via Zeroconf and then responds to info requests.
    '''
    try:
        from zeroconf import ServiceInfo, Zeroconf
        from time import sleep
    except ImportError as e:
        logging.error(
            'Zeroconf not installed, cannot register this server on the local '
            'network. Other players may still connect, but they must be told '
            'what your hostname and port are (hostname: {}, port: {})'.format(
                host, port))
        return

    advertised_interface = local_address('127.0.0.1')

    info = ServiceInfo(
        "_defusedivision._tcp.local.",
        "{}{}._defusedivision._tcp.local.".format(
            host.replace('.', '-'), advertised_interface.replace('.', '-')),
        address=socket.inet_aton(advertised_interface),
        port=int(port),
        weight=0,
        priority=0,
        properties=b"")

    zc = Zeroconf()
    zc.register_service(info)
    atexit.register(lambda: zc.close())
    while True:
        sleep(0.1)


class PlayerServer(game.Conveyor):
    '''
    PlayerServer implements a game.Conveyor object, allowing this object to act
    like a 'Player' object, as far as a Bout is concerned. Each remote player
    in a Bout is allocated a PlayerServer which keeps track of that players
    minefied, the various states of the player (whether the player's alive,
    whether they're victorious, etc), and the socket connection to the
    remote player.
    '''

    def __init__(self,
                 conn,
                 addr,
                 name,
                 bout,
                 mine_count=None,
                 height=None,
                 width=None):
        self.conn = conn
        self.addr = addr
        self.name = name
        self.bout = bout
        self.stateq = queue.Queue()
        self.mfield = MineField(
            height=height, width=width, mine_count=mine_count)
        self.living = True
        self.victory = False

        net.msg_recv(self.conn, self.send_input, self._remove_self)
        net.msg_send(conn, self.get_state)
        # Send the player information as the very first thing
        # self.conn.sendall(net.json_dump(self.json()).encode('utf-8')+net.SEP)
        net.send(self.conn, self.json())

    def send_input(self, inpt):
        # Just pass the input to the parent bout, but with info saying that
        # this input comes from this player
        logging.debug(inpt)
        self.bout.send_input({'player': self.name, 'input': inpt})

    def get_state(self):
        return self.stateq.get()

    def _remove_self(self):
        '''
        Removes ourself from the bout and close all associated sockets.
        '''
        self.conn.close()
        # Causes the concurrently running msg_send to try to send 'die' over
        # the closed socket, causing that thread to throw an exception and die.
        self.stateq.put("die")
        self.bout.remove_player(self.name)

    def json(self):
        return {
            'name': self.name,
            'living': self.living,
            'minefield': self.mfield.json(),
            'victory': self.victory,
        }


class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Enable address re-use so if we don't quite close the socket, the
        # port/address isn't stuck
        self.srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.srvsock.bind((host, port))
        self.srvsock.listen(5)
        if not host.startswith("127."):
            localnet_register(host, port)

    def create_player(self,
                      name,
                      bout,
                      mine_count=None,
                      height=None,
                      width=None):
        '''
        Method `create_player` will create a Player-like object which receives
        its input over the network.
        '''
        (conn, address) = self.srvsock.accept()
        player = PlayerServer(conn, address, name, bout, mine_count, height,
                              width)
        return player
