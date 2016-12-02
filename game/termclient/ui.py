'''
Module ui exposes user interface objects for curses. For example, want to
create a set of buttons with labels that the user can tab-between? Create the
Buttons that you want, then place them in a list of buttons.
'''

import curses

from . import curses_colors as colors

class TermUI(object):
    '''
    Abstract class TermUI describes the functionality of any object which may
    be used as a user interface object.
    '''
    def select(self):
        raise NotImplementedError
    def deselect(self):
        raise NotImplementedError
    def refresh(self):
        raise NotImplementedError
    def getch(self):
        return NotImplementedError

class TermBox(TermUI):
    '''
    Class TermBox creates a nice 'box' out of curses windows. To be used as a
    base for other interface objects.
    '''
    def __init__(self, stdscr, label, x, y, width, height):
        self.default_color = 'white-black'
        self.stdscr = stdscr
        self.label = label
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.borderbox = curses.newwin(height + 2, width + 2, y - 1, x - 1)
        self.textinpt = curses.newwin(height, width, y, x)
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        self.textinpt.keypad(1)
        self.refresh()

    def refresh(self):
        self.borderbox.border()
        self.borderbox.refresh()
        self.textinpt.refresh()

    def getch(self):
        return self.textinpt.getch()

    def getkey(self):
        return self.textinpt.getkey()

    def addstr(self, *args):
        self.textinpt.addstr(*args)

    def select(self):
        self.textinpt.bkgd(' ', colors.get_colorpair('black-white'))
        self.refresh()

    def deselect(self):
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        self.refresh()


class Textbox(TermBox):
    '''
    Class Textbox provides a TermUI object which can be used to enter text.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UIList(object):
    '''
    Buttonlist is a collection of children which are TermUI objects.
    '''
    def __init__(self):
        self.children = []
        self.current = 0

    def select_next(self):
        '''
        Method select_next will call the 'select()' method on the next child in
        the list of children, wrapping to the first child when we've already
        selected the last child in children.
        '''
        self.children[self.current].deselect()
        self.current = (self.current + 1) % len(self.children)
        self.children[self.current].select()

    def select_prior(self):
        '''
        Method select_prior will call the `select()` method on the prior child
        in the list of children, wrapping to the last child when the first
        child is already selected.
        '''
        self.children[self.current].deselect()
        self.current = (self.current - 1) % len(self.children)
        self.children[self.current].select()

    def get_current(self):
        '''
        Return the currently selected child TermUI object.
        '''
        return self.children[self.current]

    def refresh(self):
        for btn in self.children:
            btn.refresh()

