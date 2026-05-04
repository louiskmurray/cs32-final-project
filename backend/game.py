# backend/game.py
# This file is the main Monopoly game engine.
# It controls turns, dice, movement, buying, rent, cards, jail, bankruptcy, and game state.

import random

from backend.board import BOARD, PROPERTY_DATA, is_property
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
    """Create a new Monopoly game."""

    players = [create_player(name) for name in player_names]

    chance_deck = CHANCE_CARDS[:]
    community_chest_deck = COMMUNITY_CHEST_CARDS[:]

    random.shuffle(chance_deck)
    random.shuffle(community_chest_deck)

    return {
        "players": players,
        "property_owners": {},
        "chance_deck": chance_deck,
        "community_chest_deck": community_chest_deck,
        "chance_index": 0,
        "community_chest_index": 0,
        "turn": 0,
        "log": [],
        "pending_action": None,
        "has_rolled": False,
        "last_roll": None
    }


def add_log(game, message):
    """Add a message to the game log."""
    game["log"].append(message)
    print(message)


# ============================================================
# MONEY + BANKRUPTCY
# ============================================================

def change_money(player, amount):
    """Add or subtract money from a player."""
    player["money"] += amount


def release_properties(player, property_owners):
    """Release all properties owned by a bankrupt player."""
    for prop in player["properties"]:
        if prop in property_owners:
            del property_owners[prop]

    player["properties"] = []


def check_bankruptcy(player, property_owners, game):
    """Check if a player should be bankrupt."""
    if player["money"] < 0 and not player["bankrupt"]:
        player["bankrupt"] = True
        release_properties(player, property_owners)
        add_log(game, f"{player['name']} is bankrupt and out of the game!")


# ============================================================
# JAIL
# ============================================================

def send_player_to_jail(player, game):
    """Send a player to jail."""
    player["position"] = 10
    player["in_jail"] = True
    player["jail_turns"] = 0
    add_log(game, f"{player['name']} was sent to Jail!")


def handle_jail_turn(player, game):
    """
    Simplified jail rule:
    The player misses two turns.
    On the third jail turn, they pay $50 and leave jail.
    """
    player["jail_turns"] += 1

    if player["jail_turns"] < 3:
        add_log(game, f"{player['name']} is in Jail and misses this turn")
        return False

    player["money"] -= 50
    player["in_jail"] = False
    player["jail_turns"] = 0
    add_log(game, f"{player['name']} paid $50 and got out of Jail")
    return True


# ============================================================
# DICE + MOVEMENT
# ============================================================

def roll_dice():
    """Roll two dice."""
    return random.randint(1, 6), random.randint(1, 6)


def move_player(player, steps, game):
    """Move a player forward around the board."""
    old_position = player["position"]
    new_position = (old_position + steps) % 40
    player["position"] = new_position

    if steps > 0 and new_position < old_position:
        player["money"] += 200
        add_log(game, f"{player['name']} passed Go and collected $200")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}")


def move_player_to(player, new_position, game):
    """Move player to a specific board space."""
    old_position = player["position"]
    player["position"] = new_position

    if new_position < old_position or new_position == 0:
        player["money"] += 200
        add_log(game, f"{player['name']} moved past Go and collected $200")

    add_log(game, f"{player['name']} moved to {BOARD[player['position']]}")


# ============================================================
# RENT
# ============================================================

def count_railroads_owned(owner):
    """Count how many railroads a player owns."""
    return sum(
        1 for prop in owner["properties"]
        if PROPERTY_DATA[prop]["type"] == "railroad"
    )


def count_utilities_owned(owner):
    """Count how many utilities a player owns."""
    return sum(
        1 for prop in owner["properties"]
        if PROPERTY_DATA[prop]["type"] == "utility"
    )


def owner_has_full_color_set(owner, color):
    """Check whether a player owns all properties in a color group."""
    if color is None:
        return False

    color_group = [
        prop for prop in PROPERTY_DATA
        if PROPERTY_DATA[prop]["color"] == color
    ]

    for prop in color_group:
        if prop not in owner["properties"]:
            return False

    return True


def calculate_rent(space, owner, dice_roll_total):
    """Calculate rent based on property type."""
    data = PROPERTY_DATA[space]

    if data["type"] == "property":
        rent = data["rent"]

        # Simplified rule: full color set doubles base rent.
        if owner_has_full_color_set(owner, data["color"]):
            rent *= 2

        return rent

    if data["type"] == "railroad":
        num = count_railroads_owned(owner)
        return 25 * (2 ** (num - 1))

    if data["type"] == "utility":
        num = count_utilities_owned(owner)

        if num == 1:
            return 4 * dice_roll_total

        return 10 * dice_roll_total

    return 0


# ============================================================
# PROPERTY BUYING + RENT PAYMENT
# ============================================================

def buy_property(player, space, game):
    """Buy an unowned property if the player has enough money."""
    price = PROPERTY_DATA[space]["price"]

    if player["money"] >= price:
        player["money"] -= price
        player["properties"].append(space)
        game["property_owners"][space] = player["name"]
        add_log(game, f"{player['name']} bought {space} for ${price}")
        return True

    add_log(game, f"{player['name']} could not afford {space}")
    return False


