# backend/board.py
# This file stores the Monopoly board layout and all property information.
# Keeping this separate makes the backend more modular.

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


def is_property(space):
    """Return True if the space is buyable."""
    return space in PROPERTY_DATA