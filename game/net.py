
import logging
import socket
import json

from .concurrency import concurrent

def json_dump(indata):
    """Creates prettified json representation of passed in object."""
    return json.dumps(indata, sort_keys=True, indent=4, \
     separators=(',', ': '))#, cls=date_handler)


SEP = b'\x00\x00\x00\x01\x01\x01SEP'

@concurrent
def msg_recv(conn, sendfunc):
    buf = bytes()
    while True:
        try:
            data = conn.recv(8192)
            # logging.debug("Len of data thus far {}".format(len(data)))
            inbuf = buf + data
            if SEP in inbuf:
                parts = inbuf.split(SEP)
                logging.debug("Length of parts: {}".format(len(parts)))
                tosend = [parts[0]]
                for p in parts[1:-1]:
                    tosend.append(p)
                buf = parts[-1]
                for msg in tosend:
                    m = msg.decode('utf-8')
                    logging.debug("Msg: {}".format(m[:150]+'...' if len(m) > 150 else m))
                    obj = json.loads(m)
                    sendfunc(obj)
            else:
                buf += data
        except Exception as e:
            logging.exception(e)
@concurrent
def msg_send(conn, sourcefunc):
    while True:
        msg = sourcefunc()
        msg = json_dump(msg)
        logging.debug('Sending message: {}'.format(msg[:150]+'...' if len(msg) > 150 else msg))
        msg = msg.encode('utf-8')
        msg += SEP
        conn.sendall(msg)
