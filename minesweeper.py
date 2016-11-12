#!/usr/bin/env python3
import logging
import argparse
import curses
import sys

# Since cell probing is donre recursively, for large minefields with fiew
# mines, the default recursion limit may be reached.
sys.setrecursionlimit(5000)


from game.termclient import termclient as tc

logformat='%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'
logging.basicConfig(format=logformat, filename='client.log', level=logging.DEBUG)

def main():
    logging.debug('Launching minesweeper main')
    parser = argparse.ArgumentParser(
        description="Play a game of minesweeper. Use arrows to move, 'enter' or 'space' to probe, 'f' to flag, CTRL-C to exit."
    )
    parser.add_argument(
        '--height',
        type=int,
        default=16,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--width',
        type=int,
        default=16,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--mines', type=int, default=None, help="number of mines on the board")
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--vimkeys', dest='vimkeys', action='store_true')
    parser.add_argument('--maxsize', dest='maxsize', action='store_true')
    parser.add_argument('--host', default="127.0.0.1", help='remote host to connect to')
    parser.add_argument('--port', default=44444, type=int, help='port of remote host')
    parser.set_defaults(space=True)
    parser.set_defaults(debug=False)
    parser.set_defaults(maxsize=False)
    args = parser.parse_args()
    print(curses.wrapper(tc.main, args))

if __name__ == '__main__':
    main()
    # print(curses.wrapper(tc.main))
