import contextlib
import sys

# from http://stackoverflow.com/a/29824059
@contextlib.contextmanager
def smart_open(filename, mode='r'):
    if filename == '-':
        if mode is None or mode == '' or 'r' in mode:
            fh = sys.stdin
        else:
            fh = sys.stout
    else:
        fh = open(filename, mode)

    try:
        yield fh
    finally:
        if filename is not '-':
            fh.close()




