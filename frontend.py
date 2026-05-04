# frontend.py
# Polished Pygame frontend for Monopoly.
# Backend handles the game rules. This file handles the visual interface.

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

WIDTH = 1350
HEIGHT = 850

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monopoly Simulator")
clock = pygame.time.Clock()


# ============================================================
# COLORS + FONTS
# ============================================================

BG = (232, 245, 230)
BOARD_GREEN = (207, 231, 204)
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
    None: (210, 210, 210)
}

PLAYER_COLORS = [
    (235, 76, 76),
    (70, 125, 255),
    (78, 185, 110),
    (245, 180, 55),
    (150, 90, 220),
    (45, 185, 185)
]

TITLE_FONT = pygame.font.SysFont("arial", 42, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 32, bold=True)
MID_FONT = pygame.font.SysFont("arial", 22, bold=True)
FONT = pygame.font.SysFont("arial", 17)
SMALL_FONT = pygame.font.SysFont("arial", 12)
TINY_FONT = pygame.font.SysFont("arial", 10)


# ============================================================
# BUTTON
# ============================================================

class Button:
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


# ============================================================
# TEXT HELPERS
# ============================================================

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
    )


# ============================================================
# BOARD COORDINATES
# ============================================================

BOARD_X = 40
BOARD_Y = 40
CELL = 70
BOARD_SIZE = CELL * 11


def get_board_coordinates():
    coords = {}

    # Bottom row: 0-10
    for i in range(11):
        coords[i] = (BOARD_X + (10 - i) * CELL, BOARD_Y + 10 * CELL)

    # Left side: 11-20
    for i in range(11, 21):
        coords[i] = (BOARD_X, BOARD_Y + (20 - i) * CELL)

    # Top row: 21-30
    for i in range(21, 31):
        coords[i] = (BOARD_X + (i - 20) * CELL, BOARD_Y)

    # Right side: 31-39
    for i in range(31, 40):
        coords[i] = (BOARD_X + 10 * CELL, BOARD_Y + (i - 30) * CELL)

    return coords


BOARD_COORDS = get_board_coordinates()


# ============================================================
# UI STATUS TEXT
# ============================================================

def get_instruction(state):
    if state["winner"]:
        return "Game over."

    if state["pending_action"]:
        prop = state["pending_action"]["property"]
        price = state["pending_action"]["price"]
        return f"{prop} is unowned and costs ${price}. Choose Buy or Skip."

    if not state["has_rolled"]:
        return f"{state['current_player']}, click Roll Dice to start your turn."

    return "You have finished rolling. Click End Turn to pass to the next player."


# ============================================================
# DRAW BOARD
# ============================================================

