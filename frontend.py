 # frontend.py

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


pygame.init()

WIDTH = 1380
HEIGHT = 860

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

TITLE_FONT = pygame.font.SysFont("arial", 38, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 28, bold=True)
MID_FONT = pygame.font.SysFont("arial", 20, bold=True)
FONT = pygame.font.SysFont("arial", 15)
SMALL_FONT = pygame.font.SysFont("arial", 11)
TINY_FONT = pygame.font.SysFont("arial", 9)


# ============================================================
# BOARD LAYOUT
# ============================================================

BOARD_X = 55
BOARD_Y = 45
CELL = 60
BOARD_SIZE = CELL * 11


def get_board_coordinates():
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
# HELPERS
# ============================================================

class Button:
    def __init__(self, x, y, w, h, text, color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = self.color

        if self.rect.collidepoint(mouse):
            color = tuple(min(255, c + 20) for c in color)

        pygame.draw.rect(screen, color, self.rect, border_radius=16)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=16)

        label = MID_FONT.render(self.text, True, BLACK)
        screen.blit(label, label.get_rect(center=self.rect.center))

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


def draw_wrapped(text, font, color, x, y, max_width, line_height, max_lines=None):
    lines = wrap_text(text, font, max_width)

    if max_lines:
        lines = lines[:max_lines]

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
    if state["winner"]:
        return "Game over."

    if state["pending_action"]:
        prop = state["pending_action"]["property"]
        price = state["pending_action"]["price"]
        return f"{prop} is unowned and costs ${price}. Choose Buy or Skip."

    if not state["has_rolled"]:
        return f"{state['current_player']}, click Roll to start your turn."

    return "You rolled already. Click End to pass to the next player."


# ============================================================
# DICE
# ============================================================

dice_animation_end = 0
animated_dice = (1, 1)


def start_dice_animation():
    global dice_animation_end
    dice_animation_end = time.time() + 0.6


def get_display_dice(state):
    global animated_dice

    if time.time() < dice_animation_end:
        animated_dice = (random.randint(1, 6), random.randint(1, 6))
        return animated_dice

    if state["last_roll"]:
        return state["last_roll"]

    return None


def draw_die(x, y, value):
    rect = pygame.Rect(x, y, 42, 42)
    pygame.draw.rect(screen, WHITE, rect, border_radius=9)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=9)

    dots = {
        1: [(21, 21)],
        2: [(13, 13), (29, 29)],
        3: [(13, 13), (21, 21), (29, 29)],
        4: [(13, 13), (29, 13), (13, 29), (29, 29)],
        5: [(13, 13), (29, 13), (21, 21), (13, 29), (29, 29)],
        6: [(13, 11), (29, 11), (13, 21), (29, 21), (13, 31), (29, 31)],
    }

    for dx, dy in dots[value]:
        pygame.draw.circle(screen, BLACK, (x + dx, y + dy), 4)


# ============================================================
# BOARD
# ============================================================

