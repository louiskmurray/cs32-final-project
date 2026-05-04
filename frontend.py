# frontend.py
# Advanced Pygame frontend for Monopoly-style game.
# Backend handles the rules. This file handles visuals, buttons, dice animation,
# property popups, card popups, houses, and player UI.

import pygame
import sys
import random
import time

from backend.game import (
    create_game,
    get_game_state,
    roll_current_player,
    choose_buy_property,
    choose_skip_property,
    end_turn,
    buy_house,
)

from backend.board import BOARD, PROPERTY_DATA


# ============================================================
# SETUP
# ============================================================

pygame.init()

WIDTH = 1400
HEIGHT = 820

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monopoly Simulator")
clock = pygame.time.Clock()


# ============================================================
# COLORS + FONTS
# ============================================================

BG = (225, 241, 222)
BOARD_GREEN = (205, 231, 202)
PAPER = (255, 252, 246)
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (210, 210, 210)
DARK_GRAY = (75, 75, 75)

PINK = (246, 158, 199)
LIGHT_PINK = (255, 226, 240)
BLUE = (112, 159, 235)
GREEN = (123, 200, 145)
YELLOW = (250, 220, 120)
RED = (234, 83, 83)
ORANGE = (245, 160, 80)

PROPERTY_COLORS = {
    "brown": (147, 92, 50),
    "light blue": (142, 217, 232),
    "pink": (238, 133, 190),
    "orange": (245, 155, 73),
    "red": (235, 83, 83),
    "yellow": (250, 218, 80),
    "green": (94, 185, 105),
    "dark blue": (72, 99, 190),
    None: (210, 210, 210),
}

PLAYER_COLORS = [
    (235, 76, 76),
    (70, 125, 255),
    (78, 185, 110),
    (245, 180, 55),
    (150, 90, 220),
    (45, 185, 185),
]

TITLE_FONT = pygame.font.SysFont("arial", 42, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 30, bold=True)
MID_FONT = pygame.font.SysFont("arial", 21, bold=True)
FONT = pygame.font.SysFont("arial", 16)
SMALL_FONT = pygame.font.SysFont("arial", 12)
TINY_FONT = pygame.font.SysFont("arial", 10)


# ============================================================
# BOARD LAYOUT
# ============================================================

BOARD_X = 40
BOARD_Y = 40
CELL = 62
BOARD_SIZE = CELL * 11


def get_board_coordinates():
    """Map each board index to a visual coordinate."""
    coords = {}

    for i in range(11):
        coords[i] = (BOARD_X + (10 - i) * CELL, BOARD_Y + 10 * CELL)

    for i in range(11, 21):
        coords[i] = (BOARD_X, BOARD_Y + (20 - i) * CELL)

    for i in range(21, 31):
        coords[i] = (BOARD_X + (i - 20) * CELL, BOARD_Y)

    for i in range(31, 40):
        coords[i] = (BOARD_X + 10 * CELL, BOARD_Y + (i - 30) * CELL)

    return coords


BOARD_COORDS = get_board_coordinates()


# ============================================================
# UI HELPERS
# ============================================================

class Button:
    """Reusable clickable button."""

    def __init__(self, x, y, w, h, text, color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)

        color = self.color
        if hover:
            color = tuple(min(255, c + 20) for c in color)

        pygame.draw.rect(screen, color, self.rect, border_radius=18)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=18)

        label = MID_FONT.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def draw_text(text, font, color, x, y):
    img = font.render(str(text), True, color)
    screen.blit(img, (x, y))


def wrap_text(text, font, max_width):
    words = str(text).split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word if current else word

        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped(text, font, color, x, y, max_width, line_height):
    lines = wrap_text(text, font, max_width)

    for i, line in enumerate(lines):
        draw_text(line, font, color, x, y + i * line_height)


def short_name(space):
    return (
        space.replace("Mediterranean", "Med.")
        .replace("Community Chest", "Chest")
        .replace("Pennsylvania Railroad", "Penn. RR")
        .replace("Reading Railroad", "Reading RR")
        .replace("Short Line Railroad", "Short Line")
        .replace("North Carolina", "N. Carolina")
        .replace("Electric Company", "Electric Co.")
        .replace("Connecticut", "Conn.")
        .replace("Pennsylvania Ave", "Penn. Ave")
    )


def get_instruction(state):
    """Tell user what they can do right now."""
    if state["winner"]:
        return "Game over."

    if state["pending_action"]:
        prop = state["pending_action"]["property"]
        price = state["pending_action"]["price"]
        return f"{prop} is unowned and costs ${price}. Choose Buy or Skip."

    if not state["has_rolled"]:
        return f"{state['current_player']}, click Roll Dice to start your turn."

    return "You rolled already. Click End Turn to pass to the next player."


# ============================================================
# DICE ANIMATION
# ============================================================

