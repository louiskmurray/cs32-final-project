# backend/cards.py
# Stores Chance and Community Chest cards.

import random

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


def draw_chance_card(game):
    """Draw the next Chance card."""
    if game["chance_index"] >= len(game["chance_deck"]):
        random.shuffle(game["chance_deck"])
        game["chance_index"] = 0

    card = game["chance_deck"][game["chance_index"]]
    game["chance_index"] += 1
    return card


def draw_community_chest_card(game):
    """Draw the next Community Chest card."""
    if game["community_chest_index"] >= len(game["community_chest_deck"]):
        random.shuffle(game["community_chest_deck"])
        game["community_chest_index"] = 0

    card = game["community_chest_deck"][game["community_chest_index"]]
    game["community_chest_index"] += 1
    return card