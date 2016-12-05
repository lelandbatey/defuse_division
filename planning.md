
Planning
========

Here's the rough plan for developing defuse division. Given the following calendar:

       November 2016      
    Su Mo Tu We Th Fr Sa  
           1  2  3  4  5  
     6  7  8  9 10 11 12  
    13 14 15 16 17 18 19  
    20 21 22 23 24 25 26  
    27 28 29 30 

       December 2016      
    Su Mo Tu We Th Fr Sa  
                 1  2  3  
     4  5  6  7  8  9 10  
     ..remainder ommited..

## Milestones

I have from today, November 2nd, till December 9th to complete and turn in
Defuse Division. Here is a rough development schedule:

| Milestone | Date          |
|-----------|---------------|
| Alpha     | November 6th  |
| Beta      | November 13th |
| Gamma     | November 20th |
| Delta     | November 27th |
| Epsilon   | December 4th  |

Note that all of those days are Sundays, with the goal being to complete the
project with 5 days to spare.

### Definitions

1. Alpha
    - A singleplayer minesweeper implementation, using curses for the keyboard events
    - The skeleton of a server and client, with them able to talk to each other over the network, though the messaging schema will probably not be defined/implemented
2. Beta
    - The singleplayer minesweeper implementation, but with a terminal client and game logic separated so the termclient displays while the server handles game logic.
        - Basic communication schema has been defined, but is limited to talking about player1
    - A menu on startup allowing the user to select singleplayer, with a fake button for multiplayer, and the ability to modify game settings
        - Curses UI has been at least partially written. The "front-page" of the UI is written in curses, and is interactable, leading to other views/interactive modes
3. Gamma
    - Multiplayer games may be played, though a hostname/port combo is required for connection
        - Full game communication is implemented, clients and servers communication protocol and conventions are totally implemented.
    - Some basic sounds are played on certain actions, such as detonating a bomb
        - A simple event and concurrent audio playback. No need (yet) for a syncronous audio system, such as for playing background music.
4. Delta
    - Multiplayer games may be started by selecting other hosts from the game server list
        - Zeroconf discovery must be completed
    - Audio is played on all required events
5. Epsilon
    - Configuration flags for all various parameters are present
    - TURN IT IN!


# BUG plans:

Currently, there's an unsolvable bug that only rarely occurs where the screen
may be corrupted because multiple threads call the `refresh()` method of stdscr
at the same time. I've mitigated it using thread locks, but it's still possible
just less likely. It can be reproduced by holding down an arrow key on the main
menu, which should cause screen corruption within 60 seconds. "Normally"
pressing arrow keys will pretty much never cause corruption.

This happens because while one thread is calling 'refresh', another may call
'getch', and `getch` calls `refresh` before waiting for input. However, `pads`,
which are almost exactly like windows, don't cause `refresh` when `getch` is
called. Thus, I may be able to 'fake' stdscr by having a stdscr-sized pad that
acts like stdscr.

Another alternative may be to separately read from stdin (manually, outside of
curses) and wait for new input, then use locks to call `getch` from curses.
Whether this works or not I don't know.