def draw_board(state):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)

    pygame.draw.rect(screen, BOARD_GREEN, board_rect)
    pygame.draw.rect(screen, BLACK, board_rect, 4)

    inner = pygame.Rect(BOARD_X + CELL, BOARD_Y + CELL, CELL * 9, CELL * 9)
    pygame.draw.rect(screen, BOARD_GREEN, inner)
    pygame.draw.rect(screen, BLACK, inner, 3)

    logo_rect = pygame.Rect(BOARD_X + 205, BOARD_Y + 275, 250, 72)
    pygame.draw.rect(screen, RED, logo_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, logo_rect, 3, border_radius=8)
    draw_text("MONOPOLY", BIG_FONT, WHITE, logo_rect.x + 42, logo_rect.y + 20)
    draw_text("PROPERTY TRADING GAME", SMALL_FONT, DARK_GRAY, BOARD_X + 225, BOARD_Y + 365)

    pygame.draw.rect(screen, (151, 220, 240), (BOARD_X + 130, BOARD_Y + 150, 125, 78), border_radius=8)
    pygame.draw.rect(screen, BLACK, (BOARD_X + 130, BOARD_Y + 150, 125, 78), 2, border_radius=8)
    draw_text("CHEST", MID_FONT, BLACK, BOARD_X + 160, BOARD_Y + 180)

    pygame.draw.rect(screen, ORANGE, (BOARD_X + 420, BOARD_Y + 445, 125, 78), border_radius=8)
    pygame.draw.rect(screen, BLACK, (BOARD_X + 420, BOARD_Y + 445, 125, 78), 2, border_radius=8)
    draw_text("?", TITLE_FONT, WHITE, BOARD_X + 470, BOARD_Y + 458)

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
                strip = pygame.Rect(x, y, CELL, 12)
                pygame.draw.rect(screen, color, strip)
                pygame.draw.rect(screen, BLACK, strip, 1)
            else:
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)

        draw_text(i, TINY_FONT, BLACK, x + 3, y + 2)

        name_lines = wrap_text(short_name(space), TINY_FONT, 52)
        for line_i, line in enumerate(name_lines[:4]):
            draw_text(line, TINY_FONT, BLACK, x + 4, y + 14 + line_i * 10)

        if space in PROPERTY_DATA:
            draw_text(f"${PROPERTY_DATA[space]['price']}", TINY_FONT, BLACK, x + 4, y + 50)

        houses = state.get("houses", {})
        for h in range(houses.get(space, 0)):
            house_x = x + 6 + h * 10
            house_y = y + 36
            pygame.draw.rect(screen, GREEN, (house_x, house_y, 8, 8))
            pygame.draw.rect(screen, BLACK, (house_x, house_y, 8, 8), 1)

        if i in position_map:
            for token_i, (player_i, _) in enumerate(position_map[i]):
                token_x = x + 12 + (token_i % 3) * 13
                token_y = y + 52 - (token_i // 3) * 12

                pygame.draw.circle(screen, PLAYER_COLORS[player_i % len(PLAYER_COLORS)], (token_x, token_y), 6)
                pygame.draw.circle(screen, BLACK, (token_x, token_y), 6, 2)


# ============================================================
# DASHBOARD
# ============================================================

def draw_dashboard(state):
    panel_x = 760
    panel_y = 45
    panel_w = 575
    panel_h = 600

    pygame.draw.rect(screen, PAPER, (panel_x, panel_y, panel_w, panel_h), border_radius=26)
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=26)

    draw_text("Game Dashboard", BIG_FONT, BLACK, panel_x + 26, panel_y + 22)
    draw_text(f"Current Player: {state['current_player']}", MID_FONT, PINK, panel_x + 26, panel_y + 66)

    instruction = get_instruction(state)
    instr_rect = pygame.Rect(panel_x + 26, panel_y + 102, 520, 60)
    pygame.draw.rect(screen, LIGHT_PINK, instr_rect, border_radius=14)
    draw_wrapped(instruction, FONT, BLACK, instr_rect.x + 14, instr_rect.y + 10, 490, 18, max_lines=2)

    dice_rect = pygame.Rect(panel_x + 26, panel_y + 178, 240, 62)
    pygame.draw.rect(screen, (255, 245, 220), dice_rect, border_radius=14)
    pygame.draw.rect(screen, GRAY, dice_rect, 2, border_radius=14)
    draw_text("Dice", FONT, BLACK, dice_rect.x + 14, dice_rect.y + 8)

    dice = get_display_dice(state)
    if dice:
        d1, d2 = dice
        draw_die(dice_rect.x + 78, dice_rect.y + 10, d1)
        draw_die(dice_rect.x + 130, dice_rect.y + 10, d2)
    else:
        draw_text("No roll yet", FONT, DARK_GRAY, dice_rect.x + 78, dice_rect.y + 34)

    card_rect = pygame.Rect(panel_x + 286, panel_y + 178, 260, 62)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=14)
    pygame.draw.rect(screen, PINK, card_rect, 2, border_radius=14)

    if state.get("current_card"):
        draw_text("Card Drawn", FONT, BLACK, card_rect.x + 14, card_rect.y + 7)
        draw_wrapped(state["current_card"]["text"], SMALL_FONT, BLACK, card_rect.x + 14, card_rect.y + 30, 230, 13, max_lines=2)
    else:
        draw_text("Card", FONT, BLACK, card_rect.x + 14, card_rect.y + 7)
        draw_text("No card drawn", SMALL_FONT, DARK_GRAY, card_rect.x + 14, card_rect.y + 33)

    draw_text("Players", MID_FONT, BLACK, panel_x + 26, panel_y + 258)

    y = panel_y + 292
    for idx, player in enumerate(state["players"]):
        card = pygame.Rect(panel_x + 26, y, 520, 58)

        pygame.draw.rect(screen, WHITE, card, border_radius=14)
        pygame.draw.rect(screen, PLAYER_COLORS[idx % len(PLAYER_COLORS)], card, 3, border_radius=14)

        draw_text(player["name"], FONT, BLACK, card.x + 12, card.y + 6)
        draw_text(f"${player['money']}", SMALL_FONT, BLACK, card.x + 12, card.y + 31)
        draw_text(f"At: {player['space']}", SMALL_FONT, BLACK, card.x + 88, card.y + 31)
        draw_text(f"Props: {len(player['properties'])}", SMALL_FONT, BLACK, card.x + 420, card.y + 31)

        y += 66
        if y > panel_y + 470:
            break

    feed = pygame.Rect(panel_x + 26, panel_y + 490, 520, 82)
    pygame.draw.rect(screen, (250, 250, 250), feed, border_radius=14)
    pygame.draw.rect(screen, GRAY, feed, 2, border_radius=14)
    draw_text("Feed", FONT, BLACK, feed.x + 14, feed.y + 8)

    logs = [log for log in state["log"][-3:] if log.strip()]
    log_y = feed.y + 28

    if not logs:
        draw_text("No moves yet.", SMALL_FONT, DARK_GRAY, feed.x + 14, log_y)
    else:
        for log in logs:
            draw_wrapped("- " + log, SMALL_FONT, BLACK, feed.x + 14, log_y, 480, 13, max_lines=1)
            log_y += 17