def draw_board(state):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)

    pygame.draw.rect(screen, BOARD_GREEN, board_rect)
    pygame.draw.rect(screen, BLACK, board_rect, 4)

    # Inner center area
    inner = pygame.Rect(BOARD_X + CELL, BOARD_Y + CELL, CELL * 9, CELL * 9)
    pygame.draw.rect(screen, BOARD_GREEN, inner)
    pygame.draw.rect(screen, BLACK, inner, 3)

    # Center logo area
    logo_rect = pygame.Rect(BOARD_X + 235, BOARD_Y + 320, 310, 90)
    pygame.draw.rect(screen, RED, logo_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, logo_rect, 3, border_radius=8)
    draw_text("MONOPOLY", TITLE_FONT, WHITE, logo_rect.x + 38, logo_rect.y + 20)

    draw_text("PROPERTY TRADING GAME", SMALL_FONT, DARK_GRAY, BOARD_X + 280, BOARD_Y + 420)

    # Player position map
    position_map = {}
    for idx, player in enumerate(state["players"]):
        position_map.setdefault(player["position"], []).append((idx, player))

    for i, space in enumerate(BOARD):
        x, y = BOARD_COORDS[i]
        rect = pygame.Rect(x, y, CELL, CELL)

        # Space background
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        # Property color strip
        if space in PROPERTY_DATA:
            color = PROPERTY_COLORS.get(PROPERTY_DATA[space]["color"], GRAY)
            prop_type = PROPERTY_DATA[space]["type"]

            if prop_type == "property":
                strip = pygame.Rect(x, y, CELL, 14)
                pygame.draw.rect(screen, color, strip)
                pygame.draw.rect(screen, BLACK, strip, 1)
            else:
                pygame.draw.rect(screen, color, rect)

        # Space text
        draw_text(i, TINY_FONT, BLACK, x + 4, y + 3)

        name_lines = wrap_text(short_name(space), TINY_FONT, 58)

        for line_i, line in enumerate(name_lines[:4]):
            draw_text(line, TINY_FONT, BLACK, x + 5, y + 18 + line_i * 11)

        # Price
        if space in PROPERTY_DATA:
            price = PROPERTY_DATA[space]["price"]
            draw_text(f"${price}", TINY_FONT, BLACK, x + 5, y + 56)

        # Tokens
        if i in position_map:
            for token_i, (player_i, player) in enumerate(position_map[i]):
                token_x = x + 14 + (token_i % 3) * 17
                token_y = y + 52 - (token_i // 3) * 15

                pygame.draw.circle(
                    screen,
                    PLAYER_COLORS[player_i % len(PLAYER_COLORS)],
                    (token_x, token_y),
                    8
                )
                pygame.draw.circle(screen, BLACK, (token_x, token_y), 8, 2)


# ============================================================
# DRAW DASHBOARD
# ============================================================

def draw_dashboard(state):
    panel_x = 850
    panel_y = 40
    panel_w = 455
    panel_h = 650

    pygame.draw.rect(screen, PAPER, (panel_x, panel_y, panel_w, panel_h), border_radius=28)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=28)

    draw_text("Game Dashboard", BIG_FONT, BLACK, panel_x + 28, panel_y + 24)

    draw_text(
        f"Current Player: {state['current_player']}",
        MID_FONT,
        PINK,
        panel_x + 28,
        panel_y + 75
    )

    # Instruction card
    instruction = get_instruction(state)
    instr_rect = pygame.Rect(panel_x + 28, panel_y + 112, 398, 70)

    pygame.draw.rect(screen, LIGHT_PINK, instr_rect, border_radius=16)
    draw_wrapped(instruction, FONT, BLACK, instr_rect.x + 16, instr_rect.y + 14, 365, 20)

    # Dice card
    dice_rect = pygame.Rect(panel_x + 28, panel_y + 195, 398, 48)
    pygame.draw.rect(screen, (255, 245, 220), dice_rect, border_radius=14)

    if state["last_roll"]:
        d1, d2 = state["last_roll"]
        dice_text = f"Last Roll: {d1} + {d2} = {d1 + d2}"
    else:
        dice_text = "Last Roll: none"

    draw_text(dice_text, FONT, BLACK, dice_rect.x + 16, dice_rect.y + 14)

    # Players
    draw_text("Players", MID_FONT, BLACK, panel_x + 28, panel_y + 265)

    y = panel_y + 302

    for idx, player in enumerate(state["players"]):
        card_rect = pygame.Rect(panel_x + 28, y, 398, 78)

        pygame.draw.rect(screen, WHITE, card_rect, border_radius=16)
        pygame.draw.rect(
            screen,
            PLAYER_COLORS[idx % len(PLAYER_COLORS)],
            card_rect,
            3,
            border_radius=16
        )

        draw_text(player["name"], FONT, BLACK, card_rect.x + 14, card_rect.y + 8)
        draw_text(f"Money: ${player['money']}", SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 32)
        draw_text(f"Location: {player['space']}", SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 49)
        draw_text(f"Props: {len(player['properties'])}", SMALL_FONT, BLACK, card_rect.x + 305, card_rect.y + 32)

        y += 88

        if y > panel_y + 505:
            break

    # Event feed
    feed_rect = pygame.Rect(panel_x + 28, panel_y + 535, 398, 95)
    pygame.draw.rect(screen, (250, 250, 250), feed_rect, border_radius=14)
    pygame.draw.rect(screen, GRAY, feed_rect, 2, border_radius=14)

    draw_text("Feed", FONT, BLACK, feed_rect.x + 14, feed_rect.y + 8)

    log_y = feed_rect.y + 30
    recent_logs = [log for log in state["log"][-4:] if log.strip() != ""]

    if not recent_logs:
        draw_text("No moves yet.", SMALL_FONT, DARK_GRAY, feed_rect.x + 14, log_y)
    else:
        for log in recent_logs:
            draw_wrapped("- " + log, SMALL_FONT, BLACK, feed_rect.x + 14, log_y, 360, 14)
            log_y += 28


# ============================================================
# DRAW CONTROL BAR
# ============================================================

def draw_buttons(buttons):
    for button in buttons:
        button.draw()


def draw_control_bar():
    pygame.draw.rect(screen, PAPER, (40, 720, 1265, 90), border_radius=24)
    pygame.draw.rect(screen, BLACK, (40, 720, 1265, 90), 3, border_radius=24)

    draw_text("Controls", MID_FONT, BLACK, 70, 750)


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(input_text):
    screen.fill(BG)

    card = pygame.Rect(320, 170, 700, 400)
    pygame.draw.rect(screen, PAPER, card, border_radius=30)
    pygame.draw.rect(screen, BLACK, card, 3, border_radius=30)

    draw_text("MONOPOLY SIMULATOR", TITLE_FONT, BLACK, 455, 230)
    draw_text("Enter player names separated by commas", MID_FONT, DARK_GRAY, 455, 295)

    input_box = pygame.Rect(420, 360, 500, 60)
    pygame.draw.rect(screen, WHITE, input_box, border_radius=16)
    pygame.draw.rect(screen, PINK, input_box, 3, border_radius=16)

    draw_text(input_text, FONT, BLACK, input_box.x + 16, input_box.y + 19)

    draw_text("Example: luke, louis, andy", FONT, DARK_GRAY, 525, 445)
    draw_text("Press ENTER to start", MID_FONT, PINK, 545, 490)


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

        buttons = [
            Button(205, 742, 150, 46, "Roll Dice", GREEN, lambda: roll_current_player(game)),
            Button(375, 742, 120, 46, "Buy", PINK, lambda: choose_buy_property(game)),
            Button(515, 742, 120, 46, "Skip", YELLOW, lambda: choose_skip_property(game)),
            Button(655, 742, 150, 46, "End Turn", BLUE, lambda: end_turn(game)),
        ]

        draw_buttons(buttons)

        if state["winner"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))

            draw_text("GAME OVER", TITLE_FONT, BLACK, 540, 350)
            draw_text(f"{state['winner']} wins!", MID_FONT, PINK, 565, 410)

        pygame.display.flip()


if __name__ == "__main__":
    main()