def choose_buy_property(game):
    """
    Called by the UI when the player chooses Buy.
    This resolves a pending buy decision.
    """
    action = game.get("pending_action")

    if action is None or action["type"] != "buy_property":
        add_log(game, "There is no property to buy right now.")
        return False

    player = find_player_by_name(game["players"], action["player"])
    space = action["property"]

    if player is None:
        return False

    bought = buy_property(player, space, game)
    game["pending_action"] = None
    check_bankruptcy(player, game["property_owners"], game)
    return bought


def choose_skip_property(game):
    """
    Called by the UI when the player chooses Skip.
    This clears a pending buy decision.
    """
    action = game.get("pending_action")

    if action is None or action["type"] != "buy_property":
        add_log(game, "There is no property to skip right now.")
        return False

    add_log(game, f"{action['player']} skipped buying {action['property']}")
    game["pending_action"] = None
    return True


def pay_rent(player, owner, space, dice_roll_total, game):
    """Transfer rent from landing player to owner."""
    rent = calculate_rent(space, owner, dice_roll_total)

    player["money"] -= rent
    owner["money"] += rent

    add_log(game, f"{player['name']} paid ${rent} rent to {owner['name']} for {space}")
    check_bankruptcy(player, game["property_owners"], game)


def handle_property_space(player, space, dice_roll_total, game):
    """
    Handle landing on a buyable property.
    If unowned, create a pending Buy/Skip action instead of auto-buying.
    """
    if space not in game["property_owners"]:
        game["pending_action"] = {
            "type": "buy_property",
            "player": player["name"],
            "property": space,
            "price": PROPERTY_DATA[space]["price"]
        }

        add_log(game, f"{space} is available for ${PROPERTY_DATA[space]['price']}")
        return

    owner_name = game["property_owners"][space]

    if owner_name == player["name"]:
        add_log(game, f"{player['name']} landed on their own property")
        return

    owner = find_player_by_name(game["players"], owner_name)

    if owner is None or owner["bankrupt"]:
        return

    pay_rent(player, owner, space, dice_roll_total, game)


# ============================================================
# CARDS
# ============================================================

def handle_card(player, card, game):
    """Apply the effect of a Chance or Community Chest card."""
    add_log(game, f"{player['name']} drew a card: {card['text']}")

    if card["type"] == "money":
        player["money"] += card["amount"]

        if card["amount"] >= 0:
            add_log(game, f"{player['name']} received ${card['amount']}")
        else:
            add_log(game, f"{player['name']} paid ${-card['amount']}")

    elif card["type"] == "move":
        move_player_to(player, card["position"], game)
        handle_landing(player, 0, game)

    elif card["type"] == "move_relative":
        move_player(player, card["amount"], game)
        handle_landing(player, 0, game)

    elif card["type"] == "jail":
        send_player_to_jail(player, game)

    check_bankruptcy(player, game["property_owners"], game)


# ============================================================
# LANDING ON BOARD SPACES
# ============================================================

def handle_landing(player, dice_roll_total, game):
    """Handle what happens after a player lands on a board space."""
    space = BOARD[player["position"]]

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

    check_bankruptcy(player, game["property_owners"], game)


# ============================================================
# UI TURN FLOW
# ============================================================

def roll_current_player(game):
    """
    Roll dice for the current player.
    This function is designed for an interactive UI.
    """
    if game["pending_action"] is not None:
        add_log(game, "Choose Buy or Skip before rolling again.")
        return False

    if game["has_rolled"]:
        add_log(game, "You already rolled this turn. End your turn.")
        return False

    players = game["players"]
    player = players[game["turn"] % len(players)]

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

    add_log(game, f"{player['name']} rolled {die1} and {die2} for a total of {total}")

    move_player(player, total, game)
    handle_landing(player, total, game)

    game["has_rolled"] = True
    return True


def end_turn(game):
    """
    End the current player's turn.
    The player cannot end turn while a Buy/Skip decision is pending.
    """
    if game["pending_action"] is not None:
        add_log(game, "You must Buy or Skip before ending your turn.")
        return False

    game["turn"] += 1
    game["has_rolled"] = False
    game["last_roll"] = None
    return True


def take_turn(game):
    """
    Automatic turn function for testing.
    The Pygame UI should use roll_current_player, choose_buy_property,
    choose_skip_property, and end_turn instead.
    """
    roll_current_player(game)

    if game["pending_action"] is not None:
        choose_buy_property(game)

    end_turn(game)


# ============================================================
# GAME STATE
# ============================================================

def get_game_state(game):
    """Return a frontend-friendly summary of game state."""
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
        "turn": game["turn"],
        "current_player": game["players"][game["turn"] % len(game["players"])]["name"],
        "winner": winner["name"] if winner else None,
        "log": game["log"][:],
        "pending_action": game.get("pending_action"),
        "has_rolled": game["has_rolled"],
        "last_roll": game["last_roll"]
    }


# ============================================================
# TEST MODE
# ============================================================

def play_game(player_names, max_turns=200):
    """Run an automatic simulation for backend testing."""
    game = create_game(player_names)
    add_log(game, "Starting Monopoly game!")

    for _ in range(max_turns):
        winner = get_winner(game["players"])

        if winner is not None:
            add_log(game, f"{winner['name']} wins the game!")
            return game

        take_turn(game)

    add_log(game, "Game reached max turns.")
    return game


if __name__ == "__main__":
    play_game(["Alice", "Bob"], max_turns=50)