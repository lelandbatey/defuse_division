'''
defusedivision
--------------

defusedivision is a terminal based multiplayer (and singleplayer)
implementation of minesweeper.

Your goal is to correctly flag all the mines on the minefield without setting
off any of the mines. By default, the controls are:

    Arrow keys to move your cursor
    'f' key to flag a cell as containing a mine
    'enter' key to probe that cell

If you probe a cell and that cell doesn't contain any mines, then that cell is
revealed and will display a number in the center. That number indicates the
number of mines that are 'touching' that cell, either directly above, below, to
the left or right, or any of the four diagonals. If a cell doesn't contain any
mines, then all surrounding cells without mines are recursively revealed to the
player.

Play minesweeper!
`````````````````

Play minesweeper by launching defusedivision and selecting 'Singleplayer'. Just
like that, you're playing!

'''

from setuptools import setup, find_packages
import ast
import re

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('defusedivision/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

__license__ = 'GPLv3'

setup(
    name='defusedivision',
    version=version,
    url='https://github.com/lelandbatey/defuse_division',
    license=__license__,
    author='Leland Batey',
    author_email='lelandbatey@lelandbatey.com',
    description='Terminal based multiplayer (and singleplayer) minesweeper',
    long_description=__doc__,
    packages=find_packages(),
    install_requires=['zeroconf', 'pygame'],
    include_package_data=True,
    classifiers=[
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'defusedivision=defusedivision.entrypoint:main'
            ]
        }
)
