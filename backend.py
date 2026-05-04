# backend.py
# Monopoly backend logic
# this file handles the actual game rules and data
# the frontend can later call these functions and show the results on screen

import random


# ============================================================
# BOARD SETUP
# ============================================================

# The 40 spaces on a Monopoly board in order
# We use the index as the position number
# 0 = Go, 10 = Jail, 30 = Go To Jail, 39 = Boardwalk
BOARD = [
    "Go", "Mediterranean Ave", "Community Chest", "Baltic Ave", "Income Tax",
    "Reading Railroad", "Oriental Ave", "Chance", "Vermont Ave", "Connecticut Ave",
    "Jail", "St. Charles Place", "Electric Company", "States Ave", "Virginia Ave",
    "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Ave",
    "New York Ave", "Free Parking", "Kentucky Ave", "Chance", "Indiana Ave",
    "Illinois Ave", "B&O Railroad", "Atlantic Ave", "Ventnor Ave", "Water Works",
    "Marvin Gardens", "Go To Jail", "Pacific Ave", "North Carolina Ave",
    "Community Chest", "Pennsylvania Ave", "Short Line Railroad", "Chance",
    "Park Place", "Luxury Tax", "Boardwalk"
]


# ============================================================
# PROPERTY INFO
# ============================================================

# This dictionary stores info for every buyable space
# We are keeping the data simple:
# - price = how much it costs to buy
# - rent = base rent
# - type = property / railroad / utility
# - color = color group for normal properties
#
# For a class project, this is enough backend info to run the game.
# If we wanted full official Monopoly later, we could add houses, hotels,
# mortgage values, house prices, etc.
PROPERTY_DATA = {
    "Mediterranean Ave": {"price": 60, "rent": 2, "type": "property", "color": "brown"},
    "Baltic Ave": {"price": 60, "rent": 4, "type": "property", "color": "brown"},

    "Reading Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None},

    "Oriental Ave": {"price": 100, "rent": 6, "type": "property", "color": "light blue"},
    "Vermont Ave": {"price": 100, "rent": 6, "type": "property", "color": "light blue"},
    "Connecticut Ave": {"price": 120, "rent": 8, "type": "property", "color": "light blue"},

    "St. Charles Place": {"price": 140, "rent": 10, "type": "property", "color": "pink"},
    "Electric Company": {"price": 150, "rent": 10, "type": "utility", "color": None},
    "States Ave": {"price": 140, "rent": 10, "type": "property", "color": "pink"},
    "Virginia Ave": {"price": 160, "rent": 12, "type": "property", "color": "pink"},

    "Pennsylvania Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None},

    "St. James Place": {"price": 180, "rent": 14, "type": "property", "color": "orange"},
    "Tennessee Ave": {"price": 180, "rent": 14, "type": "property", "color": "orange"},
    "New York Ave": {"price": 200, "rent": 16, "type": "property", "color": "orange"},

    "Kentucky Ave": {"price": 220, "rent": 18, "type": "property", "color": "red"},
    "Indiana Ave": {"price": 220, "rent": 18, "type": "property", "color": "red"},
    "Illinois Ave": {"price": 240, "rent": 20, "type": "property", "color": "red"},

    "B&O Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None},

    "Atlantic Ave": {"price": 260, "rent": 22, "type": "property", "color": "yellow"},
    "Ventnor Ave": {"price": 260, "rent": 22, "type": "property", "color": "yellow"},
    "Water Works": {"price": 150, "rent": 10, "type": "utility", "color": None},
    "Marvin Gardens": {"price": 280, "rent": 24, "type": "property", "color": "yellow"},

    "Pacific Ave": {"price": 300, "rent": 26, "type": "property", "color": "green"},
    "North Carolina Ave": {"price": 300, "rent": 26, "type": "property", "color": "green"},
    "Pennsylvania Ave": {"price": 320, "rent": 28, "type": "property", "color": "green"},

    "Short Line Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None},

    "Park Place": {"price": 350, "rent": 35, "type": "property", "color": "dark blue"},
    "Boardwalk": {"price": 400, "rent": 50, "type": "property", "color": "dark blue"}
}


