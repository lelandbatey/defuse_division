
import socket

import zeroconf

def local_address():
    """Returns the local address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    interface = s.getsockname()[0]
    s.close()
    return interface

