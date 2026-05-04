# backend/player.py
# This file handles player creation and player helper functions.

def create_player(name):
    """Create a new player dictionary."""
    return {
        "name": name,
        "money": 1500,
        "position": 0,
        "properties": [],
        "in_jail": False,
        "jail_turns": 0,
        "bankrupt": False
    }


def find_player_by_name(players, name):
    """Find a player object by name."""
    for player in players:
        if player["name"] == name:
            return player
    return None


def get_active_players(players):
    """Return all players who are not bankrupt."""
    return [player for player in players if not player["bankrupt"]]


def get_winner(players):
    """Return winner if only one player remains."""
    active = get_active_players(players)

    if len(active) == 1:
        return active[0]

    return None