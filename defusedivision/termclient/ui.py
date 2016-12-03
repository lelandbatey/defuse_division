'''
Module ui exposes user interface objects for curses. For example, want to
create a set of buttons with labels that the user can tab-between? Create the
Buttons that you want, then place them in a list of buttons.
'''

import curses

from . import curses_colors as colors


def xycenter(scr, text):
    '''
    Given a curses window and a string, return the x, y coordinates to pass to
    scr.addstr() for the provided text to be drawn in the horizontal and
    vertical center of the window.
    '''
    y, x = scr.getmaxyx()
    nx = (x // 2) - (len(text) // 2)
    ny = (y // 2) - (len(text.split('\n')) // 2)
    return nx, ny

def interspace(btn_h, btn_count, scr_h):
    '''
    Given the height of a button, the number of buttons to be displayed, and
    the height of the curses window the buttons will be displayed within,
    returns the number of lines to be given between each button for maximum
    vertical spacing.
    '''
    return (scr_h - (btn_h * btn_count)) // (btn_count - 1)


def demo(bh, bc, sh):
    btn = '\n'.join(['XXXX'] * bh)
    isp = interspace(bh, bc, sh)
    cnct = ['----\n'] * isp
    disp = ('\n' + ''.join(cnct)).join([btn] * bc)
    while len(disp.split('\n')) < sh:
        disp += '\n----'
    assert (len(disp.split('\n')) == sh)
    return disp


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
        self.keypos = 0

    def get_contents(self):
        '''
        Returns the contents of this textbox.
        '''
        return self.textinpt.instr(0, 0).decode('utf-8')

    def getkey(self):
        k = self.textinpt.getkey()
        if len(k) == 1 and not k.isspace():
            if self.keypos < self.width-1:
                self.textinpt.addstr(0, self.keypos, k)
                self.keypos += 1
        elif k == 'KEY_BACKSPACE':
            if self.keypos > 0:
                self.textinpt.addstr(0, self.keypos-1, ' ')
                self.keypos -= 1
        self.textinpt.move(0, self.keypos)
        return k

    def select(self):
        '''
        Not only selects this textbox, but turns on the cursor and moves it to
        the correct possition within this textbox.
        '''
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        curses.curs_set(1)
        self.textinpt.move(0, self.keypos)
        self.refresh()

    def deselect(self):
        '''
        Deselects this Textbox and turns off cursor visiblity.
        '''
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        curses.curs_set(0)
        self.refresh()


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

