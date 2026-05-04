# backend/game.py
# Main Monopoly game engine.
# Handles turns, dice, movement, rent, buying, cards, jail, houses, and game state.

import random

from backend.board import BOARD, PROPERTY_DATA, is_property, get_color_group
from backend.player import create_player, find_player_by_name, get_winner
from backend.cards import (
    CHANCE_CARDS,
    COMMUNITY_CHEST_CARDS,
    draw_chance_card,
    draw_community_chest_card
)


# ============================================================
# GAME CREATION
# ============================================================

def create_game(player_names):
    """Create a new game."""

    players = [create_player(name) for name in player_names]

    chance_deck = CHANCE_CARDS[:]
    community_chest_deck = COMMUNITY_CHEST_CARDS[:]

    random.shuffle(chance_deck)
    random.shuffle(community_chest_deck)

    return {
        "players": players,
        "property_owners": {},
        "houses": {prop: 0 for prop in PROPERTY_DATA},
        "chance_deck": chance_deck,
        "community_chest_deck": community_chest_deck,
        "chance_index": 0,
        "community_chest_index": 0,
        "turn": 0,
        "log": [],
        "pending_action": None,
        "has_rolled": False,
        "last_roll": None,
        "current_card": None
    }


def add_log(game, message):
    """Add message to log."""
    game["log"].append(message)
    print(message)


def get_current_player(game):
    """Return the current player."""
    return game["players"][game["turn"] % len(game["players"])]


# ============================================================
# MONEY + BANKRUPTCY
# ============================================================

def change_money(player, amount):
    """Change player money."""
    player["money"] += amount


def release_properties(player, game):
    """Release properties when player goes bankrupt."""
    for prop in player["properties"]:
        if prop in game["property_owners"]:
            del game["property_owners"][prop]

        if prop in game["houses"]:
            game["houses"][prop] = 0

    player["properties"] = []


def check_bankruptcy(player, game):
    """Mark player bankrupt if money below zero."""
    if player["money"] < 0 and not player["bankrupt"]:
        player["bankrupt"] = True
        release_properties(player, game)
        add_log(game, f"{player['name']} is bankrupt and out of the game!")


# ============================================================
# JAIL
# ============================================================

def send_player_to_jail(player, game):
    """Send player to jail."""
    player["position"] = 10
    player["in_jail"] = True
    player["jail_turns"] = 0
    add_log(game, f"{player['name']} was sent to Jail!")


def handle_jail_turn(player, game):
    """
    Simplified jail rule:
    Player misses two turns, then pays $50 and leaves.
    """

    player["jail_turns"] += 1

    if player["jail_turns"] < 3:
        add_log(game, f"{player['name']} is in Jail and misses this turn.")
        return False

    player["money"] -= 50
    player["in_jail"] = False
    player["jail_turns"] = 0

    add_log(game, f"{player['name']} paid $50 and got out of Jail.")
    check_bankruptcy(player, game)
    return True


# ============================================================
# DICE + MOVEMENT
# ============================================================

def roll_dice():
    """Roll two dice."""
    return random.randint(1, 6), random.randint(1, 6)


def move_player(player, steps, game):
    """Move player around the board."""
    old_position = player["position"]
    new_position = (old_position + steps) % 40

    player["position"] = new_position

    if steps > 0 and new_position < old_position:
        player["money"] += 200
        add_log(game, f"{player['name']} passed Go and collected $200.")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}.")


def move_player_to(player, new_position, game):
    """Move player directly to a board position."""
    old_position = player["position"]
    player["position"] = new_position

    if new_position < old_position or new_position == 0:
        player["money"] += 200
        add_log(game, f"{player['name']} moved past Go and collected $200.")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}.")


# ============================================================
# RENT + OWNERSHIP
# ============================================================

def count_railroads_owned(owner):
    """Count railroads owned."""
    return sum(
        1 for prop in owner["properties"]
        if PROPERTY_DATA[prop]["type"] == "railroad"
    )


def count_utilities_owned(owner):
    """Count utilities owned."""
    return sum(
        1 for prop in owner["properties"]
        if PROPERTY_DATA[prop]["type"] == "utility"
    )


def owner_has_full_color_set(owner, color):
    """Check if owner owns all properties in a color group."""
    if color is None:
        return False

    group = get_color_group(color)

    for prop in group:
        if prop not in owner["properties"]:
            return False

    return True


