"""
Texas Hold'em Poker - Controller
Author: Team Member 4
Short: Manages game loop, players, and module integration
"""

import sys
import os
import time
from typing import List, Tuple

# Add 'support' folder to sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'support'))

from support.game_logic import Player, GameState, Deck
from support.expectiminimax import ExpectiminimaxAI, SimpleAI
from support.cli_interface import PokerCLI


class PokerGameController:
    """Controller for a single poker session"""
    
    def __init__(self):
        # CLI helper
        self.cli = PokerCLI()
        # Player list
        self.players = []
        # Current game state
        self.game_state = None
        # Map Player -> AI
        self.ai_players = {}
        # Hand counter
        self.hand_number = 0
        # Blinds amounts
        self.blinds = {'small': 25, 'big': 50}
    
    def start_game(self):
        """Start the game loop"""
        try:
            # Read settings from user
            settings = self.cli.get_game_settings()
            # Build players
            self._setup_players(settings)
            # Create game state
            self.game_state = GameState(self.players)
            # Run game loop
            self._game_loop()
        except KeyboardInterrupt:
            self.cli.print_colored("\n\n🛑 Game interrupted by user", 'red')
        except Exception as e:
            self.cli.print_colored(f"\n❌ An error occurred: {e}", 'red')
        finally:
            self._cleanup()
    
    def _setup_players(self, settings: dict):
        """Create human and AI players"""
        # Human player
        human_player = Player(
            name=settings['player_name'],
            chips=settings['starting_chips'],
            is_human=True
        )
        self.players.append(human_player)
        
        # AI players
        ai_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        for i in range(settings['num_ai']):
            ai_player = Player(
                name=ai_names[i],
                chips=settings['starting_chips'],
                is_human=False
            )
            self.players.append(ai_player)
            # Assign AI by difficulty
            if settings['ai_difficulty'] == 'hard':
                self.ai_players[ai_player] = ExpectiminimaxAI(ai_player, depth=3)
            else:
                self.ai_players[ai_player] = SimpleAI(ai_player)
        
        self.cli.print_colored(f"\n✅ Game setup complete with {len(self.players)} players!", 'green')
        self.cli.wait_for_enter()
    
    def _game_loop(self):
        """Run hands until game ends"""
        while not self._is_game_over():
            self.hand_number += 1
            self.cli.print_colored(f"\n🃏 Starting Hand #{self.hand_number}", 'cyan', bold=True)
            # Play one hand
            self._play_hand()
            # Show summary
            self._show_hand_results()
            # Remove busted players
            self._eliminate_players()
            # Ask to continue
            if not self._is_game_over():
                if not self._should_continue():
                    break
        # Final screen
        self.cli.show_game_over(self.players)
    
    def _play_hand(self):
        """Execute all phases of a hand"""
        # Reset and deal
        self.game_state.start_new_hand()
        # Blinds
        self._post_blinds()
        # Pre-flop
        self._betting_round("Pre-flop")
        if len(self.game_state.get_active_players()) <= 1:
            return
        # Flop
        self.game_state.deal_community_cards(3)
        self._betting_round("Flop")
        if len(self.game_state.get_active_players()) <= 1:
            return
        # Turn
        self.game_state.deal_community_cards(1)
        self._betting_round("Turn")
        if len(self.game_state.get_active_players()) <= 1:
            return
        # River
        self.game_state.deal_community_cards(1)
        self._betting_round("River")
        # Showdown if needed
        if len(self.game_state.get_active_players()) > 1:
            self._showdown()
    
    def _post_blinds(self):
        """Collect small and big blinds"""
        num_players = len(self.players)
        if num_players < 2:
            return
        # Find blind positions
        small_blind_pos = (self.game_state.dealer_position + 1) % num_players
        big_blind_pos = (self.game_state.dealer_position + 2) % num_players
        # Small blind
        small_blind_player = self.players[small_blind_pos]
        small_amount = min(self.blinds['small'], small_blind_player.chips)
        small_blind_player.bet(small_amount)
        self.game_state.current_bet = small_amount
        # Big blind
        big_blind_player = self.players[big_blind_pos]
        big_amount = min(self.blinds['big'], big_blind_player.chips)
        big_blind_player.bet(big_amount)
        self.game_state.current_bet = big_amount
        self.cli.print_colored(f"\n💰 Blinds Posted:", 'yellow')
        self.cli.print_colored(f"   Small Blind: {small_blind_player.name} - ${small_amount}", 'yellow')
        self.cli.print_colored(f"   Big Blind: {big_blind_player.name} - ${big_amount}", 'yellow')
        # First to act after big blind
        self.game_state.current_player = (big_blind_pos + 1) % num_players
    
    def _betting_round(self, round_name: str):
        """Handle a betting round"""
        self.cli.print_colored(f"\n🎲 {round_name} Betting Round", 'blue', bold=True)
        if round_name != "Pre-flop":
            # Move bets to pot and reset
            for player in self.players:
                self.game_state.pot += player.current_bet
                player.current_bet = 0
            self.game_state.current_bet = 0
            # First player is left of dealer
            self.game_state.current_player = (self.game_state.dealer_position + 1) % len(self.players)
        # Loop until bets settle
        betting_complete = False
        players_acted = set()
        last_bet_amount = self.game_state.current_bet
        max_rounds = len(self.players) * 4  # safety
        round_count = 0
        while not betting_complete and round_count < max_rounds:
            round_count += 1
            active_players = self.game_state.get_active_players()
            if len(active_players) <= 1:
                break
            current_player = self.players[self.game_state.current_player]
            # Skip folded or all-in
            if current_player.folded or current_player.all_in:
                self.game_state.current_player = (self.game_state.current_player + 1) % len(self.players)
                continue
            # Show state
            self.cli.print_game_state(self.game_state, current_player)
            # Get action
            if current_player.is_human:
                action, amount = self.cli.get_player_action(self.game_state, current_player)
            else:
                action, amount = self._get_ai_action(current_player)
                self.cli.show_ai_action(current_player, action, amount)
                time.sleep(2)
            # Apply action
            old_bet_amount = self.game_state.current_bet
            self._process_player_action(current_player, action, amount)
            players_acted.add(current_player)
            # If raised, reset who must act
            if self.game_state.current_bet > old_bet_amount:
                players_acted = {current_player}
            # Next player
            self.game_state.current_player = (self.game_state.current_player + 1) % len(self.players)
            # Check completion
            betting_complete = self._is_betting_round_complete(players_acted)
        if round_count >= max_rounds:
            self.cli.print_colored("⚠️  Betting round reached maximum rounds limit", 'yellow')
        # Summary
        self.cli.show_betting_summary(self.game_state)
        if not self.game_state.get_active_players()[0].is_human:
            self.cli.wait_for_enter("Press Enter to continue...")
    
    def _get_ai_action(self, ai_player: Player) -> Tuple[str, int]:
        """Decide AI action"""
        if ai_player in self.ai_players:
            return self.ai_players[ai_player].get_action(self.game_state)
        else:
            # fallback
            simple_ai = SimpleAI(ai_player)
            return simple_ai.get_action(self.game_state)
    
    def _process_player_action(self, player: Player, action: str, amount: int):
        """Execute player action"""
        if action == "fold":
            player.fold()
        elif action == "call":
            call_amount = self.game_state.current_bet - player.current_bet
            player.bet(min(call_amount, player.chips))
        elif action == "raise":
            # amount = total bet
            if player.bet(amount):
                self.game_state.current_bet = player.current_bet
            else:
                # go all-in if not enough
                player.bet(player.chips)
                self.game_state.current_bet = max(self.game_state.current_bet, player.current_bet)
    
    def _is_betting_round_complete(self, players_acted: set) -> bool:
        """Return True when betting is settled"""
        active_players = self.game_state.get_active_players()
        # Single player left
        if len(active_players) <= 1:
            return True
        # Some active players haven't acted
        active_not_acted = [p for p in active_players if p not in players_acted and not p.all_in]
        if active_not_acted:
            return False
        # Bets equal (ignoring all-in)
        active_bets = [p.current_bet for p in active_players if not p.all_in]
        return len(set(active_bets)) <= 1
    
    def _showdown(self):
        """Reveal hands and award pot"""
        self.cli.print_colored("\n🎭 SHOWDOWN", 'magenta', bold=True)
        # Reveal hands
        active_players = self.game_state.get_active_players()
        for player in active_players:
            self.cli.print_player_info(player, show_cards=True)
        self.cli.wait_for_enter("\nPress Enter to reveal the winner...")
        # Pick winners
        winners = self.game_state.get_winners()
        # Compute pot
        total_pot = self.game_state.pot + sum(p.current_bet for p in self.players)
        # Award
        if len(winners) == 1:
            winner = winners[0][0]
            winner.chips += total_pot
        else:
            split_amount = total_pot // len(winners)
            for winner, _, _ in winners:
                winner.chips += split_amount
        # Show results
        self.cli.show_winners(winners, total_pot)
        for winner, hand_rank, _ in winners:
            if hand_rank:
                self.cli.show_hand_result(winner, hand_rank, 
                                        winner.hole_cards, self.game_state.community_cards)
    
    def _show_hand_results(self):
        """Print hand summary and chips"""
        self.cli.print_colored(f"\n📊 Hand #{self.hand_number} Complete", 'green', bold=True)
        print("\nChip Counts:")
        for player in self.players:
            status = " (ELIMINATED)" if player.chips == 0 else ""
            print(f"  {player.name}: ${player.chips:,}{status}")
        self.cli.wait_for_enter()
    
    def _eliminate_players(self):
        """Remove players who ran out of chips"""
        eliminated = [p for p in self.players if p.chips == 0]
        for player in eliminated:
            self.cli.print_colored(f"💀 {player.name} has been eliminated!", 'red')
            self.players.remove(player)
            if player in self.ai_players:
                del self.ai_players[player]
    
    def _is_game_over(self) -> bool:
        """True when only one (or zero) players remain"""
        return len(self.players) <= 1
    
    def _should_continue(self) -> bool:
        """Ask player whether to keep playing"""
        return self.cli.get_yes_no_input("\nDo you want to play another hand?")
    
    def _cleanup(self):
        """Final messages and cleanup"""
        self.cli.print_colored("\n👋 Thanks for playing Texas Hold'em Poker!", 'cyan', bold=True)
        self.cli.print_colored("🎯 Game developed using Expectiminimax Algorithm", 'blue')


def main():
    """Program entry"""
    try:
        # Start controller
        game_controller = PokerGameController()
        game_controller.start_game()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
