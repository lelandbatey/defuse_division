
from os.path import join, dirname, realpath
import logging
try:
    import pygame
except ImportError:
    logging.warn("Cannot import pygame, sound will not be playable")
    pygame = None
import os
# SUPER important that this be here. Without it, audio on Linux will be weirdly
# broken (at least in my experience). HOWEVER, this only happens if I haven't
# installed all the libsdl1.2-*-dev libraries.
# os.environ['SDL_AUDIODRIVER'] = 'alsa'

SOUND_PATH = dirname(realpath(__file__))
_SOUND_ENABLE = False

def attempt_enable():
    '''
    Attempts to enable the playing of sound. If pygame is not available, sound
    will not be enabled. If pygame is available, we initialize the pygame
    mixer.
    '''
    global _SOUND_ENABLE
    if not pygame is None:
        pygame.mixer.quit()
        pygame.mixer.pre_init(22050, 8, 2, 10)
        pygame.init()
        _SOUND_ENABLE = True

def disable():
    '''
    Disables the playing of sound.
    '''
    global _SOUND_ENABLE
    _SOUND_ENABLE = False

def is_sound_playable():
    '''
    Returns whether we can play sound or not. Even if attempt_enable is called,
    if pygame is not available, then sound won't be playable.
    '''
    global _SOUND_ENABLE
    if not pygame is None and _SOUND_ENABLE:
        return True
    return False

class _bunch(object):
    '''
    A convenient way to create a 'bunch' of . accessible items of a collection.
    '''
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Sample(object):
    '''
    Represents a single playable 'noise'.
    '''
    def __init__(self, name, filename='', origin='', creator='', license=None):
        self.name = name
        self.filename = filename
        self.origin = origin
        self.creator = creator
        self.license = license
        if not pygame is None:
            global SOUND_PATH
            self.sound = pygame.mixer.Sound(join(SOUND_PATH, filename))

    def play(self):
        global _SOUND_ENABLE
        if not pygame is None and _SOUND_ENABLE:
            self.sound.play()



SOUNDS_DATA = {
    "probe": {
        'filename': '29301__junggle__btn121.wav',
        'origin': 'https://www.freesound.org/people/junggle/sounds/29301/',
        'creator': 'junggle',
        'license': {
            'name': 'Creative Commons - Attribution',
            'link': 'https://creativecommons.org/licenses/by/4.0/'
        }
    },
    "move_click": {
        'filename': '29275__junggle__btn095.wav',
        'origin': 'https://www.freesound.org/people/junggle/sounds/29275/',
        'creator': 'junggle',
        'license': {
            'name': 'Creative Commons - Attribution',
            'link': 'https://creativecommons.org/licenses/by/4.0/'
        }
    },
    'explosion': {
        'filename': '80401__steveygos93__explosion2.wav',
        'origin': 'http://www.freesound.org/people/steveygos93/sounds/80401/',
        'creator': 'steveygos93',
        'license': {
            'name': 'Creative Commons - Attribution',
            'link': 'https://creativecommons.org/licenses/by/3.0/'
        }
    },
    'you_lose': {
        'filename': '321910__bboyjoe-15__you-lose.wav',
        'origin': 'https://www.freesound.org/people/bboyjoe_15/sounds/321910/',
        'creator': 'bboyjoe_15',
        'license': {
            'name': 'Creative Commons - Attribution',
            'link': 'https://creativecommons.org/licenses/by/3.0/'
        }
    },
    'you_win': {
        'filename': '321917__bboyjoe-15__you-win.wav',
        'origin': 'https://www.freesound.org/people/bboyjoe_15/sounds/321917/',
        'creator': 'bboyjoe_15',
        'license': {
            'name': 'Creative Commons - Attribution',
            'link': 'https://creativecommons.org/licenses/by/3.0/'
        }
    },
}

SAMPLES = None

# Initialize a . addressable collection of playable sound samples
def sound_init():
    global SAMPLES
    attempt_enable()
    disable()
    _d = dict()
    for s in SOUNDS_DATA:
        _d[s] = Sample(s, **SOUNDS_DATA[s])
    SAMPLES = _bunch(**_d)
sound_init()
