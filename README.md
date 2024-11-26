This is a simple War Card Game game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script. Args: -p (server port)
2. **Connect clients:** Run the `client.py` script on two different machines or terminals. Args: -i (server IP) -p (server port)
3. **Play the game:** Players take turns flipping over the top card of thier deck. Players can "slap the deck" when a rule is met, ie: two cards of same rank in a row (doubles) or two cards of same rank are seperated by one and only one card (sandwitch).
4. **Chat with opponet:** Type a message in the text box above the 'send' button, when ready click the 'send' button to send your message to the other player

**Current active slap rules:**
1. **Two in a row**
2. **Sandwitch** (two cards of the same rank are seperated by one and only one card)

If a player plays a face card then the other player must play the corresponding number of cards in response:
Jack - 1 card
Queen - 2 cards
King - 3 cards
Ace - 4 cards

The game is over when one player has earned all of the cards in the deck and the other player has no more cards to play

**Technologies used:**
* Python
* Sockets

# Project Title: War Card Game

## Team:
- Ben Palmer

## Project Objectives
The objective of this project is to develop a multiplayer card game, based on the classic game "War." The game will support at least two players and one server for interaction, with a web UI to display the game's state and progress.

## Scope
The scope of this project is focused on implementing a two-player version of the game. Although the original game can accomodate more players, this version will only support two. If time permits, multiplayer functionality may be expanded. 

## Inclusions:
- A web-based UI to display the current card stack and the next card to be played.
- A random card shuffling mechanism to ensure each game session is unique.
- Rules to determine when a valid slap has been made

## Deliverables:
- The project will be delivered in several sprints, each focusing on a specific aspect of the game.
- By the end of development, the deliverable will include a Python-based program for both the clients and the server. 

## Timline and Key Milestones:
- **Sprint 0**: Set up tools and submit Statement of Work
- **Sprint 1**: Implement socket communication and establish TCP client-server interaction.
- **Sprint 2**: Design and implement the message protocol.
- **Sprint 3**: Add multiplayer support and syncronize game states.
- **Sprint 4**: Develop game play functionality and design user interface.
- **Sprint 5**: Implement error handling and conduct testing.

## Technical Requirements:

### Hardware: 
- 3 Linux machines from the CS lab.

### Software: 
- Python
- Socket library
- Pydealer library
- re library (regex)

## Assumptions:
- Due to potential network latency, perfect synchronization may not be available during game play. In cases where a player "slaps" the deck but experinces network delays, the system may incorrectly register the other player as the winner of the round. This issue will be reduced by the "tick" timing system but cannot be fully eliminated.