# ============================================================
# CARD DECKS
# ============================================================

# We keep cards simple using dictionaries.
# "type" tells us what the card does.
# Different card types:
# - money: add/subtract money
# - move: move player to a certain board position
# - jail: send player to jail
# - move_relative: move forward/back by some amount

CHANCE_CARDS = [
    {"text": "Advance to Go", "type": "move", "position": 0},
    {"text": "Go to Jail", "type": "jail"},
    {"text": "Bank pays you dividend of $50", "type": "money", "amount": 50},
    {"text": "Pay poor tax of $15", "type": "money", "amount": -15},
    {"text": "Speeding fine $15", "type": "money", "amount": -15},
    {"text": "Your building loan matures, collect $150", "type": "money", "amount": 150},
    {"text": "Advance to Illinois Ave", "type": "move", "position": 24},
    {"text": "Go back 3 spaces", "type": "move_relative", "amount": -3}
]

COMMUNITY_CHEST_CARDS = [
    {"text": "Advance to Go", "type": "move", "position": 0},
    {"text": "Go to Jail", "type": "jail"},
    {"text": "Bank error in your favor, collect $200", "type": "money", "amount": 200},
    {"text": "Doctor's fee, pay $50", "type": "money", "amount": -50},
    {"text": "From sale of stock you get $50", "type": "money", "amount": 50},
    {"text": "Income tax refund, collect $20", "type": "money", "amount": 20},
    {"text": "Pay hospital fees of $100", "type": "money", "amount": -100},
    {"text": "You inherit $100", "type": "money", "amount": 100}
]


# ============================================================
# PLAYER + GAME CREATION
# ============================================================

def create_player(name):
    # each player starts with:
    # - name
    # - $1500
    # - position 0 (Go)
    # - empty property list
    # - jail info
    # - bankrupt flag
    return {
        "name": name,
        "money": 1500,
        "position": 0,
        "properties": [],
        "in_jail": False,
        "jail_turns": 0,
        "bankrupt": False
    }


def create_game(player_names):
    # create all players from a list of names
    players = []
    for name in player_names:
        players.append(create_player(name))

    # property_owners maps property name -> player name
    # example:
    # property_owners["Boardwalk"] = "Alice"
    property_owners = {}

    # chance/community chest decks can be shuffled so card order feels more real
    chance_deck = CHANCE_CARDS[:]
    community_chest_deck = COMMUNITY_CHEST_CARDS[:]
    random.shuffle(chance_deck)
    random.shuffle(community_chest_deck)

    # deck indexes help us go through cards one by one
    game = {
        "players": players,
        "property_owners": property_owners,
        "chance_deck": chance_deck,
        "community_chest_deck": community_chest_deck,
        "chance_index": 0,
        "community_chest_index": 0,
        "turn": 0,
        "log": []
    }

    return game


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_log(game, message):
    # store a message in the game log
    # frontend can later read this and display it however it wants
    game["log"].append(message)

    # also print it for backend testing in the terminal
    print(message)


def find_player_by_name(players, name):
    # loop through players until we find the one with that name
    for player in players:
        if player["name"] == name:
            return player
    return None


def get_space_name(position):
    # helper so we can turn a board index into the actual board space name
    return BOARD[position]


def is_property(space):
    # checks if the space is one of the buyable spaces
    return space in PROPERTY_DATA


def count_active_players(players):
    # active means not bankrupt
    count = 0
    for player in players:
        if not player["bankrupt"]:
            count += 1
    return count


def get_active_players(players):
    active = []
    for player in players:
        if not player["bankrupt"]:
            active.append(player)
    return active


def get_winner(players):
    # if only one player is left not bankrupt, that player wins
    active_players = get_active_players(players)
    if len(active_players) == 1:
        return active_players[0]
    return None


# ============================================================
# MONEY + BANKRUPTCY
# ============================================================

def change_money(player, amount):
    # amount can be positive or negative
    # positive = player gains money
    # negative = player loses money
    player["money"] += amount


