
import threading
import logging


def concurrent(f):
    """Concurrent is a decorator for a function which will cause that function
    to immediately return when called, but be left running in 'in the
    background'. It is intended as a functional equivelent to the 'go func()'
    syntax in the Go programming language."""
    def err_logger(*args, **kwargs):
        '''
        err_logger logs uncaught exceptions, which is nice to have in long
        running processes in other threads.
        '''
        try:
            f(*args, **kwargs)
        except Exception as e:
            logging.error(e, exc_info=True)

    def rv(*args, **kwargs):
        t = threading.Thread(target=err_logger, args=(args), kwargs=kwargs)
        t.daemon = True
        t.start()
    return rv
