# backend/__init__.py
# Makes backend functions importable by frontend.

from backend.game import (
    create_game,
    get_game_state,
    roll_current_player,
    choose_buy_property,
    choose_skip_property,
    end_turn,
    buy_house,
    get_buildable_properties,
    take_turn,
    play_game
)

from backend.board import BOARD, PROPERTY_DATA