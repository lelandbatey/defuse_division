
Defuse Division -- Design Thoughts
==================================

What are the requirements:

1. It is a real-time competitive multiplayer (optionally single player) minesweeper, displayed in the terminal with communication over the network, with sounds that play when events occur (such as player movement, tripping a mine, winning, losing, etc), and a menu for selecting hosts to play against.
	- Real-time means that it's not a turn based style of playing minesweeper, the player plays as fast or as slow as they choose, with their input immediately changing the state of the game
	- Competitive means that you are playing a "vs" match, where you're trying to solve the board before the other player.
	- Multiplayer and over the network means that the game is not played locally, it is played using clients that connect to a server over the network. Optionally, it may be used to play by oneself.
	- Sounds must be played by the client when certain events occur. For example, when the game starts, it should play some audio clip for the game starting. If a player detonates a mine, then that will cause a sound to be played.
	- A menu means that when the game is launched, there must be an interactive menu for a user to select whether to connect to a game or host a game, with a list of other games on the network (if there are any).


Architecture Thoughts
---------------------

There will be a client and a server program/module. However, both the client
and server will be contained within a single executable, so one can launch
either the client or server with a different flags to the same executable.
E.g.:

	defuse_division # launches client
	defuse_division --server-only # launches the server only

Additionally, both a server may be launched (in a non-printing daemonized mode)
by the client if the client chooses to "host a game" or chooses "single
player".

### Module Layout

As a result, defuse division will probably be broken into some kind of
structure like the following:

- Game
	- Server
	- Client
- Terminal client


### Operational Relationships

While running, there will be a variety of different possible relationships
between the executing components:

#### Singleplayer

- Terminal client
	- Game.Client
	- Game.Server

#### Multiplayer, host-and-play

- Terminal client
	- Game.Client
	- Game.Server

#### Multiplayer, playing on some other host

- Terminal client
	- Game.Client

#### Hosting a server exclusively

This could run with a game server and no terminal client, just the game server directly:

- Game.Server

Or it could be that the game server runs beneath a terminal client:

- Terminal client
	- Game.Server


User Stories
------------

1. As a player, I launch the game and am presented with a menu where I can choose singleplayer, or multiplayer.
2. As a player, when I select "single player", I am immediately dropped into a single player game of minesweeper.
3. As a player, when I select "multiplayer" the menu changes to a new menu where I can select either an already running game on the network, or type in a hostname/port combo for a remote server, or select "Host and Play"
4. As a player, when I choose "host and play" under "Multiplayer", I am dropped into a waiting screen till another player chooses to join my game.
5. As a player, when I select "Multiplayer" and another player is already waiting at "host and play" on the same network as me, I will see their host in the list of games I may choose to join.

### Playing on a dedicated server:

The default state for a minesweeper server is to create a new bout. The default
state for a bout is to wait for players to connect. When a player connects, the
bout checks if the number of players currently registered is the correct
number, and if it is, then the bout moves into the 'playing' state.

In the playing state, actions are sent from each player to the server. During
the processing of each action, the server evaluates whether that action results
in a play-terminating game state. If a play-terminating game state is reached,
the server categorizes each player as victorious or defeated and sends this
message to each player. After sending the message indicating a play-terminating
state and its outcomes, the bout is ended, players are disconnected, and the
server creates a new bout and enters the default state.


Sound Sources
-------------

For my sounds, I plan to use the sounds on Freesound.org, specifically the same source of sounds that Notch used when creating Minecraft, this user: https://www.freesound.org/people/junggle/sounds/?page=27#sound

Also, here's possible source for into music: http://opengameart.org/content/generic-8-bit-jrpg-soundtrack

I'll have to remember to include attribution to all of these sounds, as they use the CC-Attribution license.

