
import curses

from game.termclient import termclient as tc

if __name__ == '__main__':
	print(curses.wrapper(tc.main))
