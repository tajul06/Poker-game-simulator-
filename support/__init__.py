"""
Texas Hold'em Poker Game Simulator Package
Modular design with game logic, AI, and CLI components
"""

from .game_logic import Player, GameState, Card, Deck, HandEvaluator, HandRank
from .expectiminimax import ExpectiminimaxAI, SimpleAI, HandStrengthEvaluator
from .cli_interface import PokerCLI

__version__ = "1.0.0"
__author__ = "Team Members 1-4"
__description__ = "AI vs Human Texas Hold'em Poker using Expectiminimax Algorithm"

__all__ = [
    'Player', 'GameState', 'Card', 'Deck', 'HandEvaluator', 'HandRank',
    'ExpectiminimaxAI', 'SimpleAI', 'HandStrengthEvaluator',
    'PokerCLI'
]