def calculate_rent(space, owner, dice_roll_total, game):
    """Calculate rent based on property type and houses."""

    data = PROPERTY_DATA[space]

    if data["type"] == "property":
        rent = data["rent"]

        if owner_has_full_color_set(owner, data["color"]):
            rent *= 2

        house_count = game["houses"].get(space, 0)

        if house_count > 0:
            rent += data["rent"] * house_count * 2

        return rent

    if data["type"] == "railroad":
        count = count_railroads_owned(owner)
        return 25 * (2 ** (count - 1))

    if data["type"] == "utility":
        count = count_utilities_owned(owner)

        if count == 1:
            return 4 * dice_roll_total

        return 10 * dice_roll_total

    return 0


# ============================================================
# PROPERTY BUYING
# ============================================================

def buy_property(player, space, game):
    """Buy property if affordable."""

    price = PROPERTY_DATA[space]["price"]

    if player["money"] < price:
        add_log(game, f"{player['name']} cannot afford {space}.")
        return False

    player["money"] -= price
    player["properties"].append(space)
    game["property_owners"][space] = player["name"]

    add_log(game, f"{player['name']} bought {space} for ${price}.")
    return True


def choose_buy_property(game):
    """Resolve pending Buy action from frontend."""

    action = game.get("pending_action")

    if action is None or action["type"] != "buy_property":
        add_log(game, "There is no property to buy right now.")
        return False

    player = find_player_by_name(game["players"], action["player"])
    space = action["property"]

    bought = buy_property(player, space, game)
    game["pending_action"] = None

    check_bankruptcy(player, game)
    return bought


def choose_skip_property(game):
    """Resolve pending Skip action from frontend."""

    action = game.get("pending_action")

    if action is None or action["type"] != "buy_property":
        add_log(game, "There is no property to skip right now.")
        return False

    add_log(game, f"{action['player']} skipped buying {action['property']}.")
    game["pending_action"] = None
    return True


# ============================================================
# HOUSES
# ============================================================

def can_buy_house(player, property_name, game):
    """Check if current player can buy a house on a property."""

    if property_name not in player["properties"]:
        return False

    data = PROPERTY_DATA[property_name]

    if data["type"] != "property":
        return False

    color = data["color"]

    if not owner_has_full_color_set(player, color):
        return False

    if game["houses"].get(property_name, 0) >= 4:
        return False

    return True


def buy_house(game, property_name):
    """
    Buy one house on a property.
    Frontend can call this when player chooses a property to improve.
    """

    player = get_current_player(game)

    if not can_buy_house(player, property_name, game):
        add_log(game, "You need to own the full color set before buying a house.")
        return False

    cost = PROPERTY_DATA[property_name]["house_cost"]

    if player["money"] < cost:
        add_log(game, f"{player['name']} cannot afford a house on {property_name}.")
        return False

    player["money"] -= cost
    game["houses"][property_name] += 1

    add_log(game, f"{player['name']} bought a house on {property_name} for ${cost}.")
    return True


def get_buildable_properties(game):
    """Return properties the current player can build houses on."""

    player = get_current_player(game)

    buildable = []

    for prop in player["properties"]:
        if can_buy_house(player, prop, game):
            buildable.append(prop)

    return buildable


# ============================================================
# RENT PAYMENT
# ============================================================

def pay_rent(player, owner, space, dice_roll_total, game):
    """Pay rent to owner."""

    rent = calculate_rent(space, owner, dice_roll_total, game)

    player["money"] -= rent
    owner["money"] += rent

    add_log(game, f"{player['name']} paid ${rent} rent to {owner['name']} for {space}.")
    check_bankruptcy(player, game)


def handle_property_space(player, space, dice_roll_total, game):
    """Handle landing on property."""

    if space not in game["property_owners"]:
        game["pending_action"] = {
            "type": "buy_property",
            "player": player["name"],
            "property": space,
            "price": PROPERTY_DATA[space]["price"]
        }

        add_log(game, f"{space} is available for ${PROPERTY_DATA[space]['price']}.")
        return

    owner_name = game["property_owners"][space]

    if owner_name == player["name"]:
        add_log(game, f"{player['name']} landed on their own property.")
        return

    owner = find_player_by_name(game["players"], owner_name)

    if owner is None or owner["bankrupt"]:
        return

    pay_rent(player, owner, space, dice_roll_total, game)


