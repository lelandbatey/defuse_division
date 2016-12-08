from pprint import pprint, pformat
from time import sleep
import logging
import socket
import queue

try:
    import zeroconf as zeroconfig
except ImportError:
    logging.warn(
        "Zeroconf not installed. As a result, we cannot search for other "
        "servers on the network or advertise our own servers on the network. "
        "In the future, zeroconf may become a requirement to run this program."
    )

from .. import concurrency
from ..concurrency import concurrent
from .. import game, net


def local_address():
    """Returns the local address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    interface = s.getsockname()[0]
    s.close()
    return interface


class ServerInfo(object):
    def __init__(self, servername, address, port, properties):
        self.servername = servername
        self.address = address
        self.port = port
        self.properties = properties

    def __str__(self):
        return "{}:{}".format(self.address, self.port)

    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return "{}('{}', '{}', '{}', '{}')".format(
            self.__class__.__name__, self.servername, self.address, self.port,
            self.properties)

    def __hash__(self):
        return hash(repr(self))


def zeroconf_info():
    """zeroconf_info returns a list of tuples of the information about other
    zeroconf services on the local network. It does this by creating a
    zeroconf.ServiceBrowser and spending 0.25 seconds querying the network for
    other services."""
    ret_info = []

    def on_change(zeroconf, service_type, name, state_change):
        if state_change is zeroconfig.ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                address = "{}".format(socket.inet_ntoa(info.address))
                props = str(info.properties.items())
                item = ServerInfo(str(info.server), address, info.port, props)
                ret_info.append(item)

    zc = zeroconfig.Zeroconf()
    browser = zeroconfig.ServiceBrowser(
        zc, "_defusedivision._tcp.local.", handlers=[on_change])
    sleep(1)
    concurrency.concurrent(lambda: zc.close())()
    return ret_info


class PlayerClient(game.Conveyor):
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.stateq = queue.Queue()
        self.clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsock.connect((self.host, self.port))
        net.msg_recv(self.clientsock, self.stateq.put, lambda: None)
        conf = self.stateq.get()
        logging.debug("Conf: {}".format(conf))
        self.name = conf['name']

    def send_input(self, inpt):
        logging.debug('PlayerClient "{}" sending: {}'.format(
            self.name, net.json_dump(inpt)))
        if isinstance(inpt, dict) and 'change-name' in inpt:
            self.name = inpt['change-name']
        net.send(self.clientsock, inpt)
        # self.clientsock.sendall(net.json_dump(inpt).encode('utf-8')+net.SEP)

    def get_state(self):
        return self.stateq.get()