def release_properties(player, property_owners):
    # when a player goes bankrupt, their properties go back to unowned
    for prop in player["properties"]:
        if prop in property_owners:
            del property_owners[prop]

    player["properties"] = []


def check_bankruptcy(player, property_owners, game):
    # if money is below 0, player is bankrupt
    # simplified rule: they are immediately out
    if player["money"] < 0 and not player["bankrupt"]:
        player["bankrupt"] = True
        release_properties(player, property_owners)
        add_log(game, f"{player['name']} is bankrupt and out of the game!")


# ============================================================
# JAIL
# ============================================================

def send_player_to_jail(player, game):
    # Jail space is position 10
    player["position"] = 10
    player["in_jail"] = True
    player["jail_turns"] = 0
    add_log(game, f"{player['name']} was sent to Jail!")


def handle_jail_turn(player, game):
    # simple jail rule for our project:
    # - player misses up to 3 turns
    # - after the 3rd missed turn, they pay $50 and leave jail
    #
    # this is a good backend rule because it is easy to follow and easy to code
    player["jail_turns"] += 1

    if player["jail_turns"] < 3:
        add_log(game, f"{player['name']} is in Jail and misses this turn")
        return False

    # after 3 turns in jail, pay $50 and get out
    player["money"] -= 50
    player["in_jail"] = False
    player["jail_turns"] = 0
    add_log(game, f"{player['name']} paid $50 and got out of Jail")
    return True


# ============================================================
# DICE + MOVEMENT
# ============================================================

def roll_dice():
    # roll two normal six-sided dice
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return die1, die2


def move_player(player, steps, game):
    # move a player forward (or backward if steps is negative)
    old_position = player["position"]
    new_position = (old_position + steps) % 40
    player["position"] = new_position

    # if moving forward wraps around the board, player passed Go
    # only do this when steps is positive
    if steps > 0 and new_position < old_position:
        player["money"] += 200
        add_log(game, f"{player['name']} passed Go and collected $200")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}")


def move_player_to(player, new_position, game):
    # move to an exact board position
    old_position = player["position"]
    player["position"] = new_position

    # if player moved from a later space to an earlier one, they passed Go
    # example: from 36 to 0
    if new_position < old_position or new_position == 0:
        player["money"] += 200
        add_log(game, f"{player['name']} moved past Go and collected $200")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}")


# ============================================================
# RENT CALCULATION
# ============================================================

def count_railroads_owned(owner):
    # railroads have special rent rules
    count = 0
    for prop in owner["properties"]:
        if PROPERTY_DATA[prop]["type"] == "railroad":
            count += 1
    return count


def count_utilities_owned(owner):
    # utilities also have their own rule
    count = 0
    for prop in owner["properties"]:
        if PROPERTY_DATA[prop]["type"] == "utility":
            count += 1
    return count


def owner_has_full_color_set(owner, color):
    # checks if owner has every property in a color group
    # used to double base rent if no houses/hotels
    if color is None:
        return False

    color_group = []
    for prop in PROPERTY_DATA:
        if PROPERTY_DATA[prop]["color"] == color:
            color_group.append(prop)

    for prop in color_group:
        if prop not in owner["properties"]:
            return False

    return True


def calculate_rent(space, owner, dice_roll_total):
    # figure out how much rent should be paid based on the type of property
    data = PROPERTY_DATA[space]

    if data["type"] == "property":
        rent = data["rent"]

        # simplified monopoly rule:
        # if someone owns the full color set, base rent doubles
        # only applies because we are not doing houses/hotels yet
        if owner_has_full_color_set(owner, data["color"]):
            rent = rent * 2

        return rent

    elif data["type"] == "railroad":
        # official Monopoly style railroad rent:
        # 1 railroad = 25
        # 2 railroads = 50
        # 3 railroads = 100
        # 4 railroads = 200
        num = count_railroads_owned(owner)
        return 25 * (2 ** (num - 1))

    elif data["type"] == "utility":
        # official-style utility rule uses dice roll
        # 1 utility = 4x dice roll
        # 2 utilities = 10x dice roll
        num = count_utilities_owned(owner)
        if num == 1:
            return 4 * dice_roll_total
        else:
            return 10 * dice_roll_total

    return 0