dice_animation_end = 0
animated_dice = (1, 1)


def start_dice_animation():
    """Start a short dice animation."""
    global dice_animation_end
    dice_animation_end = time.time() + 0.6


def get_display_dice(state):
    """Show random dice while animating, otherwise show real last roll."""
    global animated_dice

    if time.time() < dice_animation_end:
        animated_dice = (random.randint(1, 6), random.randint(1, 6))
        return animated_dice

    if state["last_roll"]:
        return state["last_roll"]

    return None


def draw_die(x, y, value):
    """Draw one die."""
    rect = pygame.Rect(x, y, 48, 48)
    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

    dot_positions = {
        1: [(24, 24)],
        2: [(14, 14), (34, 34)],
        3: [(14, 14), (24, 24), (34, 34)],
        4: [(14, 14), (34, 14), (14, 34), (34, 34)],
        5: [(14, 14), (34, 14), (24, 24), (14, 34), (34, 34)],
        6: [(14, 12), (34, 12), (14, 24), (34, 24), (14, 36), (34, 36)],
    }

    for dx, dy in dot_positions[value]:
        pygame.draw.circle(screen, BLACK, (x + dx, y + dy), 4)


# ============================================================
# BOARD DRAWING
# ============================================================

def draw_board(state):
    """Draw Monopoly-inspired board."""
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)

    pygame.draw.rect(screen, BOARD_GREEN, board_rect)
    pygame.draw.rect(screen, BLACK, board_rect, 4)

    inner = pygame.Rect(BOARD_X + CELL, BOARD_Y + CELL, CELL * 9, CELL * 9)
    pygame.draw.rect(screen, BOARD_GREEN, inner)
    pygame.draw.rect(screen, BLACK, inner, 3)

    # Center logo
    logo_rect = pygame.Rect(BOARD_X + 220, BOARD_Y + 290, 275, 82)
    pygame.draw.rect(screen, RED, logo_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, logo_rect, 3, border_radius=8)
    draw_text("MONOPOLY", BIG_FONT, WHITE, logo_rect.x + 43, logo_rect.y + 23)
    draw_text("PROPERTY TRADING GAME", SMALL_FONT, DARK_GRAY, BOARD_X + 250, BOARD_Y + 390)

    # Decorative center cards
    pygame.draw.rect(screen, (151, 220, 240), (BOARD_X + 125, BOARD_Y + 150, 135, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (BOARD_X + 125, BOARD_Y + 150, 135, 90), 2, border_radius=8)
    draw_text("CHEST", MID_FONT, BLACK, BOARD_X + 157, BOARD_Y + 183)

    pygame.draw.rect(screen, ORANGE, (BOARD_X + 465, BOARD_Y + 475, 135, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (BOARD_X + 465, BOARD_Y + 475, 135, 90), 2, border_radius=8)
    draw_text("?", TITLE_FONT, WHITE, BOARD_X + 515, BOARD_Y + 495)

    # Player position map
    position_map = {}
    for idx, player in enumerate(state["players"]):
        position_map.setdefault(player["position"], []).append((idx, player))

    for i, space in enumerate(BOARD):
        x, y = BOARD_COORDS[i]
        rect = pygame.Rect(x, y, CELL, CELL)

        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        if space in PROPERTY_DATA:
            color = PROPERTY_COLORS.get(PROPERTY_DATA[space]["color"], GRAY)
            prop_type = PROPERTY_DATA[space]["type"]

            if prop_type == "property":
                strip = pygame.Rect(x, y, CELL, 13)
                pygame.draw.rect(screen, color, strip)
                pygame.draw.rect(screen, BLACK, strip, 1)
            else:
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)

        # Space number and name
        draw_text(i, TINY_FONT, BLACK, x + 4, y + 2)

        name_lines = wrap_text(short_name(space), TINY_FONT, 52)
        for line_i, line in enumerate(name_lines[:4]):
            draw_text(line, TINY_FONT, BLACK, x + 5, y + 15 + line_i * 10)

        # Price
        if space in PROPERTY_DATA:
            price = PROPERTY_DATA[space]["price"]
            draw_text(f"${price}", TINY_FONT, BLACK, x + 5, y + 50)

        # Houses
        houses = state.get("houses", {})
        house_count = houses.get(space, 0)
        for h in range(house_count):
            house_x = x + 7 + h * 12
            house_y = y + 36
            pygame.draw.rect(screen, GREEN, (house_x, house_y, 9, 9))
            pygame.draw.rect(screen, BLACK, (house_x, house_y, 9, 9), 1)

        # Player tokens
        if i in position_map:
            for token_i, (player_i, player) in enumerate(position_map[i]):
                token_x = x + 13 + (token_i % 3) * 15
                token_y = y + 53 - (token_i // 3) * 13

                pygame.draw.circle(
                    screen,
                    PLAYER_COLORS[player_i % len(PLAYER_COLORS)],
                    (token_x, token_y),
                    7,
                )
                pygame.draw.circle(screen, BLACK, (token_x, token_y), 7, 2)


# ============================================================
# DASHBOARD
# ============================================================

def draw_dashboard(state):
    """Draw right-side dashboard."""
    panel_x = 780
    panel_y = 40
    panel_w = 570
    panel_h = 610

    pygame.draw.rect(screen, PAPER, (panel_x, panel_y, panel_w, panel_h), border_radius=28)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=28)

    draw_text("Game Dashboard", BIG_FONT, BLACK, panel_x + 28, panel_y + 22)

    draw_text(
        f"Current Player: {state['current_player']}",
        MID_FONT,
        PINK,
        panel_x + 28,
        panel_y + 68,
    )

    # Instruction card
    instruction = get_instruction(state)
    instr_rect = pygame.Rect(panel_x + 28, panel_y + 105, 515, 65)
    pygame.draw.rect(screen, LIGHT_PINK, instr_rect, border_radius=16)
    draw_wrapped(instruction, FONT, BLACK, instr_rect.x + 16, instr_rect.y + 12, 485, 19)

    # Dice display
    dice_rect = pygame.Rect(panel_x + 28, panel_y + 185, 230, 70)
    pygame.draw.rect(screen, (255, 245, 220), dice_rect, border_radius=14)
    pygame.draw.rect(screen, GRAY, dice_rect, 2, border_radius=14)
    draw_text("Dice", FONT, BLACK, dice_rect.x + 16, dice_rect.y + 10)

    dice = get_display_dice(state)
    if dice:
        d1, d2 = dice
        draw_die(dice_rect.x + 78, dice_rect.y + 14, d1)
        draw_die(dice_rect.x + 135, dice_rect.y + 14, d2)
    else:
        draw_text("No roll yet", FONT, DARK_GRAY, dice_rect.x + 75, dice_rect.y + 34)

    # Card display
    card_rect = pygame.Rect(panel_x + 275, panel_y + 185, 268, 70)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=14)
    pygame.draw.rect(screen, PINK, card_rect, 2, border_radius=14)

    if state.get("current_card"):
        card_text = state["current_card"]["text"]
        draw_text("Card Drawn", FONT, BLACK, card_rect.x + 14, card_rect.y + 9)
        draw_wrapped(card_text, SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 32, 235, 14)
    else:
        draw_text("Card", FONT, BLACK, card_rect.x + 14, card_rect.y + 9)
        draw_text("No card drawn", SMALL_FONT, DARK_GRAY, card_rect.x + 14, card_rect.y + 36)

    # Players
    draw_text("Players", MID_FONT, BLACK, panel_x + 28, panel_y + 275)

    y = panel_y + 308
    for idx, player in enumerate(state["players"]):
        card = pygame.Rect(panel_x + 28, y, 515, 63)

        pygame.draw.rect(screen, WHITE, card, border_radius=15)
        pygame.draw.rect(screen, PLAYER_COLORS[idx % len(PLAYER_COLORS)], card, 3, border_radius=15)

        draw_text(player["name"], FONT, BLACK, card.x + 14, card.y + 7)
        draw_text(f"${player['money']}", SMALL_FONT, BLACK, card.x + 14, card.y + 30)
        draw_text(f"At: {player['space']}", SMALL_FONT, BLACK, card.x + 90, card.y + 30)
        draw_text(f"Props: {len(player['properties'])}", SMALL_FONT, BLACK, card.x + 415, card.y + 30)

        y += 73
        if y > panel_y + 495:
            break

    # Feed
    feed = pygame.Rect(panel_x + 28, panel_y + 522, 515, 72)
    pygame.draw.rect(screen, (250, 250, 250), feed, border_radius=14)
    pygame.draw.rect(screen, GRAY, feed, 2, border_radius=14)
    draw_text("Feed", FONT, BLACK, feed.x + 14, feed.y + 8)

    logs = [log for log in state["log"][-3:] if log.strip()]
    log_y = feed.y + 29

    if not logs:
        draw_text("No moves yet.", SMALL_FONT, DARK_GRAY, feed.x + 14, log_y)
    else:
        for log in logs:
            draw_wrapped("- " + log, SMALL_FONT, BLACK, feed.x + 14, log_y, 480, 14)
            log_y += 19


