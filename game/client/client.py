
from pprint import pprint, pformat
from time import sleep
import socket


import zeroconf as zeroconfig

from .. import concurrency


def local_address():
    """Returns the local address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    interface = s.getsockname()[0]
    s.close()
    return interface


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
                address = "{}:{}".format(socket.inet_ntoa(info.address), info.port)
                props = str(info.properties.items())
                ret_info.append((address, props))
    zc = zeroconfig.Zeroconf()
    browser = zeroconfig.ServiceBrowser(zc, "_http._tcp.local.", handlers=[on_change])
    sleep(0.25)
    concurrency.concurrent(lambda: zc.close())
    return ret_info