# ============================================================
# PROPERTY BUYING + RENT
# ============================================================

def buy_property(player, space, game):
    # player buys the property if they have enough money
    price = PROPERTY_DATA[space]["price"]

    if player["money"] >= price:
        player["money"] -= price
        player["properties"].append(space)
        game["property_owners"][space] = player["name"]
        add_log(game, f"{player['name']} bought {space} for ${price}")
        return True

    add_log(game, f"{player['name']} could not afford {space}")
    return False


def pay_rent(player, owner, space, dice_roll_total, game):
    rent = calculate_rent(space, owner, dice_roll_total)

    player["money"] -= rent
    owner["money"] += rent

    add_log(game, f"{player['name']} paid ${rent} rent to {owner['name']} for {space}")


def handle_property_space(player, space, dice_roll_total, game):
    # if nobody owns the property yet, player can buy it
    if space not in game["property_owners"]:
        buy_property(player, space, game)
        return

    owner_name = game["property_owners"][space]

    # if player owns it themselves, nothing happens
    if owner_name == player["name"]:
        add_log(game, f"{player['name']} landed on their own property")
        return

    owner = find_player_by_name(game["players"], owner_name)

    # if owner somehow no longer exists or is bankrupt, do nothing
    if owner is None or owner["bankrupt"]:
        return

    pay_rent(player, owner, space, dice_roll_total, game)


# ============================================================
# CARDS
# ============================================================

def draw_chance_card(game):
    # draw the next card in the deck
    # when we reach the end, reshuffle and start over
    if game["chance_index"] >= len(game["chance_deck"]):
        random.shuffle(game["chance_deck"])
        game["chance_index"] = 0

    card = game["chance_deck"][game["chance_index"]]
    game["chance_index"] += 1
    return card


def draw_community_chest_card(game):
    if game["community_chest_index"] >= len(game["community_chest_deck"]):
        random.shuffle(game["community_chest_deck"])
        game["community_chest_index"] = 0

    card = game["community_chest_deck"][game["community_chest_index"]]
    game["community_chest_index"] += 1
    return card


def handle_card(player, card, game):
    # apply the effect of a Chance or Community Chest card
    add_log(game, f"{player['name']} drew a card: {card['text']}")

    if card["type"] == "money":
        player["money"] += card["amount"]

        if card["amount"] >= 0:
            add_log(game, f"{player['name']} received ${card['amount']}")
        else:
            add_log(game, f"{player['name']} paid ${-card['amount']}")

    elif card["type"] == "move":
        move_player_to(player, card["position"], game)
        # after moving, the new space should also be handled
        handle_landing(player, 0, game)

    elif card["type"] == "move_relative":
        move_player(player, card["amount"], game)
        handle_landing(player, 0, game)

    elif card["type"] == "jail":
        send_player_to_jail(player, game)


# ============================================================
# LANDING ON SPACES
# ============================================================

def handle_landing(player, dice_roll_total, game):
    # this function handles what happens after a player lands somewhere
    space = BOARD[player["position"]]

    # Go usually does nothing special when landed on directly
    if space == "Go":
        add_log(game, f"{player['name']} landed on Go")

    elif space == "Income Tax":
        player["money"] -= 200
        add_log(game, f"{player['name']} paid $200 Income Tax")

    elif space == "Luxury Tax":
        player["money"] -= 100
        add_log(game, f"{player['name']} paid $100 Luxury Tax")

    elif space == "Free Parking":
        add_log(game, f"{player['name']} landed on Free Parking")

    elif space == "Jail":
        add_log(game, f"{player['name']} is just visiting Jail")

    elif space == "Go To Jail":
        send_player_to_jail(player, game)

    elif space == "Chance":
        card = draw_chance_card(game)
        handle_card(player, card, game)

    elif space == "Community Chest":
        card = draw_community_chest_card(game)
        handle_card(player, card, game)

    elif is_property(space):
        handle_property_space(player, space, dice_roll_total, game)

    # always check bankruptcy after landing
    check_bankruptcy(player, game["property_owners"], game)