# ============================================================
# ACTIONS + CONTROLS
# ============================================================

def draw_action_panel(state):
    action = state.get("pending_action")
    buildable = state.get("buildable_properties", [])

    panel = pygame.Rect(760, 665, 575, 100)
    pygame.draw.rect(screen, PAPER, panel, border_radius=20)
    pygame.draw.rect(screen, BLACK, panel, 2, border_radius=20)

    if action:
        prop = action["property"]
        price = action["price"]
        data = PROPERTY_DATA[prop]
        color = PROPERTY_COLORS.get(data["color"], GRAY)

        pygame.draw.rect(screen, color, (panel.x + 20, panel.y + 22, 58, 50), border_radius=8)
        pygame.draw.rect(screen, BLACK, (panel.x + 20, panel.y + 22, 58, 50), 2, border_radius=8)

        draw_text("Property Available", FONT, BLACK, panel.x + 95, panel.y + 18)
        draw_text(prop, SMALL_FONT, BLACK, panel.x + 95, panel.y + 42)
        draw_text(f"Price: ${price} | Rent: ${data['rent']}", SMALL_FONT, DARK_GRAY, panel.x + 335, panel.y + 42)

    elif buildable:
        draw_text("Build Houses", FONT, BLACK, panel.x + 20, panel.y + 18)
        draw_text("You own a full color set. Build options appear below.", SMALL_FONT, DARK_GRAY, panel.x + 20, panel.y + 43)

    else:
        draw_text("Property Actions", FONT, BLACK, panel.x + 20, panel.y + 18)
        draw_text("Buy, skip, and house-building actions will appear here.", SMALL_FONT, DARK_GRAY, panel.x + 20, panel.y + 43)


def draw_control_bar():
    panel = pygame.Rect(55, 725, 660, 70)
    pygame.draw.rect(screen, PAPER, panel, border_radius=20)
    pygame.draw.rect(screen, BLACK, panel, 2, border_radius=20)
    draw_text("Controls", MID_FONT, BLACK, panel.x + 20, panel.y + 22)


def draw_buttons(buttons):
    for button in buttons:
        button.draw()


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(input_text):
    screen.fill(BG)

    card = pygame.Rect(350, 185, 680, 370)
    pygame.draw.rect(screen, PAPER, card, border_radius=28)
    pygame.draw.rect(screen, BLACK, card, 3, border_radius=28)

    draw_text("MONOPOLY SIMULATOR", TITLE_FONT, BLACK, 475, 245)
    draw_text("Enter player names separated by commas", MID_FONT, DARK_GRAY, 470, 310)

    input_box = pygame.Rect(440, 375, 500, 55)
    pygame.draw.rect(screen, WHITE, input_box, border_radius=16)
    pygame.draw.rect(screen, PINK, input_box, 3, border_radius=16)

    draw_text(input_text, FONT, BLACK, input_box.x + 16, input_box.y + 18)

    draw_text("Example: luke, louis, andy", FONT, DARK_GRAY, 565, 460)
    draw_text("Press ENTER to start", MID_FONT, PINK, 585, 500)


# ============================================================
# MAIN
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
        draw_action_panel(state)
        draw_control_bar()

        buttons = [
            Button(195, 742, 115, 38, "Roll", GREEN, lambda: [start_dice_animation(), roll_current_player(game)]),
            Button(330, 742, 85, 38, "Buy", PINK, lambda: choose_buy_property(game)),
            Button(435, 742, 85, 38, "Skip", YELLOW, lambda: choose_skip_property(game)),
            Button(540, 742, 105, 38, "End", BLUE, lambda: end_turn(game)),
        ]

        buildable = state.get("buildable_properties", [])
        start_x = 960

        for i, prop in enumerate(buildable[:2]):
            buttons.append(
                Button(
                    start_x + i * 155,
                    727,
                    140,
                    34,
                    short_name(prop),
                    GREEN,
                    lambda p=prop: buy_house(game, p),
                )
            )

        draw_buttons(buttons)

        if state["winner"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))

            draw_text("GAME OVER", TITLE_FONT, BLACK, 550, 360)
            draw_text(f"{state['winner']} wins!", MID_FONT, PINK, 570, 415)

        pygame.display.flip()


if __name__ == "__main__":
    main()