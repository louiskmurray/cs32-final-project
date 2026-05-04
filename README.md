# Monopoly CS32 Final Project

## Overview
This project is an interactive digital version of Monopoly built in Python. It automates core gameplay including turns, dice rolls, movement, passing Go, property buying, rent, cards, jail, taxes, houses, and bankruptcy, while providing a visual Pygame interface.

Players interact using buttons (Roll, Buy, Skip, End Turn), and the UI updates in real time.

---

## Features
- Multiplayer support (custom player names)
- Dice rolling and board movement with Go bonus
- Property purchasing and rent (including railroads and utilities)
- Chance and Community Chest cards
- Jail system and taxes
- Bankruptcy and win detection
- House building for full color sets
- Real-time event log and interactive UI

---

## Project Structure
backend/
  board.py
  player.py
  cards.py
  game.py
frontend.py

---

## Setup and Running

Install pygame:

python3 -m pip install pygame

Run the game:

python3 frontend.py

Note: The Pygame interface must be run locally. It will not display in environments like GitHub Codespaces or other online IDEs.

---

## Design Overview

Inputs:
- Player names
- User actions (Roll Dice, Buy, Skip, End Turn, Build House)

Outputs:
- Updated board state
- Player positions
- Money and property ownership
- Event log
- Winner (when the game ends)

Architecture:
- Backend (Python) handles all game logic and state
- Frontend (Pygame) renders the board and handles user interaction
- The frontend calls backend functions and displays the updated game state

---

## Collaboration

This project was developed collaboratively in person. We worked together on design, implementation, and debugging.

We also used a shared Google Colab-style workflow at times to test ideas and experiment with logic.

Luke handled most of the GitHub pushes since he had more experience with Git, but all group members contributed to the implementation, design decisions, and debugging.

---

## Use of Generative AI

We used ChatGPT as a development tool to assist with:
- Debugging Python code
- Refactoring the backend into a modular structure
- Improving the Pygame UI layout and spacing
- Implementing features like dice animation and UI behavior

These suggestions were used as starting points and were always reviewed, tested, and modified by our team.

We also used ChatGPT to help organize and refine this README.

---

## Future Improvements

- Full Monopoly rules (hotels, trading, auctions)
- Multiplayer support
- Save/load functionality
- Improved animations (token movement, card interactions)
- More polished UI and sound effects

---

## Summary

We built a modular Monopoly game with a Python backend and an interactive Pygame frontend, combining game logic, data structures, and UI design into a cohesive system.