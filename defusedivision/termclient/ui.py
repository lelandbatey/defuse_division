'''
Module ui exposes user interface objects for curses. For example, want to
create a set of buttons with labels that the user can tab-between? Create the
Buttons that you want, then place them in a list of buttons.
'''

import curses
import logging

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

    def __init__(self, stdscr, label="", x=0, y=0, width=10, height=1):
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
        self.borderbox.bkgd(' ', curses.A_BOLD)
        self.textinpt.bkgd(' ', colors.get_colorpair('black-white'))
        self.refresh()

    def deselect(self):
        self.borderbox.bkgd(' ', curses.A_NORMAL)
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
            if self.keypos < self.width - 1:
                self.textinpt.addstr(0, self.keypos, k)
                self.keypos += 1
        elif k == 'KEY_BACKSPACE':
            if self.keypos > 0:
                self.textinpt.addstr(0, self.keypos - 1, ' ')
                self.keypos -= 1
        self.textinpt.move(0, self.keypos)
        return k

    def select(self):
        '''
        Not only selects this textbox, but turns on the cursor and moves it to
        the correct possition within this textbox.
        '''
        self.borderbox.bkgd(' ', curses.A_BOLD)
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        curses.curs_set(1)
        self.textinpt.move(0, self.keypos)
        self.refresh()

    def deselect(self):
        '''
        Deselects this Textbox and turns off cursor visiblity.
        '''
        self.borderbox.bkgd(' ', curses.A_NORMAL)
        self.textinpt.bkgd(' ', colors.get_colorpair(self.default_color))
        curses.curs_set(0)
        self.refresh()


class ListBox(TermBox):
    '''
    Class ListBox provides a selectable list of items. It 'takes control' of
    keyboard input in that get_key won't return arrow keys or tab literals,
    instead using them to manipulate it's own display. 'Leaving' a ListBox will
    have to rely on other keys.
    '''

    def __init__(self, stdscr, label="", x=0, y=0, width=10, height=1):
        self.highlight_color = 'white-blue'
        self.current = None
        self.items = list()
        self.is_selected = False
        super().__init__(stdscr, label=label, x=x, y=y, width=width, height=height)

    def update_items(self, newitems):
        self.items = list()
        for item in newitems:
            self.current = 0 if not self.current else self.current
            self.items.append(item)
        self.refresh()

    def get_selection(self):
        if self.current is None:
            return None
        return self.items[self.current]

    def select_next(self):
        # If there's nothing to select
        if self.current is None:
            return
        self.current = (self.current + 1) % len(self.items)

    def select_prior(self):
        if self.current is None:
            return
        self.current = (self.current - 1) % len(self.items)

    def getkey(self):
        key = self.textinpt.getkey()
        if key == 'KEY_BTAB' or key == 'KEY_UP':
            self.select_prior()
            self.refresh()
        elif key == '\t' or key == 'KEY_DOWN':
            self.select_next()
            self.refresh()
        else:
            return key

    def select(self):
        self.is_selected = True
        self.refresh()

    def deselect(self):
        self.is_selected = False
        self.refresh()

    def refresh(self):
        prior, (cursr_y, cursr_x) = curses.curs_set(0), curses.getsyx()
        for idx, item in enumerate(self.items):
            fmt = '{{: <{}}}'.format(self.width-1)
            s = fmt.format(str(item))[:self.width-1]
            # s = str(item)[:self.width-1] if len(str(item)) > self.width-1 else str(item)
            color = colors.get_colorpair(self.default_color)
            if self.current == idx:
                if self.is_selected:
                    color = colors.get_colorpair('black-white')
                else:
                    color = colors.get_colorpair(self.highlight_color)
            self.textinpt.addstr(idx, 0, s, color)
        if self.is_selected:
            self.borderbox.bkgd(' ', curses.A_BOLD)
        else:
            self.borderbox.bkgd(' ', curses.A_DIM)
        self.borderbox.border()
        self.borderbox.refresh()
        self.textinpt.refresh()

        curses.curs_set(prior)
        curses.setsyx(cursr_y, cursr_x)
        curses.doupdate()



class UIList(object):
    '''
    UIList is a collection of children which are TermUI objects.
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
