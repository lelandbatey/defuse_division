
import logging
import socket
import gzip
import json

from .concurrency import concurrent

def json_dump(indata):
    """Creates prettified json representation of passed in object."""
    # return json.dumps(indata, sort_keys=True, indent=4, separators=(',', ': '))#, cls=date_handler)
    return json.dumps(indata)


SEP = b'\x00\x01\x00'

@concurrent
def msg_recv(conn, sendfunc, closefunc):
    '''
    Function msg_recv reads null-delimited series of bytes from `conn`, which
    is a socket. Each series of bytes is then de-serialized into a json object,
    and `sendfunc` is called with that json object.
    `closefunc` is called if/when the socket `conn` is closed.
    '''
    buf = bytes()
    while True:
        try:
            data = conn.recv(8192)

            # No data means the connection is closed
            if not data:
                closefunc()
                return

            inbuf = buf + data
            if SEP in inbuf:
                parts = inbuf.split(SEP)
                # logging.debug("Length of parts: {}".format(len(parts)))
                tosend = [parts[0]]
                for p in parts[1:-1]:
                    tosend.append(p)
                buf = parts[-1]
                for msg in tosend:
                    m = gzip.decompress(msg)
                    m = m.decode('utf-8')
                    logging.debug("Msg: {}".format(m[:150]+'...' if len(m) > 150 else m))
                    obj = json.loads(m)
                    sendfunc(obj)
            else:
                buf += data
        except Exception as e:
            logging.exception(e)
@concurrent
def msg_send(conn, sourcefunc):
    '''
    Function msg_send continuously sends the result of `sourcefunc` on the
    socket `conn`. This is done by calling `sourcefunc`, serializing what's
    returned by sourcefunc into json, then calling `conn.sendall()` with the
    json-serialized string encoded via utf-8 into bytes.
    '''
    while True:
        msg = sourcefunc()
        try:
            send(conn, msg)
        except OSError:
            # The socket's closed, return from this function
            return

def send(conn, obj):
    msg = json_dump(obj)
    msg = msg.encode('utf-8')
    msg = gzip.compress(msg)
    msg += SEP
    conn.sendall(msg)

