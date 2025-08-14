"""
Texas Hold'em Poker Game Controller - Main Entry Point
Developed by: Team Member 4
Description: Orchestrates game flow, manages players, and coordinates all modules
"""

import sys
import os
import time
from typing import List, Tuple

# Add support directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'support'))

from support.game_logic import Player, GameState, Deck
from support.expectiminimax import ExpectiminimaxAI, SimpleAI
from support.cli_interface import PokerCLI


class PokerGameController:
    """
    Main game controller that manages the entire poker game session
    """
    
    def __init__(self):
        self.cli = PokerCLI()
        self.players = []
        self.game_state = None
        self.ai_players = {}  # Player -> AI instance mapping
        self.hand_number = 0
        self.blinds = {'small': 25, 'big': 50}
    
    def start_game(self):
        """Main entry point to start the poker game"""
        try:
            # Get game settings from user
            settings = self.cli.get_game_settings()
            
            # Initialize players
            self._setup_players(settings)
            
            # Initialize game state
            self.game_state = GameState(self.players)
            
            # Game loop
            self._game_loop()
            
        except KeyboardInterrupt:
            self.cli.print_colored("\n\n🛑 Game interrupted by user", 'red')
        except Exception as e:
            self.cli.print_colored(f"\n❌ An error occurred: {e}", 'red')
        finally:
            self._cleanup()
    
    def _setup_players(self, settings: dict):
        """Initialize all players (human and AI)"""
        # Create human player
        human_player = Player(
            name=settings['player_name'],
            chips=settings['starting_chips'],
            is_human=True
        )
        self.players.append(human_player)
        
        # Create AI players
        ai_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        for i in range(settings['num_ai']):
            ai_player = Player(
                name=ai_names[i],
                chips=settings['starting_chips'],
                is_human=False
            )
            self.players.append(ai_player)
            
            # Create AI instance based on difficulty
            if settings['ai_difficulty'] == 'hard':
                self.ai_players[ai_player] = ExpectiminimaxAI(ai_player, depth=3)
            else:
                self.ai_players[ai_player] = SimpleAI(ai_player)
        
        self.cli.print_colored(f"\n✅ Game setup complete with {len(self.players)} players!", 'green')
        self.cli.wait_for_enter()
    
    def _game_loop(self):
        """Main game loop - continues until game ends"""
        while not self._is_game_over():
            self.hand_number += 1
            self.cli.print_colored(f"\n🃏 Starting Hand #{self.hand_number}", 'cyan', bold=True)
            
            # Play one complete hand
            self._play_hand()
            
            # Show results and wait
            self._show_hand_results()
            
            # Remove players with no chips
            self._eliminate_players()
            
            # Ask if human wants to continue (if game not over)
            if not self._is_game_over():
                if not self._should_continue():
                    break
        
        # Show final results
        self.cli.show_game_over(self.players)
    
    def _play_hand(self):
        """Play one complete hand of Texas Hold'em"""
        # Start new hand
        self.game_state.start_new_hand()
        
        # Post blinds
        self._post_blinds()
        
        # Pre-flop betting round
        self._betting_round("Pre-flop")
        
        if len(self.game_state.get_active_players()) <= 1:
            return  # Hand over due to folds
        
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
        
        # Showdown (if needed)
        if len(self.game_state.get_active_players()) > 1:
            self._showdown()
    
    def _post_blinds(self):
        """Post small and big blinds"""
        num_players = len(self.players)
        if num_players < 2:
            return
        
        # Determine blind positions
        small_blind_pos = (self.game_state.dealer_position + 1) % num_players
        big_blind_pos = (self.game_state.dealer_position + 2) % num_players
        
        # Post small blind
        small_blind_player = self.players[small_blind_pos]
        small_amount = min(self.blinds['small'], small_blind_player.chips)
        small_blind_player.bet(small_amount)
        self.game_state.current_bet = small_amount
        
        # Post big blind
        big_blind_player = self.players[big_blind_pos]
        big_amount = min(self.blinds['big'], big_blind_player.chips)
        big_blind_player.bet(big_amount)
        self.game_state.current_bet = big_amount
        
        self.cli.print_colored(f"\n💰 Blinds Posted:", 'yellow')
        self.cli.print_colored(f"   Small Blind: {small_blind_player.name} - ${small_amount}", 'yellow')
        self.cli.print_colored(f"   Big Blind: {big_blind_player.name} - ${big_amount}", 'yellow')
        
        # Set first player to act (after big blind)
        self.game_state.current_player = (big_blind_pos + 1) % num_players
    
    def _betting_round(self, round_name: str):
        """Conduct one betting round"""
        self.cli.print_colored(f"\n🎲 {round_name} Betting Round", 'blue', bold=True)
        
        if round_name != "Pre-flop":
            # Reset betting for new round
            for player in self.players:
                self.game_state.pot += player.current_bet
                player.current_bet = 0
            self.game_state.current_bet = 0
            # First player to act is left of dealer
            self.game_state.current_player = (self.game_state.dealer_position + 1) % len(self.players)
        
        # Players act in turn until betting is complete
        betting_complete = False
        players_acted = set()
        
        while not betting_complete:
            active_players = self.game_state.get_active_players()
            
            if len(active_players) <= 1:
                break
            
            current_player = self.players[self.game_state.current_player]
            
            # Skip folded players and players who are all-in
            if current_player.folded or current_player.all_in:
                self.game_state.current_player = (self.game_state.current_player + 1) % len(self.players)
                continue
            
            # Show game state
            self.cli.print_game_state(self.game_state, current_player)
            
            # Get player action
            if current_player.is_human:
                action, amount = self.cli.get_player_action(self.game_state, current_player)
            else:
                action, amount = self._get_ai_action(current_player)
                self.cli.show_ai_action(current_player, action, amount)
                time.sleep(2)  # Pause for dramatic effect
            
            # Process action
            self._process_player_action(current_player, action, amount)
            players_acted.add(current_player)
            
            # Move to next player
            self.game_state.current_player = (self.game_state.current_player + 1) % len(self.players)
            
            # Check if betting round is complete
            betting_complete = self._is_betting_round_complete(players_acted)
        
        # Show betting summary
        self.cli.show_betting_summary(self.game_state)
        if not self.game_state.get_active_players()[0].is_human:
            self.cli.wait_for_enter("Press Enter to continue...")
    
    def _get_ai_action(self, ai_player: Player) -> Tuple[str, int]:
        """Get action from AI player"""
        if ai_player in self.ai_players:
            return self.ai_players[ai_player].get_action(self.game_state)
        else:            # Fallback simple AI
            simple_ai = SimpleAI(ai_player)
            return simple_ai.get_action(self.game_state)
    
    def _process_player_action(self, player: Player, action: str, amount: int):
        """Process a player's action"""
        if action == "fold":
            player.fold()
        elif action == "call":
            call_amount = self.game_state.current_bet - player.current_bet
            player.bet(min(call_amount, player.chips))
        elif action == "raise":
            # Amount is the total raise amount, not additional
            if player.bet(amount):
                self.game_state.current_bet = player.current_bet
            else:
                # Not enough chips - go all-in instead
                player.bet(player.chips)
                self.game_state.current_bet = max(self.game_state.current_bet, player.current_bet)
    
    def _is_betting_round_complete(self, players_acted: set) -> bool:
        """Check if the current betting round is complete"""
        active_players = self.game_state.get_active_players()
        
        # If only one player left, betting is complete
        if len(active_players) <= 1:
            return True
        
        # If not all active players have acted, continue
        active_not_acted = [p for p in active_players if p not in players_acted and not p.all_in]
        if active_not_acted:
            return False
        
        # Check if all active players have matching bets (or are all-in)
        active_bets = [p.current_bet for p in active_players if not p.all_in]
        return len(set(active_bets)) <= 1
    
    def _showdown(self):
        """Handle showdown and determine winners"""
        self.cli.print_colored("\n🎭 SHOWDOWN", 'magenta', bold=True)
        
        # Show all players' hands
        active_players = self.game_state.get_active_players()
        for player in active_players:
            self.cli.print_player_info(player, show_cards=True)
        
        self.cli.wait_for_enter("\nPress Enter to reveal the winner...")
        
        # Determine winners
        winners = self.game_state.get_winners()
        
        # Calculate pot to distribute
        total_pot = self.game_state.pot + sum(p.current_bet for p in self.players)
        
        # Award winnings
        if len(winners) == 1:
            winner = winners[0][0]
            winner.chips += total_pot
        else:
            # Split pot
            split_amount = total_pot // len(winners)
            for winner, _, _ in winners:
                winner.chips += split_amount
        
        # Show results
        self.cli.show_winners(winners, total_pot)
        
        # Show winning hands
        for winner, hand_rank, _ in winners:
            if hand_rank:  # Only show if not won by fold
                self.cli.show_hand_result(winner, hand_rank, 
                                        winner.hole_cards, self.game_state.community_cards)
    
    def _show_hand_results(self):
        """Show results after hand completion"""
        self.cli.print_colored(f"\n📊 Hand #{self.hand_number} Complete", 'green', bold=True)
        
        # Show chip counts
        print("\nChip Counts:")
        for player in self.players:
            status = " (ELIMINATED)" if player.chips == 0 else ""
            print(f"  {player.name}: ${player.chips:,}{status}")
        
        self.cli.wait_for_enter()
    
    def _eliminate_players(self):
        """Remove players with no chips"""
        eliminated = [p for p in self.players if p.chips == 0]
        for player in eliminated:
            self.cli.print_colored(f"💀 {player.name} has been eliminated!", 'red')
            self.players.remove(player)
            if player in self.ai_players:
                del self.ai_players[player]
    
    def _is_game_over(self) -> bool:
        """Check if the game should end"""
        return len(self.players) <= 1
    
    def _should_continue(self) -> bool:
        """Ask human player if they want to continue playing"""
        return self.cli.get_yes_no_input("\nDo you want to play another hand?")
    
    def _cleanup(self):
        """Clean up resources and show final message"""
        self.cli.print_colored("\n👋 Thanks for playing Texas Hold'em Poker!", 'cyan', bold=True)
        self.cli.print_colored("🎯 Game developed using Expectiminimax Algorithm", 'blue')


def main():
    """Main entry point"""
    try:
        # Create and start the game
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