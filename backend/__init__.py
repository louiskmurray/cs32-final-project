# backend/__init__.py
# Makes backend functions easier to import elsewhere.

from backend.game import (
    create_game,
    get_game_state,
    roll_current_player,
    choose_buy_property,
    choose_skip_property,
    end_turn,
    take_turn,
    play_game
)

from backend.board import BOARD, PROPERTY_DATA