# pygame_frontend.py
# Visual Monopoly frontend using Pygame.
# This file only handles UI. The backend handles the game rules.

import pygame
import sys

from backend.game import (
    create_game,
    get_game_state,
    roll_current_player,
    choose_buy_property,
    choose_skip_property,
    end_turn
)

from backend.board import BOARD, PROPERTY_DATA


# ============================================================
# PYGAME SETUP
# ============================================================

pygame.init()

WIDTH = 1300
HEIGHT = 850

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monopoly Simulator")

clock = pygame.time.Clock()


# ============================================================
# COLORS + FONTS
# ============================================================

BG = (248, 241, 230)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
PINK = (245, 156, 196)
GREEN = (124, 190, 140)
BLUE = (130, 180, 230)
YELLOW = (250, 220, 120)
GRAY = (220, 220, 220)
DARK_GRAY = (90, 90, 90)
RED = (230, 80, 80)

PROPERTY_COLORS = {
    "brown": (145, 95, 55),
    "light blue": (145, 220, 235),
    "pink": (245, 156, 196),
    "orange": (245, 155, 80),
    "red": (230, 80, 80),
    "yellow": (245, 215, 80),
    "green": (100, 190, 110),
    "dark blue": (70, 100, 190),
    None: (210, 210, 210)
}

PLAYER_COLORS = [
    (230, 80, 80),
    (80, 120, 240),
    (80, 180, 120),
    (245, 180, 60),
    (150, 90, 220),
    (40, 190, 190)
]

FONT = pygame.font.SysFont("arial", 18)
SMALL_FONT = pygame.font.SysFont("arial", 13)
BIG_FONT = pygame.font.SysFont("arial", 36, bold=True)
MID_FONT = pygame.font.SysFont("arial", 24, bold=True)


# ============================================================
# BUTTON CLASS
# ============================================================

class Button:
    """A simple clickable button."""

    def __init__(self, x, y, w, h, text, color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=16)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=16)

        label = MID_FONT.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ============================================================
# TEXT HELPERS
# ============================================================

def draw_text(text, font, color, x, y):
    """Draw text at a location."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def wrap_text(text, font, max_width):
    """Split long text into multiple lines."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word if current else word

        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped_text(text, font, color, x, y, max_width, line_height):
    """Draw wrapped text."""
    lines = wrap_text(text, font, max_width)

    for i, line in enumerate(lines):
        draw_text(line, font, color, x, y + i * line_height)


# ============================================================
# BOARD COORDINATES
# ============================================================

def get_board_coordinates():
    """Return screen coordinates for each of the 40 board spaces."""
    coords = {}

    board_x = 40
    board_y = 40
    cell = 65

    for i in range(11):
        coords[i] = (board_x + (10 - i) * cell, board_y + 10 * cell)

    for i in range(11, 21):
        coords[i] = (board_x, board_y + (20 - i) * cell)

    for i in range(21, 31):
        coords[i] = (board_x + (i - 20) * cell, board_y)

    for i in range(31, 40):
        coords[i] = (board_x + 10 * cell, board_y + (i - 30) * cell)

    return coords


BOARD_COORDS = get_board_coordinates()


# ============================================================
# DRAW BOARD
# ============================================================

