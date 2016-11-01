
import threading


def concurrent(f):
    """Concurrent is a decorator for a function which will cause that function
    to immediately return when called, but be left running in 'in the
    background'. It is intended as a functional equivelent to the 'go func()'
    syntax in the Go programming language."""
    def rv(*args, **kwargs):
        t = threading.Thread(target=f, args=(args), kwargs=kwargs)
        t.daemon = True
        t.start()
    return rv
