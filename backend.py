# backend.py (Monopoly logic)
# TODO: add property buying, rent, jail, and card drawing

import random

# The 40 spaces on a Monopoly board in order
# We use the index as the position number (0 = Go, 39 = Boardwalk)
BOARD = ["Go", "Mediterranean Ave", "Community Chest", "Baltic Ave", "Income Tax",
         "Reading Railroad", "Oriental Ave", "Chance", "Vermont Ave", "Connecticut Ave",
         "Jail", "St. Charles Place", "Electric Company", "States Ave", "Virginia Ave",
         "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Ave",
         "New York Ave", "Free Parking", "Kentucky Ave", "Chance", "Indiana Ave",
         "Illinois Ave", "B&O Railroad", "Atlantic Ave", "Ventnor Ave", "Water Works",
         "Marvin Gardens", "Go To Jail", "Pacific Ave", "North Carolina Ave",
         "Community Chest", "Pennsylvania Ave", "Short Line Railroad", "Chance",
         "Park Place", "Luxury Tax", "Boardwalk"]

def create_player(name):
    # each player starts with $1500 and on Go (position 0)
    # stored as a dictionary so we can easily add more fields later
    # TODO: add properties list, jail status, bankrupt status
    return {"name": name, "money": 1500, "position": 0}

def take_turn(player):
    # roll two six-sided dice and add them together (same as real Monopoly)
    roll = random.randint(1,6) + random.randint(1,6)

    old_position = player["position"]

    # % 40 wraps the position around the board back to Go
    # e.g. position 38 + roll 5 = 43 % 40 = 3
    player["position"] = (old_position + roll) % 40

    # if new position is less than old position, player wrapped around and passed Go
    if player["position"] < old_position:
        player["money"] += 200  # collect $200 for passing Go
        print(f"  {player['name']} passed Go! Collects $200")

    # look up the space name using the position as an index into BOARD list
    space = BOARD[player["position"]]
    print(f"  {player['name']} rolled {roll}, landed on {space}, has ${player['money']}")

    # TODO: handle special spaces (taxes, jail, cards, properties)