# ============================================================
# POPUPS
# ============================================================

def draw_property_popup(state):
    """Draw Buy/Skip popup if property is available."""
    if not state["pending_action"]:
        return

    action = state["pending_action"]
    prop = action["property"]
    price = action["price"]

    data = PROPERTY_DATA[prop]
    color = PROPERTY_COLORS.get(data["color"], GRAY)

    popup = pygame.Rect(810, 665, 510, 115)
    pygame.draw.rect(screen, PAPER, popup, border_radius=22)
    pygame.draw.rect(screen, BLACK, popup, 3, border_radius=22)

    pygame.draw.rect(screen, color, (popup.x + 20, popup.y + 20, 80, 75), border_radius=10)
    pygame.draw.rect(screen, BLACK, (popup.x + 20, popup.y + 20, 80, 75), 2, border_radius=10)

    draw_text("Property Available", MID_FONT, BLACK, popup.x + 120, popup.y + 18)
    draw_text(prop, FONT, BLACK, popup.x + 120, popup.y + 47)
    draw_text(f"Price: ${price} | Base Rent: ${data['rent']}", SMALL_FONT, DARK_GRAY, popup.x + 120, popup.y + 72)


def draw_house_panel(state):
    """Show properties where current player can buy houses."""
    buildable = state.get("buildable_properties", [])

    panel = pygame.Rect(40, 715, 730, 75)
    pygame.draw.rect(screen, PAPER, panel, border_radius=22)
    pygame.draw.rect(screen, BLACK, panel, 3, border_radius=22)

    draw_text("Build Houses", MID_FONT, BLACK, panel.x + 20, panel.y + 22)

    if not buildable:
        draw_text("Own a full color set to build houses.", FONT, DARK_GRAY, panel.x + 180, panel.y + 27)
    else:
        draw_text("Click a property button to add a house.", FONT, DARK_GRAY, panel.x + 180, panel.y + 27)


