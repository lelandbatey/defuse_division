
Defuse Division
===============

Defuse Division is a real-time competitive multiplayer implementation of the
game Minesweeper that you can play in your terminal. Defuse Division is written
entirely in Python3.

.. image:: ./defusedivision_uiexample00.gif

.. contents:: Table of Contents
   :backlinks: none

Installation
============

Install with Pip
----------------

To install and play, run:

    pip install defusedivision
    defusedivision # Starts the game

Play from source
----------------

Alternatively, you can clone this repository and run the ``play-defusedivision``
file in this repository (which works in the same way as the ``defusedivision``
command which is installed when you install via pip):::

    git clone "https://github.com/lelandbatey/defuse_division"
    cd defuse_division
    ./play-defusedivision


Multiplayer
===========

If you want to play head to head against multiple people, you have two options:

Run a dedicated server
----------------------

You can run a dedicated server with the command:::

    defusedivision --serveronly

This will launch a dedicated DefuseDivision server on port 44444. You can
customize the port and interface with the ``--port`` and ``--host`` command line
arguments.

Host a server while playing
---------------------------

You can play and host a server for other people to play on by selecting the
option in the main menu labeled 'Host and play'. This will launch a game server
on port 44444 on your machine exposed on all interfaces and connect to that
server. This server will also use Zeroconf/mDNS to advertise itself on the
local network, so other people on the same network as you will see your server
in the box labeled 'Local Servers' under the 'Multiplayer' menu.

Prerequisites
=============

DefuseDivision is a terminal based game leveraging some semi-specialized
features of terminal emulators. Some terminal emulators don't support the
necessary features, and will break or not run. For example, ``PuTTY`` on Windows
works very poorly with this game.

The actual requirements are:

- Unicode support
    - Specialized unicode characters are used to draw certain elements of the game, and will display as missing characters like "�" or "□" if your terminal doesn't support them
- Color terminal support
    - If your terminal doesn't support colors, hopefully it will display an error explaining what's happened, but the game may simply crash or refuse to run.

Environments known to work with the base game (without sound)
-------------------------------------------------------------

I've tested DefuseDivision on the following platforms/terminal emulators and found them to work with the base game:

===================  =======================  =============================
Operating System     Terminal Emulator        ``TERM`` Environment Variable
===================  =======================  =============================
Ubuntu 16.04.1 LTS   rxvt-unicode-256color    rxvt-unicode-256color
Ubuntu 16.04.1 LTS   gnome-terminal           xterm-256color
Ubuntu 16.04.1 LTS   xfce4-terminal           xterm-256color
===================  =======================  =============================

Getting sound to work
---------------------

DefuseDivision can try to play sounds with the ``--withsound`` command line
argument. Sound is played through the ``pygame`` library, if it is installed. If
``pygame`` is not installed, sound will not be played, even if the ``--withsound``
argument is passed.

On my Linux installation, to enable playing sound through ``pygame``, I had to
set the environment variable ``SDL_AUDIODRIVER`` to the value ``alsa``, and that is
hardcoded in the ``defusedivision/sound/sound.py`` file. If sound is not working,
or sound is playing very erratically (such as crackling, static-like crunching
noises while audio plays), you may try fiddling with that environment variable.

Sound has not been tested on any system other than Linux.


