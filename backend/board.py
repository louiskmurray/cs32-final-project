# backend/board.py
# Stores board layout and property data.

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
    "Mediterranean Ave": {"price": 60, "rent": 2, "type": "property", "color": "brown", "house_cost": 50},
    "Baltic Ave": {"price": 60, "rent": 4, "type": "property", "color": "brown", "house_cost": 50},

    "Reading Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None, "house_cost": None},

    "Oriental Ave": {"price": 100, "rent": 6, "type": "property", "color": "light blue", "house_cost": 50},
    "Vermont Ave": {"price": 100, "rent": 6, "type": "property", "color": "light blue", "house_cost": 50},
    "Connecticut Ave": {"price": 120, "rent": 8, "type": "property", "color": "light blue", "house_cost": 50},

    "St. Charles Place": {"price": 140, "rent": 10, "type": "property", "color": "pink", "house_cost": 100},
    "Electric Company": {"price": 150, "rent": 10, "type": "utility", "color": None, "house_cost": None},
    "States Ave": {"price": 140, "rent": 10, "type": "property", "color": "pink", "house_cost": 100},
    "Virginia Ave": {"price": 160, "rent": 12, "type": "property", "color": "pink", "house_cost": 100},

    "Pennsylvania Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None, "house_cost": None},

    "St. James Place": {"price": 180, "rent": 14, "type": "property", "color": "orange", "house_cost": 100},
    "Tennessee Ave": {"price": 180, "rent": 14, "type": "property", "color": "orange", "house_cost": 100},
    "New York Ave": {"price": 200, "rent": 16, "type": "property", "color": "orange", "house_cost": 100},

    "Kentucky Ave": {"price": 220, "rent": 18, "type": "property", "color": "red", "house_cost": 150},
    "Indiana Ave": {"price": 220, "rent": 18, "type": "property", "color": "red", "house_cost": 150},
    "Illinois Ave": {"price": 240, "rent": 20, "type": "property", "color": "red", "house_cost": 150},

    "B&O Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None, "house_cost": None},

    "Atlantic Ave": {"price": 260, "rent": 22, "type": "property", "color": "yellow", "house_cost": 150},
    "Ventnor Ave": {"price": 260, "rent": 22, "type": "property", "color": "yellow", "house_cost": 150},
    "Water Works": {"price": 150, "rent": 10, "type": "utility", "color": None, "house_cost": None},
    "Marvin Gardens": {"price": 280, "rent": 24, "type": "property", "color": "yellow", "house_cost": 150},

    "Pacific Ave": {"price": 300, "rent": 26, "type": "property", "color": "green", "house_cost": 200},
    "North Carolina Ave": {"price": 300, "rent": 26, "type": "property", "color": "green", "house_cost": 200},
    "Pennsylvania Ave": {"price": 320, "rent": 28, "type": "property", "color": "green", "house_cost": 200},

    "Short Line Railroad": {"price": 200, "rent": 25, "type": "railroad", "color": None, "house_cost": None},

    "Park Place": {"price": 350, "rent": 35, "type": "property", "color": "dark blue", "house_cost": 200},
    "Boardwalk": {"price": 400, "rent": 50, "type": "property", "color": "dark blue", "house_cost": 200}
}


def is_property(space):
    """Return True if this board space is buyable."""
    return space in PROPERTY_DATA


def get_color_group(color):
    """Return all properties in a color group."""
    return [
        prop for prop in PROPERTY_DATA
        if PROPERTY_DATA[prop]["color"] == color
    ]