# ============================================================
# TAKING A TURN
# ============================================================

def take_turn(game):
    # this handles one player's full turn
    players = game["players"]

    # find which player's turn it is
    current_index = game["turn"] % len(players)
    player = players[current_index]

    # if player is bankrupt, skip them
    if player["bankrupt"]:
        game["turn"] += 1
        return

    add_log(game, "")
    add_log(game, f"--- {player['name']}'s turn ---")

    # if player is in jail, deal with jail first
    if player["in_jail"]:
        can_move = handle_jail_turn(player, game)

        # if they are still in jail after that, turn ends
        if not can_move:
            game["turn"] += 1
            return

        # if they got out, they continue and roll normally

    # roll dice
    die1, die2 = roll_dice()
    total = die1 + die2

    add_log(game, f"{player['name']} rolled {die1} and {die2} for a total of {total}")

    # move player forward
    move_player(player, total, game)

    # handle whatever space they landed on
    handle_landing(player, total, game)

    # simplified doubles rule:
    # if doubles are rolled, give one extra turn
    # but if player was sent to jail during the turn, no extra turn
    if die1 == die2 and not player["bankrupt"] and not player["in_jail"]:
        add_log(game, f"{player['name']} rolled doubles and gets another turn!")
    else:
        game["turn"] += 1


# ============================================================
# GAME STATE / FRONTEND HOOKS
# ============================================================

def get_game_state(game):
    # this returns a clean summary of the current game
    # frontend can use this without needing to understand all backend internals
    players_summary = []

    for player in game["players"]:
        players_summary.append({
            "name": player["name"],
            "money": player["money"],
            "position": player["position"],
            "space": BOARD[player["position"]],
            "properties": player["properties"][:],
            "in_jail": player["in_jail"],
            "jail_turns": player["jail_turns"],
            "bankrupt": player["bankrupt"]
        })

    state = {
        "players": players_summary,
        "property_owners": game["property_owners"].copy(),
        "turn": game["turn"],
        "current_player": game["players"][game["turn"] % len(game["players"])]["name"],
        "winner": None,
        "log": game["log"][:]
    }

    winner = get_winner(game["players"])
    if winner is not None:
        state["winner"] = winner["name"]

    return state


def print_player_status(game):
    # useful for terminal testing before frontend is connected
    print("\nCurrent status:")
    for player in game["players"]:
        print(
            f"{player['name']}: "
            f"${player['money']}, "
            f"position {player['position']} ({BOARD[player['position']]}), "
            f"properties = {player['properties']}, "
            f"in_jail = {player['in_jail']}, "
            f"bankrupt = {player['bankrupt']}"
        )
    print()


# ============================================================
# FULL GAME LOOP FOR TESTING
# ============================================================

def play_game(player_names, max_turns=200):
    # this loop is mainly for testing the backend by itself
    # once the frontend is connected, it probably will not use this exact loop
    game = create_game(player_names)

    add_log(game, "Starting Monopoly game!")

    for _ in range(max_turns):
        winner = get_winner(game["players"])
        if winner is not None:
            add_log(game, f"{winner['name']} wins the game!")
            return game

        take_turn(game)

    # if game reaches max turns, winner is whoever has most money
    richest = None
    for player in game["players"]:
        if not player["bankrupt"]:
            if richest is None or player["money"] > richest["money"]:
                richest = player

    if richest is not None:
        add_log(game, f"Game reached max turns. {richest['name']} wins by highest money!")

    return game


# ============================================================
# TEST RUN
# ============================================================

# this is just here so we can run backend.py directly and make sure it works
# when frontend gets connected, the frontend will probably call create_game(),
# take_turn(), and get_game_state() instead
if __name__ == "__main__":
    game = play_game(["Alice", "Bob", "Charlie"], max_turns=100)
    print_player_status(game)
