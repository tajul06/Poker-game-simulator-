#taibur 's code
# main.py
"""
Quick + dirty demo for Poker AI
Just runs one hand between AI and a dummy "human" player
"""

from support.game_logic import GameState, Player
from support.expectiminimax import ExpectiminimaxAI

def main():
    # --- Setup players ---
    human = Player("Human", chips=1000)
    ai = Player("AI Bot", chips=1000)

    # --- Game state ---
    game = GameState(players=[human, ai])

    # --- Attach an AI brain to the AI player ---
    ai_brain = ExpectiminimaxAI(depth=2)  # depth=2 = shallow tree for now

    # --- Start a hand ---
    game.start_new_hand()
    print("\n--- Hole Cards Dealt ---")
    for p in game.players:
        print(f"{p.name} hole cards: {p.hole_cards}")

    # --- Flop, Turn, River ---
    while game.round < 4:
        print(f"\n=== Round {game.round} ===")
        print("Community:", game.community_cards)

        # Human just checks/calls for now (lazy stub)
        if human.folded is False:
            human.bet(0)

        # AI decision
        move, amount = ai_brain.decide(game, ai)
        print(f"AI decides: {move} {amount}")
        if move == "fold":
            ai.fold()
        elif move == "bet":
            ai.bet(amount)

        # Move to next round
        game.advance_to_next_round()

    # --- Showdown ---
    winner = game.determine_winner()
    print("\n=== Showdown ===")
    if winner:
        print(f"Winner: {winner.name} with {winner.hole_cards}")
    else:
        print("No winner (everyone folded?)")

if __name__ == "__main__":
    main()
