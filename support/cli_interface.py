"""
Command Line Interface Module for Texas Hold'em Poker
Developed by: Team Member 3
Description: User interface, input handling, and game visualization
"""

import os
import sys
from typing import List, Tuple, Optional
from .game_logic import Player, Card, GameState, HandRank, Suit, Rank


class PokerCLI:
    """Command-line interface for the poker game"""
    
    def __init__(self):
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_colored(self, text: str, color: str = 'white', bold: bool = False):
        """Print colored text"""
        color_code = self.colors.get(color, self.colors['white'])
        if bold:
            color_code += self.colors['bold']
        print(f"{color_code}{text}{self.colors['end']}")
    
    def print_banner(self):
        """Print game banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    TEXAS HOLD'EM POKER                       ║
║                     AI vs Human Simulator                    ║
║                  Using Expectiminimax Algorithm              ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.print_colored(banner, 'cyan', bold=True)
    
    def print_card(self, card: Card, show_hidden: bool = False) -> str:
        """Format a card for display"""
        if not show_hidden:
            return "🂠 "
        
        # Choose color based on suit
        if card.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            color = 'red'
        else:
            color = 'white'
        
        card_str = f"{card.rank.display}{card.suit.value}"
        return f"{self.colors[color]}{card_str:>3}{self.colors['end']}"
    
    def print_hand(self, cards: List[Card], label: str = "", show_hidden: bool = True):
        """Print a hand of cards"""
        if label:
            print(f"\n{label}:")
        
        card_strs = [self.print_card(card, show_hidden) for card in cards]
        print("  " + " ".join(card_strs))
    
    def print_community_cards(self, cards: List[Card], round_name: str = ""):
        """Print community cards with stage label"""
        if not cards:
            return
        
        stage_names = {
            3: "FLOP",
            4: "TURN", 
            5: "RIVER"
        }
        
        stage = stage_names.get(len(cards), round_name)
        
        self.print_colored(f"\n═══ {stage} ═══", 'yellow', bold=True)
        card_strs = [self.print_card(card, True) for card in cards]
        print("     " + " ".join(card_strs))
        print()
    
    def print_player_info(self, player: Player, is_current: bool = False, show_cards: bool = False):
        """Print player information"""
        status_indicators = []
        
        if player.folded:
            status_indicators.append("FOLDED")
        if player.all_in:
            status_indicators.append("ALL-IN")
        if is_current:
            status_indicators.append("CURRENT")
        
        status_str = f" ({', '.join(status_indicators)})" if status_indicators else ""
        
        # Player name and status
        name_color = 'green' if is_current else 'white'
        self.print_colored(f"\n{player.name}{status_str}", name_color, bold=is_current)
        
        # Chips and current bet
        print(f"  Chips: ${player.chips:,}")
        if player.current_bet > 0:
            print(f"  Current Bet: ${player.current_bet}")
        
        # Cards (if shown)
        if show_cards and not player.folded:
            self.print_hand(player.hole_cards, "  Hole Cards", True)
    
    def print_game_state(self, game_state: GameState, current_player: Player, 
                        show_all_cards: bool = False):
        """Print complete game state"""
        self.clear_screen()
        self.print_banner()
        
        # Pot information
        total_pot = game_state.pot + sum(p.current_bet for p in game_state.players)
        self.print_colored(f"\nPOT: ${total_pot:,}", 'green', bold=True)
        
        if game_state.current_bet > 0:
            print(f"Current Bet to Call: ${game_state.current_bet}")
        
        # Community cards
        if game_state.community_cards:
            self.print_community_cards(game_state.community_cards)
        
        # Players
        self.print_colored("\n═══ PLAYERS ═══", 'cyan', bold=True)
        for player in game_state.players:
            is_current = (player == current_player)
            show_cards = (player.is_human or show_all_cards)
            self.print_player_info(player, is_current, show_cards)
        
        print("\n" + "═" * 60)
    
    def get_player_action(self, game_state: GameState, player: Player) -> Tuple[str, int]:
        """Get action from human player"""
        call_amount = game_state.current_bet - player.current_bet
        min_raise = max(game_state.current_bet * 2 - player.current_bet, 
                       game_state.current_bet + 50) if game_state.current_bet > 0 else 50
        
        while True:
            print(f"\n{player.name}, it's your turn!")
            print("Available actions:")
            print("  1. Fold")
            
            if call_amount > 0:
                print(f"  2. Call ${call_amount}")
            else:
                print("  2. Check")
            
            if min_raise <= player.chips:
                print(f"  3. Raise (minimum ${min_raise})")
            
            print("  4. All-in")
            print("  h. Show hand strength help")
            
            try:
                choice = input("\nEnter your choice (1-4, h): ").strip().lower()
                
                if choice == '1':
                    return "fold", 0
                
                elif choice == '2':
                    if call_amount > 0:
                        if call_amount <= player.chips:
                            return "call", call_amount
                        else:
                            print(f"You don't have enough chips to call ${call_amount}")
                    else:
                        return "call", 0  # Check
                
                elif choice == '3':
                    if min_raise <= player.chips:
                        raise_amount = self.get_raise_amount(player, min_raise)
                        if raise_amount > 0:
                            return "raise", raise_amount
                    else:
                        print("You don't have enough chips to raise")
                
                elif choice == '4':
                    return "raise", player.chips  # All-in
                
                elif choice == 'h':
                    self.show_hand_help(player.hole_cards, game_state.community_cards)
                
                else:
                    print("Invalid choice. Please try again.")
            
            except (ValueError, KeyboardInterrupt):
                print("Invalid input. Please try again.")
    
    def get_raise_amount(self, player: Player, min_raise: int) -> int:
        """Get raise amount from player"""
        while True:
            try:
                print(f"\nYou have ${player.chips} chips")
                print(f"Minimum raise: ${min_raise}")
                print(f"Maximum raise: ${player.chips} (All-in)")
                
                amount_str = input("Enter raise amount: $").strip()
                amount = int(amount_str)
                
                if amount < min_raise:
                    print(f"Raise must be at least ${min_raise}")
                elif amount > player.chips:
                    print(f"You only have ${player.chips} chips")
                else:
                    return amount
                    
            except ValueError:
                print("Please enter a valid number")
    
    def show_hand_help(self, hole_cards: List[Card], community_cards: List[Card]):
        """Show hand strength analysis to help player"""
        from .expectiminimax import HandStrengthEvaluator
        
        print("\n" + "="*50)
        print("HAND ANALYSIS")
        print("="*50)
        
        # Show current cards
        self.print_hand(hole_cards, "Your Hole Cards")
        if community_cards:
            self.print_hand(community_cards, "Community Cards")
        
        # Calculate and show hand strength
        strength = HandStrengthEvaluator.calculate_hand_strength(hole_cards, community_cards)
        
        print(f"\nHand Strength: {strength:.2%}")
        
        if strength > 0.8:
            self.print_colored("💪 VERY STRONG HAND - Consider raising!", 'green', bold=True)
        elif strength > 0.6:
            self.print_colored("👍 STRONG HAND - Good to bet/call", 'green')
        elif strength > 0.4:
            self.print_colored("🤔 MEDIUM HAND - Play cautiously", 'yellow')
        elif strength > 0.2:
            self.print_colored("👎 WEAK HAND - Consider folding", 'red')
        else:
            self.print_colored("💸 VERY WEAK HAND - Fold recommended", 'red', bold=True)
        
        # Show potential improvements
        if len(community_cards) < 5:
            pos_pot, neg_pot = HandStrengthEvaluator.calculate_hand_potential(hole_cards, community_cards)
            if pos_pot > 0.15:
                print(f"🎯 Good potential to improve: {pos_pot:.1%}")
            if neg_pot > 0.15:
                print(f"⚠️  Risk of being outdrawn: {neg_pot:.1%}")
        
        input("\nPress Enter to continue...")
    
    def show_hand_result(self, player: Player, hand_rank: HandRank, 
                        hole_cards: List[Card], community_cards: List[Card]):
        """Show the final hand result"""
        print(f"\n{player.name}'s Final Hand:")
        self.print_hand(hole_cards + community_cards, show_hidden=True)
        
        hand_names = {
            HandRank.HIGH_CARD: "High Card",
            HandRank.ONE_PAIR: "One Pair",
            HandRank.TWO_PAIR: "Two Pair", 
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush"
        }
        
        hand_name = hand_names.get(hand_rank, "Unknown")
        self.print_colored(f"Hand: {hand_name}", 'yellow', bold=True)
    
    def show_winners(self, winners: List[Tuple[Player, Optional[HandRank], Optional[List[int]]]], 
                    pot_amount: int):
        """Display the winners of the hand"""
        self.print_colored("\n🏆 HAND RESULTS 🏆", 'green', bold=True)
        
        if len(winners) == 1:
            winner, hand_rank, _ = winners[0]
            self.print_colored(f"\n{winner.name} wins ${pot_amount:,}!", 'green', bold=True)
            
            if hand_rank:
                hand_names = {
                    HandRank.HIGH_CARD: "High Card",
                    HandRank.ONE_PAIR: "One Pair",
                    HandRank.TWO_PAIR: "Two Pair",
                    HandRank.THREE_OF_A_KIND: "Three of a Kind", 
                    HandRank.STRAIGHT: "Straight",
                    HandRank.FLUSH: "Flush",
                    HandRank.FULL_HOUSE: "Full House",
                    HandRank.FOUR_OF_A_KIND: "Four of a Kind",
                    HandRank.STRAIGHT_FLUSH: "Straight Flush",
                    HandRank.ROYAL_FLUSH: "Royal Flush"
                }
                hand_name = hand_names.get(hand_rank, "Unknown")
                print(f"Winning hand: {hand_name}")
        else:
            split_pot = pot_amount // len(winners)
            self.print_colored(f"\nSplit pot! Each winner gets ${split_pot:,}", 'green', bold=True)
            for winner, hand_rank, _ in winners:
                print(f"  - {winner.name}")
    
    def show_game_over(self, final_results: List[Player]):
        """Show final game results"""
        self.clear_screen()
        self.print_colored("\n🎮 GAME OVER 🎮", 'cyan', bold=True)
        
        # Sort players by chips (descending)
        sorted_players = sorted(final_results, key=lambda p: p.chips, reverse=True)
        
        print("\nFinal Results:")
        print("=" * 40)
        
        for i, player in enumerate(sorted_players, 1):
            if i == 1:
                self.print_colored(f"🥇 {i}. {player.name}: ${player.chips:,}", 'yellow', bold=True)
            elif i == 2:
                self.print_colored(f"🥈 {i}. {player.name}: ${player.chips:,}", 'white', bold=True)
            else:
                print(f"   {i}. {player.name}: ${player.chips:,}")
        
        # Show some final stats
        total_chips = sum(p.chips for p in sorted_players)
        human_players = [p for p in sorted_players if p.is_human]
        
        if human_players:
            human_performance = human_players[0].chips
            if human_performance > total_chips // len(sorted_players):
                self.print_colored("\n🎉 Great job! You performed above average!", 'green')
            else:
                print("\n💪 Better luck next time! Keep practicing your poker skills.")
    
    def get_yes_no_input(self, prompt: str) -> bool:
        """Get yes/no input from user"""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes', '1']:
                return True
            elif response in ['n', 'no', '0']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def wait_for_enter(self, prompt: str = "Press Enter to continue..."):
        """Wait for user to press enter"""
        input(f"\n{prompt}")
    
    def show_ai_action(self, player: Player, action: str, amount: int):
        """Show what action the AI took"""
        action_msgs = {
            'fold': f"{player.name} folds",
            'call': f"{player.name} calls ${amount}" if amount > 0 else f"{player.name} checks",
            'raise': f"{player.name} raises to ${amount}" if amount < player.chips + player.current_bet else f"{player.name} goes all-in with ${amount}"
        }
        
        message = action_msgs.get(action, f"{player.name} takes action")
        self.print_colored(f"\n🤖 {message}", 'blue')
        
        # Add some personality to AI actions
        if action == 'raise' and amount >= player.chips:
            print("   \"I'm all in!\" 💪")
        elif action == 'fold':
            print("   \"Not this time...\" 😔")
        elif action == 'raise':
            print("   \"Let's make this interesting!\" 😎")
        elif action == 'call' and amount == 0:
            print("   \"I'll check.\" 👍")
    
    def show_betting_summary(self, game_state: GameState):
        """Show summary of current betting round"""
        active_players = game_state.get_active_players()
        total_pot = game_state.pot + sum(p.current_bet for p in game_state.players)
        
        print(f"\nBetting Summary - Pot: ${total_pot:,}")
        for player in game_state.players:
            if player.current_bet > 0:
                print(f"  {player.name}: ${player.current_bet}")
    
    def get_game_settings(self) -> dict:
        """Get initial game settings from user"""
        self.clear_screen()
        self.print_banner()
        
        settings = {}
        
        print("\n🎯 GAME SETUP")
        print("=" * 40)
        
        # Get player name
        while True:
            name = input("Enter your name: ").strip()
            if name:
                settings['player_name'] = name
                break
            print("Please enter a valid name.")
        
        # Get starting chips
        while True:
            try:
                chips_str = input("Starting chips for each player (default 1000): $").strip()
                if not chips_str:
                    settings['starting_chips'] = 1000
                    break
                chips = int(chips_str)
                if chips > 0:
                    settings['starting_chips'] = chips
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get number of AI opponents
        while True:
            try:
                ai_str = input("Number of AI opponents (1-3, default 1): ").strip()
                if not ai_str:
                    settings['num_ai'] = 1
                    break
                num_ai = int(ai_str)
                if 1 <= num_ai <= 3:
                    settings['num_ai'] = num_ai
                    break
                else:
                    print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Please enter a valid number.")
        
        # AI difficulty
        while True:
            print("\nChoose AI difficulty:")
            print("  1. Easy (Simple heuristics)")
            print("  2. Hard (Expectiminimax algorithm)")
            
            try:
                diff_str = input("Difficulty (1-2, default 2): ").strip()
                if not diff_str:
                    settings['ai_difficulty'] = 'hard'
                    break
                diff = int(diff_str)
                if diff == 1:
                    settings['ai_difficulty'] = 'easy'
                    break
                elif diff == 2:
                    settings['ai_difficulty'] = 'hard'
                    break
                else:
                    print("Please enter 1 or 2.")
            except ValueError:
                print("Please enter a valid number.")
        
        return settings
