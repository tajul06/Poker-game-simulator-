#taibur 's code
# main.py
"""
Texas Hold'em Poker Game - Main Controller
Shortened & updated version
"""

import sys
import os
import time

# Add support directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'support'))

from game_logic import Player, GameState
from expectiminimax import ExpectiminimaxAI, SimpleAI
from cli_interface import PokerCLI


def main():
    cli = PokerCLI()

    # --- Setup Players ---
    player_name = cli.get_input("Enter your name: ")
    human = Player(player_name, chips=1000, is_human=True)
    ai = Player("AI Bot", chips=1000, is_human=False)
    players = [human, ai]
    ai_brains = {ai: ExpectiminimaxAI(ai, depth=2)}

    game = GameState(players)
    hand_number = 0
    blinds = {'small': 25, 'big': 50}

    try:
        while len([p for p in players if p.chips > 0]) > 1:
            hand_number += 1
            cli.print_colored(f"\n🃏 Starting Hand #{hand_number}", 'cyan', bold=True)
            game.start_new_hand()

            # --- Post Blinds ---
            for idx, blind in enumerate(['small', 'big']):
                p = players[idx]
                amount = min(blinds[blind], p.chips)
                p.bet(amount)
                cli.print_colored(f"{blind.capitalize()} Blind: {p.name} - ${amount}", 'yellow')
            game.current_player = 0

            # --- Betting Rounds ---
            for round_name, cards_to_deal in [("Pre-flop", 0), ("Flop", 3), ("Turn", 1), ("River", 1)]:
                if cards_to_deal > 0:
                    game.deal_community_cards(cards_to_deal)
                cli.print_colored(f"\n🎲 {round_name} Round", 'blue', bold=True)

                for p in [pl for pl in players if not pl.folded and pl.chips > 0]:
                    if p.is_human:
                        action, amount = cli.get_player_action(game, p)
                    else:
                        action, amount = ai_brains[p].get_action(game)
                        cli.show_ai_action(p, action, amount)
                        time.sleep(1)

                    if action == "fold":
                        p.fold()
                    else:
                        p.bet(min(amount, p.chips))

                if len([p for p in players if not p.folded and p.chips > 0]) <= 1:
                    break

            # --- Showdown ---
            active_players = [p for p in players if not p.folded]
            cli.print_colored("\n🎭 SHOWDOWN", 'magenta', bold=True)
            for p in active_players:
                cli.print_player_info(p, show_cards=True)

            winners = game.get_winners()
            total_pot = game.pot + sum(p.current_bet for p in players)
            split_amount = total_pot // len(winners) if winners else 0

            for winner, hand_rank, _ in winners:
                winner.chips += split_amount
                cli.show_hand_result(winner, hand_rank, winner.hole_cards, game.community_cards)

            # --- Remove eliminated players ---
            for p in players[:]:
                if p.chips == 0:
                    cli.print_colored(f"💀 {p.name} eliminated!", 'red')
                    players.remove(p)

            cli.wait_for_enter("Press Enter to continue...")

        cli.show_game_over(players)

    except KeyboardInterrupt:
        cli.print_colored("\n🛑 Game interrupted!", 'red')


if __name__ == "__main__":
    sys.exit(main())
