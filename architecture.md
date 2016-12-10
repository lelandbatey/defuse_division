


## How does this work, in conceptual form?

It works like how this diagram shows it works:

                         User input
        .----<------------------------------<--\
        |                                       \
        v                                        \
    Game logic                                Send-input & update
    event loop                                display event loop
        |                                         ^
         \                                       /
          `--->-------------------------->------'
                      New world states

The 'pipes' that are connecting the `input/display` event loop with the `game
logic` event loop could be pretty much anything. If everything where happening
on one computer, they could just be queue data structures. If we want to extend
this over the network, then the pipes could be tcp sockets with little
reader/writers shuttling things from the queues over the network. That way, the
event loops don't even have to be aware that things are happening over the
network.

And basically, that's how I chose to implement things! This "pair of
bi-directional channels" interface is outlined in the
`defusedivision.game.Conveyor` object, an abstract class which has just two
methods:

	send_input(input) -> None
	get_state() -> state


# Inputs to the Game loop

Valid inputs that the client can send are:

	# Send a movement or action to the game
	"RIGHT" or "LEFT" or "UP" or "DOWN"
	or "PROBE" or "FLAG"

	# Change the name of my player (sent in json form)
	{"change-name": "NEW_NAME_GOES_HERE"}

	# Create a new minefield for this player (sent in json form)
	{
		"new-minefield": {
			"height": 16, # Must be some number
			"width": 16,
			"mine_count": null, # May be any number greater than zero, or null to default to a 'decent amount'
		}
	}

And that's it. The client have relatively little they're allowed to change.

# Outputs of the Game loop

The game loop may respond with only two different types of messages. One is far
more complex than the other, so I'll start with the simpler:

	# Update the selected mine of a player
	["update-selected", ["PLAYER_NAME_HERE", [1, 0]]]

	# Update the entire state of the world:
	[
		"new-state",
		{
			"ready": true,
			"players": {
				"PLAYER1": {
					"name": "PLAYER1"
					"living": true,
					"minefield": {
					"height": 16,
					"width": 16,
					"mine_count": 38,
					"selected": [0, 0],
					"victory": false,
					"cells": [
							{
								"contents": "   ",
								"y": 0,
								"x": 0,
								"probed": False,
								"neighbors": {"N": None,
									"NW": None,
									"W": None,
									"SW": None,
									"E": False,
									"NE": None,
									"SE": False,
									"S": False
								},
								"flagged": False
							},
							# Other cells omitted
						],
					},
				},
			},
		}
	]