# ============================================================
# CONTROL BAR
# ============================================================

def draw_control_bar():
    pygame.draw.rect(screen, PAPER, (40, 665, 730, 42), border_radius=18)
    pygame.draw.rect(screen, BLACK, (40, 665, 730, 42), 2, border_radius=18)
    draw_text("Controls", MID_FONT, BLACK, 60, 674)


def draw_buttons(buttons):
    for button in buttons:
        button.draw()


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(input_text):
    screen.fill(BG)

    card = pygame.Rect(335, 170, 730, 400)
    pygame.draw.rect(screen, PAPER, card, border_radius=30)
    pygame.draw.rect(screen, BLACK, card, 3, border_radius=30)

    draw_text("MONOPOLY SIMULATOR", TITLE_FONT, BLACK, 470, 230)
    draw_text("Enter player names separated by commas", MID_FONT, DARK_GRAY, 465, 295)

    input_box = pygame.Rect(445, 360, 510, 60)
    pygame.draw.rect(screen, WHITE, input_box, border_radius=16)
    pygame.draw.rect(screen, PINK, input_box, 3, border_radius=16)

    draw_text(input_text, FONT, BLACK, input_box.x + 16, input_box.y + 19)

    draw_text("Example: luke, louis, andy", FONT, DARK_GRAY, 540, 445)
    draw_text("Press ENTER to start", MID_FONT, PINK, 565, 490)


# ============================================================
# MAIN APP
# ============================================================

def main():
    game = None
    input_text = ""
    mode = "start"
    buttons = []

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if mode == "start" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    names = [n.strip() for n in input_text.split(",") if n.strip()]

                    if len(names) >= 2:
                        game = create_game(names)
                        mode = "game"
                    else:
                        input_text = ""

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                else:
                    input_text += event.unicode

            if mode == "game" and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                for button in buttons:
                    if button.clicked(mouse_pos):
                        button.action()

        if mode == "start":
            draw_start_screen(input_text)
            pygame.display.flip()
            continue

        state = get_game_state(game)

        screen.fill(BG)

        draw_board(state)
        draw_dashboard(state)
        draw_control_bar()
        draw_house_panel(state)
        draw_property_popup(state)

        buttons = []

        buttons.append(Button(160, 663, 130, 42, "Roll Dice", GREEN, lambda: [start_dice_animation(), roll_current_player(game)]))
        buttons.append(Button(305, 663, 95, 42, "Buy", PINK, lambda: choose_buy_property(game)))
        buttons.append(Button(415, 663, 95, 42, "Skip", YELLOW, lambda: choose_skip_property(game)))
        buttons.append(Button(525, 663, 130, 42, "End Turn", BLUE, lambda: end_turn(game)))

        # House buttons
        buildable = state.get("buildable_properties", [])
        start_x = 240
        for i, prop in enumerate(buildable[:3]):
            buttons.append(
                Button(
                    start_x + i * 165,
                    733,
                    150,
                    38,
                    short_name(prop),
                    GREEN,
                    lambda p=prop: buy_house(game, p)
                )
            )

        draw_buttons(buttons)

        if state["winner"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))

            draw_text("GAME OVER", TITLE_FONT, BLACK, 560, 350)
            draw_text(f"{state['winner']} wins!", MID_FONT, PINK, 590, 410)

        pygame.display.flip()


if __name__ == "__main__":
    main()