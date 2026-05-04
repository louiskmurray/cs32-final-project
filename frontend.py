# frontend.py
# Beautiful Pygame frontend for Monopoly.
# Backend handles game rules. This file handles visuals and buttons.

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
# SETUP
# ============================================================

pygame.init()

WIDTH = 1150
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monopoly Simulator")
clock = pygame.time.Clock()


# ============================================================
# COLORS + FONTS
# ============================================================

CREAM = (248, 241, 230)
PAPER = (255, 252, 246)
BLACK = (35, 35, 35)
SOFT_BLACK = (70, 70, 70)
PINK = (246, 158, 199)
LIGHT_PINK = (255, 224, 239)
GREEN = (132, 203, 153)
BLUE = (132, 178, 240)
YELLOW = (252, 220, 128)
RED = (235, 96, 96)
GRAY = (220, 220, 220)
WHITE = (255, 255, 255)

PROPERTY_COLORS = {
    "brown": (154, 101, 58),
    "light blue": (142, 217, 232),
    "pink": (246, 158, 199),
    "orange": (246, 159, 83),
    "red": (235, 96, 96),
    "yellow": (250, 218, 93),
    "green": (102, 191, 115),
    "dark blue": (72, 100, 190),
    None: (210, 210, 210)
}

PLAYER_COLORS = [
    (239, 78, 78),
    (73, 125, 255),
    (78, 190, 117),
    (245, 177, 57),
    (159, 97, 230),
    (52, 190, 190)
]

TITLE_FONT = pygame.font.SysFont("arial", 34, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 28, bold=True)
MID_FONT = pygame.font.SysFont("arial", 21, bold=True)
FONT = pygame.font.SysFont("arial", 16)
SMALL_FONT = pygame.font.SysFont("arial", 11)


# ============================================================
# BUTTON
# ============================================================

class Button:
    """Clickable UI button."""

    def __init__(self, x, y, w, h, text, color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)

        draw_color = self.color
        if hover:
            draw_color = tuple(min(255, c + 18) for c in self.color)

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=18)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=18)

        label = MID_FONT.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ============================================================
# TEXT HELPERS
# ============================================================

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def wrap_text(text, font, max_width):
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


def draw_wrapped(text, font, color, x, y, max_width, line_height):
    lines = wrap_text(text, font, max_width)

    for i, line in enumerate(lines):
        draw_text(line, font, color, x, y + i * line_height)


# ============================================================
# BOARD COORDINATES
# ============================================================

def get_board_coordinates():
    coords = {}

    board_x = 40
    board_y = 40
    cell = 58

    # Bottom row: 0-10
    for i in range(11):
        coords[i] = (board_x + (10 - i) * cell, board_y + 10 * cell)

    # Left column: 11-20
    for i in range(11, 21):
        coords[i] = (board_x, board_y + (20 - i) * cell)

    # Top row: 21-30
    for i in range(21, 31):
        coords[i] = (board_x + (i - 20) * cell, board_y)

    # Right column: 31-39
    for i in range(31, 40):
        coords[i] = (board_x + 10 * cell, board_y + (i - 30) * cell)

    return coords


BOARD_COORDS = get_board_coordinates()


# ============================================================
# DRAWING
# ============================================================