# ============================================================
# CARDS
# ============================================================

def handle_card(player, card, game):
    """Apply Chance or Community Chest card."""

    game["current_card"] = card
    add_log(game, f"{player['name']} drew a card: {card['text']}")

    if card["type"] == "money":
        player["money"] += card["amount"]

        if card["amount"] >= 0:
            add_log(game, f"{player['name']} received ${card['amount']}.")
        else:
            add_log(game, f"{player['name']} paid ${-card['amount']}.")

    elif card["type"] == "move":
        move_player_to(player, card["position"], game)
        handle_landing(player, 0, game)

    elif card["type"] == "move_relative":
        move_player(player, card["amount"], game)
        handle_landing(player, 0, game)

    elif card["type"] == "jail":
        send_player_to_jail(player, game)

    check_bankruptcy(player, game)


# ============================================================
# LANDING
# ============================================================

def handle_landing(player, dice_roll_total, game):
    """Handle space landed on."""

    space = BOARD[player["position"]]

    if space == "Go":
        add_log(game, f"{player['name']} landed on Go.")

    elif space == "Income Tax":
        player["money"] -= 200
        add_log(game, f"{player['name']} paid $200 Income Tax.")

    elif space == "Luxury Tax":
        player["money"] -= 100
        add_log(game, f"{player['name']} paid $100 Luxury Tax.")

    elif space == "Free Parking":
        add_log(game, f"{player['name']} landed on Free Parking.")

    elif space == "Jail":
        add_log(game, f"{player['name']} is just visiting Jail.")

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

    check_bankruptcy(player, game)


# ============================================================
# TURN FLOW
# ============================================================

def roll_current_player(game):
    """Frontend calls this when Roll Dice button is clicked."""

    if game["pending_action"] is not None:
        add_log(game, "Choose Buy or Skip before rolling again.")
        return False

    if game["has_rolled"]:
        add_log(game, "You already rolled. End your turn.")
        return False

    game["current_card"] = None

    player = get_current_player(game)

    if player["bankrupt"]:
        end_turn(game)
        return False

    add_log(game, "")
    add_log(game, f"--- {player['name']}'s turn ---")

    if player["in_jail"]:
        can_move = handle_jail_turn(player, game)

        if not can_move:
            game["has_rolled"] = True
            return True

    die1, die2 = roll_dice()
    total = die1 + die2

    game["last_roll"] = (die1, die2)

    add_log(game, f"{player['name']} rolled {die1} and {die2} for a total of {total}.")

    move_player(player, total, game)
    handle_landing(player, total, game)

    game["has_rolled"] = True
    return True


def end_turn(game):
    """Frontend calls this when End Turn is clicked."""

    if game["pending_action"] is not None:
        add_log(game, "You must Buy or Skip before ending your turn.")
        return False

    game["turn"] += 1
    game["has_rolled"] = False
    game["last_roll"] = None
    game["current_card"] = None

    return True


def take_turn(game):
    """Automatic backend test turn."""

    roll_current_player(game)

    if game["pending_action"] is not None:
        choose_buy_property(game)

    end_turn(game)


# ============================================================
# GAME STATE
# ============================================================

def get_game_state(game):
    """Return frontend-friendly state."""

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

    winner = get_winner(game["players"])

    return {
        "players": players_summary,
        "property_owners": game["property_owners"].copy(),
        "houses": game["houses"].copy(),
        "buildable_properties": get_buildable_properties(game),
        "turn": game["turn"],
        "current_player": get_current_player(game)["name"],
        "winner": winner["name"] if winner else None,
        "log": game["log"][:],
        "pending_action": game.get("pending_action"),
        "has_rolled": game["has_rolled"],
        "last_roll": game["last_roll"],
        "current_card": game["current_card"]
    }


# ============================================================
# TEST MODE
# ============================================================

def play_game(player_names, max_turns=200):
    """Run automatic simulation for backend testing."""

    game = create_game(player_names)

    for _ in range(max_turns):
        if get_winner(game["players"]):
            break

        take_turn(game)

    return game


if __name__ == "__main__":
    play_game(["Alice", "Bob"], max_turns=50)