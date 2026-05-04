# Monopoly CS32 Final Project

## Project Description

This project is a fully interactive digital version of Monopoly built in Python.  
Our program recreates the core mechanics of the game, including player turns, dice rolls, movement around the board, passing Go, buying properties, paying rent, drawing Chance and Community Chest cards, going to jail, paying taxes, building houses, and bankruptcy.

The project consists of:
- A modular backend that handles all game rules and state
- A Pygame frontend that provides a visual, interactive interface

Players can interact with the game through buttons (Roll, Buy, Skip, End Turn), and the UI updates in real time to reflect game state changes.

---

## Features

### Core Gameplay
- Create multiple players with starting money and position
- Roll dice and move around the board
- Collect $200 for passing Go
- Buy unowned properties
- Pay rent on owned properties
- Handle railroads and utilities
- Draw Chance and Community Chest cards
- Handle Income Tax and Luxury Tax
- Send players to jail and process jail turns
- Detect bankruptcy
- Determine when the game is over

### Advanced Features
- Modular backend split into:
  - board.py
  - player.py
  - cards.py
  - game.py
- Interactive Pygame frontend
- Visual Monopoly-style board
- Player tokens displayed on board
- Dice roll system with animation
- Event feed showing game actions
- Buy / Skip property system (no auto-play)
- House building system (for full color sets)
- Dynamic UI that updates based on game state

---

## Project Structure

backend/
    board.py
    player.py
    cards.py
    game.py
frontend.py
README.md

---

## Installing Pygame

Before running the game, you need to install Pygame.

Run this in your terminal:

python3 -m pip install pygame

If that doesn’t work, try:

pip3 install pygame

---

## Verifying Installation

You can test if Pygame installed correctly by running:

python3 -c "import pygame; print(pygame.__version__)"

If it prints a version number, Pygame is installed correctly.

---

## How to Run the Code

Run the full interactive game:

python3 frontend.py

---

## Important Note

The Pygame interface must be run locally on your computer.

It will NOT display properly in cloud environments such as:
- GitHub Codespaces
- Online IDEs

If you try to run it there, you will only see:

pygame 2.x.x  
Hello from the pygame community...

and no game window will appear.

To properly run the game, download the project to your computer and run:

python3 frontend.py

---

## Design Overview

### Inputs
- Player names
- User actions (Roll Dice, Buy, Skip, End Turn, Build House)

### Outputs
- Updated board state
- Player positions
- Money and property ownership
- Event log
- Winner (when game ends)

### Logical Components
- Backend processes game logic
- Frontend displays state and handles user interaction
- Game state is shared between backend and frontend

---

## External Contributors / Sources

We used ChatGPT as a development tool to assist with:
- Debugging Python logic
- Refactoring backend into a modular structure
- Designing and improving the Pygame user interface
- Implementing animations (dice rolling, UI updates)
- Fixing layout and spacing issues in the frontend

A significant portion of the UI improvements, debugging, and animation logic in Pygame was developed with the help of ChatGPT.

All code suggestions were:
- Carefully reviewed
- Tested by our team
- Modified as needed to fit our project design

ChatGPT was used as a tool to accelerate development, but we ensured full understanding of all implemented features.

---

## Future Improvements

If we continued working on this project, we would add:
- Full Monopoly rules (hotels, trading, auctions)
- Multiplayer networking
- Save/load game functionality
- Improved animations (token movement, card flips)
- More polished UI and sound effects

---

## Summary

This project demonstrates how to build a modular software system with a Python backend and a graphical frontend.  
We combined data structures, algorithms, and UI design to recreate a complex board game in an interactive digital format.