def draw_board(state):
    """Draw the Monopoly board and player tokens."""
    cell = 65

    pygame.draw.rect(screen, (235, 225, 210), (40, 40, 715, 715), border_radius=18)

    draw_text("MONOPOLY", BIG_FONT, BLACK, 275, 340)
    draw_text("SIMULATOR", MID_FONT, DARK_GRAY, 305, 385)

    position_map = {}

    for idx, player in enumerate(state["players"]):
        position_map.setdefault(player["position"], []).append((idx, player))

    for i, space in enumerate(BOARD):
        x, y = BOARD_COORDS[i]

        color = WHITE

        if space in PROPERTY_DATA:
            prop_color = PROPERTY_DATA[space]["color"]
            color = PROPERTY_COLORS.get(prop_color, WHITE)

        rect = pygame.Rect(x, y, cell, cell)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        draw_text(str(i), SMALL_FONT, BLACK, x + 4, y + 4)

        short_name = space.replace("Railroad", "RR")
        lines = wrap_text(short_name, SMALL_FONT, 55)

        for line_index, line in enumerate(lines[:3]):
            draw_text(line, SMALL_FONT, BLACK, x + 4, y + 18 + line_index * 13)

        if i in position_map:
            for token_index, (player_index, player) in enumerate(position_map[i]):
                token_x = x + 12 + (token_index % 3) * 16
                token_y = y + 48 + (token_index // 3) * 12

                pygame.draw.circle(
                    screen,
                    PLAYER_COLORS[player_index % len(PLAYER_COLORS)],
                    (token_x, token_y),
                    7
                )

                pygame.draw.circle(screen, BLACK, (token_x, token_y), 7, 1)


# ============================================================
# DRAW SIDE PANEL
# ============================================================

def draw_side_panel(state):
    """Draw dashboard, player summaries, pending actions, and event log."""
    panel_x = 790
    panel_y = 40
    panel_w = 470
    panel_h = 715

    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), border_radius=22)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=22)

    draw_text("Game Dashboard", BIG_FONT, BLACK, panel_x + 30, panel_y + 25)

    draw_text(
        f"Current Player: {state['current_player']}",
        MID_FONT,
        PINK,
        panel_x + 30,
        panel_y + 80
    )

    if state["last_roll"]:
        d1, d2 = state["last_roll"]
        draw_text(f"Last Roll: {d1} + {d2} = {d1 + d2}", FONT, BLACK, panel_x + 30, panel_y + 115)
    else:
        draw_text("Last Roll: none", FONT, DARK_GRAY, panel_x + 30, panel_y + 115)

    pending = state["pending_action"]

    if pending:
        msg = f"{pending['property']} is available for ${pending['price']}. Buy or Skip?"
        draw_wrapped_text(msg, FONT, BLACK, panel_x + 30, panel_y + 145, 400, 22)
    else:
        draw_text("No pending action.", FONT, DARK_GRAY, panel_x + 30, panel_y + 145)

    draw_text("Players", MID_FONT, BLACK, panel_x + 30, panel_y + 195)

    y = panel_y + 230

    for idx, player in enumerate(state["players"]):
        card_rect = pygame.Rect(panel_x + 30, y, 410, 82)

        pygame.draw.rect(screen, (248, 248, 248), card_rect, border_radius=14)
        pygame.draw.rect(
            screen,
            PLAYER_COLORS[idx % len(PLAYER_COLORS)],
            card_rect,
            3,
            border_radius=14
        )

        draw_text(player["name"], FONT, BLACK, panel_x + 45, y + 10)
        draw_text(f"Money: ${player['money']}", SMALL_FONT, BLACK, panel_x + 45, y + 35)
        draw_text(f"Location: {player['space']}", SMALL_FONT, BLACK, panel_x + 45, y + 52)
        draw_text(f"Properties: {len(player['properties'])}", SMALL_FONT, BLACK, panel_x + 270, y + 35)

        y += 92

    draw_text("Latest Events", MID_FONT, BLACK, panel_x + 30, panel_y + 515)

    log_y = panel_y + 550

    recent_logs = state["log"][-6:]

    for log in recent_logs:
        if log.strip() == "":
            continue

        draw_wrapped_text("- " + log, SMALL_FONT, BLACK, panel_x + 30, log_y, 405, 16)
        log_y += 34


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(input_text):
    """Draw the player-name input screen."""
    screen.fill(BG)

    draw_text("MONOPOLY SIMULATOR", BIG_FONT, BLACK, 430, 220)
    draw_text("Enter player names separated by commas", MID_FONT, DARK_GRAY, 420, 280)

    input_box = pygame.Rect(400, 340, 500, 60)

    pygame.draw.rect(screen, WHITE, input_box, border_radius=14)
    pygame.draw.rect(screen, BLACK, input_box, 2, border_radius=14)

    draw_text(input_text, MID_FONT, BLACK, input_box.x + 15, input_box.y + 17)

    draw_text("Example: Luke, Koan, Andy", FONT, DARK_GRAY, 530, 420)
    draw_text("Press ENTER to start", MID_FONT, PINK, 540, 470)


# ============================================================
# MAIN APP
# ============================================================

def main():
    """Run the Pygame frontend."""
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
        draw_side_panel(state)

        buttons = []

        buttons.append(Button(790, 780, 150, 48, "Roll Dice", GREEN, lambda: roll_current_player(game)))
        buttons.append(Button(955, 780, 130, 48, "Buy", PINK, lambda: choose_buy_property(game)))
        buttons.append(Button(1100, 780, 130, 48, "Skip", YELLOW, lambda: choose_skip_property(game)))
        buttons.append(Button(40, 780, 150, 48, "End Turn", BLUE, lambda: end_turn(game)))

        for button in buttons:
            button.draw()

        if state["winner"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))

            draw_text("GAME OVER", BIG_FONT, BLACK, 545, 350)
            draw_text(f"{state['winner']} wins!", MID_FONT, PINK, 565, 410)

        pygame.display.flip()


if __name__ == "__main__":
    main()