def draw_board(state):
    cell = 58
    board_rect = pygame.Rect(35, 35, 648, 648)

    pygame.draw.rect(screen, PAPER, board_rect, border_radius=24)
    pygame.draw.rect(screen, BLACK, board_rect, 3, border_radius=24)

    # Center area
    pygame.draw.rect(screen, CREAM, (100, 100, 520, 520), border_radius=16)
    draw_text("MONOPOLY", TITLE_FONT, BLACK, 235, 315)
    draw_text("SIMULATOR", MID_FONT, SOFT_BLACK, 270, 355)

    # Player positions
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
        pygame.draw.rect(screen, color, rect, border_radius=3)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=3)

        draw_text(str(i), SMALL_FONT, BLACK, x + 4, y + 3)

        short_name = (
            space.replace("Railroad", "RR")
                 .replace("Community Chest", "Chest")
                 .replace("Mediterranean", "Med.")
                 .replace("Pennsylvania", "Penn.")
                 .replace("North Carolina", "N. Carolina")
        )

        lines = wrap_text(short_name, SMALL_FONT, 48)

        for line_index, line in enumerate(lines[:3]):
            draw_text(line, SMALL_FONT, BLACK, x + 4, y + 16 + line_index * 12)

        # Player tokens
        if i in position_map:
            for token_index, (player_index, player) in enumerate(position_map[i]):
                token_x = x + 12 + (token_index % 3) * 15
                token_y = y + 47 + (token_index // 3) * 10

                pygame.draw.circle(
                    screen,
                    PLAYER_COLORS[player_index % len(PLAYER_COLORS)],
                    (token_x, token_y),
                    7
                )
                pygame.draw.circle(screen, BLACK, (token_x, token_y), 7, 1)


def draw_dashboard(state):
    panel_x = 715
    panel_y = 35
    panel_w = 400
    panel_h = 590

    pygame.draw.rect(screen, PAPER, (panel_x, panel_y, panel_w, panel_h), border_radius=28)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=28)

    draw_text("Game Dashboard", BIG_FONT, BLACK, panel_x + 28, panel_y + 25)

    draw_text(
        f"Current Player: {state['current_player']}",
        MID_FONT,
        PINK,
        panel_x + 28,
        panel_y + 72
    )

    # Dice card
    dice_rect = pygame.Rect(panel_x + 28, panel_y + 108, 340, 48)
    pygame.draw.rect(screen, LIGHT_PINK, dice_rect, border_radius=14)

    if state["last_roll"]:
        d1, d2 = state["last_roll"]
        dice_text = f"🎲 Last Roll: {d1} + {d2} = {d1 + d2}"
    else:
        dice_text = "🎲 Last Roll: none"

    draw_text(dice_text, FONT, BLACK, dice_rect.x + 16, dice_rect.y + 14)

    # Pending action
    pending = state["pending_action"]
    action_y = panel_y + 174

    if pending:
        pygame.draw.rect(screen, (255, 245, 225), (panel_x + 28, action_y, 340, 62), border_radius=14)
        msg = f"{pending['property']} is available for ${pending['price']}. Buy or Skip?"
        draw_wrapped(msg, FONT, BLACK, panel_x + 42, action_y + 12, 310, 18)
    else:
        draw_text("No pending action.", FONT, SOFT_BLACK, panel_x + 28, action_y)

    draw_text("Players", MID_FONT, BLACK, panel_x + 28, panel_y + 255)

    y = panel_y + 292

    for idx, player in enumerate(state["players"]):
        card_rect = pygame.Rect(panel_x + 28, y, 340, 72)

        pygame.draw.rect(screen, WHITE, card_rect, border_radius=16)
        pygame.draw.rect(
            screen,
            PLAYER_COLORS[idx % len(PLAYER_COLORS)],
            card_rect,
            3,
            border_radius=16
        )

        draw_text(player["name"], FONT, BLACK, card_rect.x + 14, card_rect.y + 9)
        draw_text(f"Money: ${player['money']}", SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 32)
        draw_text(f"Location: {player['space']}", SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 48)
        draw_text(f"Props: {len(player['properties'])}", SMALL_FONT, BLACK, card_rect.x + 245, card_rect.y + 32)

        y += 82

    draw_text("Latest Events", MID_FONT, BLACK, panel_x + 28, panel_y + 520)

    log_y = panel_y + 550
    recent_logs = [log for log in state["log"][-4:] if log.strip() != ""]

    for log in recent_logs:
        draw_wrapped("- " + log, SMALL_FONT, BLACK, panel_x + 28, log_y, 340, 15)
        log_y += 30


def draw_buttons(buttons):
    for button in buttons:
        button.draw()


def draw_start_screen(input_text):
    screen.fill(CREAM)

    card = pygame.Rect(250, 150, 650, 360)
    pygame.draw.rect(screen, PAPER, card, border_radius=30)
    pygame.draw.rect(screen, BLACK, card, 3, border_radius=30)

    draw_text("MONOPOLY SIMULATOR", TITLE_FONT, BLACK, 365, 210)
    draw_text("Enter player names separated by commas", MID_FONT, SOFT_BLACK, 350, 270)

    input_box = pygame.Rect(330, 330, 490, 56)
    pygame.draw.rect(screen, WHITE, input_box, border_radius=16)
    pygame.draw.rect(screen, PINK, input_box, 3, border_radius=16)

    draw_text(input_text, FONT, BLACK, input_box.x + 16, input_box.y + 17)

    draw_text("Example: Luke, Koan, Andy", FONT, SOFT_BLACK, 455, 410)
    draw_text("Press ENTER to start", MID_FONT, PINK, 455, 450)


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

            # Press ESC to quit
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

        screen.fill(CREAM)

        draw_board(state)
        draw_dashboard(state)

        buttons = [
            Button(715, 650, 125, 46, "Roll", GREEN, lambda: roll_current_player(game)),
            Button(855, 650, 95, 46, "Buy", PINK, lambda: choose_buy_property(game)),
            Button(965, 650, 95, 46, "Skip", YELLOW, lambda: choose_skip_property(game)),
            Button(40, 650, 130, 46, "End Turn", BLUE, lambda: end_turn(game)),
        ]

        draw_buttons(buttons)

        if state["winner"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))

            draw_text("GAME OVER", TITLE_FONT, BLACK, 480, 300)
            draw_text(f"{state['winner']} wins!", MID_FONT, PINK, 490, 355)

        pygame.display.flip()


if __name__ == "__main__":
    main()