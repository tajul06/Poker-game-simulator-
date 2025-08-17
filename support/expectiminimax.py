"""
Expectiminimax Algorithm Implementation for Texas Hold'em Poker AI
Developed by: Team Member 2
Description: Advanced AI decision making using expectiminimax with opponent modeling
"""

import math
import random
from typing import List, Tuple, Dict, Optional
from itertools import combinations

from .game_logic import Player, Card, GameState, HandEvaluator, HandRank, Rank, Suit


class OpponentModel:
    """Models opponent behavior and tendencies"""
    
    def __init__(self):
        self.aggression_factor = 0.5  # 0 = passive, 1 = aggressive
        self.tightness_factor = 0.5   # 0 = loose, 1 = tight
        self.bluff_frequency = 0.1    # Probability of bluffing
        self.fold_frequency = 0.3     # Probability of folding to pressure
        
        # Statistics tracking
        self.hands_played = 0
        self.hands_won = 0
        self.total_bets = 0
        self.total_folds = 0
    
    def update_stats(self, action: str, bet_amount: int = 0):
        """Update opponent statistics based on observed actions"""
        self.hands_played += 1
        
        if action == "bet" or action == "raise":
            self.total_bets += 1
            self.aggression_factor = min(1.0, self.aggression_factor + 0.05)
        elif action == "fold":
            self.total_folds += 1
            self.tightness_factor = min(1.0, self.tightness_factor + 0.05)
    
    def get_action_probabilities(self, game_state: GameState) -> Dict[str, float]:
        """Get probability distribution of opponent actions"""
        base_fold = self.fold_frequency
        base_call = 0.4
        base_raise = 0.1
        
        # Adjust based on opponent model
        fold_prob = base_fold * self.tightness_factor
        raise_prob = base_raise * self.aggression_factor
        call_prob = 1.0 - fold_prob - raise_prob
        
        return {
            "fold": max(0.05, fold_prob),
            "call": max(0.1, call_prob),
            "raise": max(0.05, raise_prob)
        }


class HandStrengthEvaluator:
    """Evaluates hand strength and potential"""
    
    @staticmethod
    def calculate_hand_strength(hole_cards: List[Card], community_cards: List[Card], 
                              num_opponents: int = 1) -> float:
        """
        Calculate hand strength using Monte Carlo simulation
        Returns value between 0 and 1
        """
        if not community_cards:  # Pre-flop
            return HandStrengthEvaluator._preflop_hand_strength(hole_cards)
        
        wins = 0
        trials = 1000
        
        # Get remaining cards
        used_cards = set(hole_cards + community_cards)
        remaining_cards = [Card(rank, suit) for rank in Rank for suit in Suit 
                          if Card(rank, suit) not in used_cards]
        
        for _ in range(trials):
            # Simulate random opponent hands and community cards
            simulation_deck = remaining_cards.copy()
            random.shuffle(simulation_deck)
            
            # Complete community cards if needed
            sim_community = community_cards.copy()
            cards_needed = 5 - len(community_cards)
            sim_community.extend(simulation_deck[:cards_needed])
            
            # Give opponent random hole cards
            opponent_cards = simulation_deck[cards_needed:cards_needed + 2]
            
            # Evaluate hands
            our_hand = HandEvaluator.evaluate_hand(hole_cards, sim_community)
            opp_hand = HandEvaluator.evaluate_hand(opponent_cards, sim_community)
            
            if (our_hand[0].value > opp_hand[0].value or 
                (our_hand[0] == opp_hand[0] and our_hand[1] > opp_hand[1])):
                wins += 1        
        return wins / trials
    
    @staticmethod
    def _preflop_hand_strength(hole_cards: List[Card]) -> float:
        """Calculate pre-flop hand strength using poker charts"""
        card1, card2 = hole_cards
        rank1, rank2 = card1.rank.numeric_value, card2.rank.numeric_value
        
        # Pocket pairs
        if rank1 == rank2:
            if rank1 >= 10:  # TT+
                return 0.85
            elif rank1 >= 7:  # 77-99
                return 0.65
            else:  # 22-66
                return 0.45
        
        # Suited cards
        if card1.suit == card2.suit:
            high_rank = max(rank1, rank2)
            low_rank = min(rank1, rank2)
            gap = high_rank - low_rank
            
            if high_rank == 14:  # Ace high
                if low_rank >= 10:  # AK, AQ, AJ, AT suited
                    return 0.8
                elif low_rank >= 7:  # A9-A7 suited
                    return 0.6
                else:  # A6-A2 suited
                    return 0.4
            elif high_rank >= 13 and gap <= 3:  # High connected suited
                return 0.7
            elif gap <= 1:  # Suited connectors
                return 0.55
        
        # Offsuit cards
        high_rank = max(rank1, rank2)
        low_rank = min(rank1, rank2)
        
        if high_rank == 14:  # Ace high
            if low_rank >= 10:  # AK, AQ, AJ, AT offsuit
                return 0.75
            elif low_rank >= 9:  # A9 offsuit
                return 0.35
        elif high_rank >= 13 and low_rank >= 10:  # KQ, KJ, QJ offsuit
            return 0.6
        
        return 0.25  # Default for weak hands
    
    @staticmethod
    def calculate_hand_potential(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[float, float]:
        """
        Calculate positive and negative potential (how hand might improve/worsen)
        Returns (positive_potential, negative_potential)
        """
        if len(community_cards) >= 5:
            return 0.0, 0.0
        
        ahead = 0
        tied = 0
        behind = 0
        
        # Current hand strength vs random opponent
        trials = 500
        used_cards = set(hole_cards + community_cards)
        remaining_cards = [Card(rank, suit) for rank in Rank for suit in Suit 
                          if Card(rank, suit) not in used_cards]
        
        for _ in range(trials):
            deck = remaining_cards.copy()
            random.shuffle(deck)
            
            # Random opponent cards
            opp_cards = deck[:2]
            
            # Current evaluation
            our_current = HandEvaluator.evaluate_hand(hole_cards, community_cards)
            opp_current = HandEvaluator.evaluate_hand(opp_cards, community_cards)
            
            if our_current[0].value > opp_current[0].value or (our_current[0] == opp_current[0] and our_current[1] > opp_current[1]):
                ahead += 1
            elif our_current[0] == opp_current[0] and our_current[1] == opp_current[1]:
                tied += 1
            else:
                behind += 1
        
        total = ahead + tied + behind
        if total == 0:
            return 0.0, 0.0
        
        # Simplified potential calculation
        pos_potential = min(0.3, behind / total) if behind > 0 else 0.0
        neg_potential = min(0.3, ahead / total) if ahead > 0 else 0.0
        
        return pos_potential, neg_potential


class ExpectiminimaxAI:
    """
    Advanced poker AI using Expectiminimax algorithm with opponent modeling
    """
    
    def __init__(self, player: Player, depth: int = 3):
        self.player = player
        self.depth = depth
        self.opponent_models = {}  # Player name -> OpponentModel
        self.risk_tolerance = 0.6  # 0 = risk averse, 1 = risk seeking
    
    def get_action(self, game_state: GameState) -> Tuple[str, int]:
        """
        Get the best action using expectiminimax algorithm
        Returns (action, amount) where action is 'fold', 'call', 'raise'
        """
        if len(game_state.get_active_players()) == 1:
            return "call", 0
        
        # Initialize opponent models if needed
        for player in game_state.players:
            if player != self.player and player.name not in self.opponent_models:
                self.opponent_models[player.name] = OpponentModel()
        
        # Calculate expected value for each action
        actions = self._get_possible_actions(game_state)
        best_action = ("fold", 0)
        best_value = float('-inf')
        
        # Evaluate each action
        for action, amount in actions:
            try:
                # Create hypothetical game state after our action
                sim_state = self._simulate_action(game_state, action, amount)
                expected_value = self._expectiminimax(sim_state, self.depth, True)
                
                if expected_value > best_value:
                    best_value = expected_value
                    best_action = (action, amount)
            except Exception:
                # If simulation fails, fall back to direct evaluation
                sim_state = self._simulate_action(game_state, action, amount)
                expected_value = self._evaluate_game_state(sim_state)
                
                if expected_value > best_value:
                    best_value = expected_value
                    best_action = (action, amount)
        
        # Safety check: if we're folding with a very strong hand, reconsider
        if best_action[0] == "fold":
            hand_strength = HandStrengthEvaluator.calculate_hand_strength(
                self.player.hole_cards, game_state.community_cards
            )
            
            call_amount = game_state.current_bet - self.player.current_bet
            
            # If we have a very strong hand, don't fold unless the bet is huge
            if hand_strength > 0.7 and call_amount <= self.player.chips * 0.2:
                # Find the call action
                for action, amount in actions:
                    if action == "call":
                        return (action, amount)
            # If we have a decent hand and small bet, consider calling
            elif hand_strength > 0.3 and call_amount <= self.player.chips * 0.1:
                for action, amount in actions:
                    if action == "call":
                        return (action, amount)
        
        return best_action
    
    def _expectiminimax(self, game_state: GameState, depth: int, is_chance_node: bool) -> float:
        """
        Expectiminimax algorithm implementation
        """
        if depth == 0 or game_state.hand_over:
            return self._evaluate_game_state(game_state)
        
        if is_chance_node:
            # Chance node - average over possible outcomes
            return self._evaluate_chance_node(game_state, depth)
        else:
            # Min node - opponent's turn
            return self._evaluate_opponent_node(game_state, depth)
    
    def _evaluate_chance_node(self, game_state: GameState, depth: int) -> float:
        """Evaluate chance node (community card dealing)"""
        if game_state.is_betting_complete():
            # Move to next round
            next_state = self._advance_game_state(game_state)
            return self._expectiminimax(next_state, depth - 1, False)
        else:
            # Still in betting round
            return self._expectiminimax(game_state, depth, False)
    
    def _evaluate_opponent_node(self, game_state: GameState, depth: int) -> float:
        """Evaluate opponent decision node"""
        active_opponents = [p for p in game_state.get_active_players() if p != self.player]
        
        if not active_opponents:
            return self._evaluate_game_state(game_state)
        
        # Get next opponent to act
        current_opponent = active_opponents[0]  # Simplified - assume first opponent acts
        
        if current_opponent.name in self.opponent_models:
            model = self.opponent_models[current_opponent.name]
            action_probs = model.get_action_probabilities(game_state)
        else:
            # Default probabilities
            action_probs = {"fold": 0.3, "call": 0.5, "raise": 0.2}
        
        expected_value = 0.0
        
        for action, prob in action_probs.items():
            if prob > 0:
                # Simulate opponent action
                sim_state = self._simulate_opponent_action(game_state, current_opponent, action)
                value = self._expectiminimax(sim_state, depth - 1, True)
                expected_value += prob * value
        
        return expected_value
    
    def _evaluate_game_state(self, game_state: GameState) -> float:
        """
        Evaluate the current game state from our perspective
        Returns expected value in chips
        """
        # Find our player in the current game state
        our_player = None
        for player in game_state.players:
            if player.name == self.player.name:
                our_player = player
                break
        
        if our_player is None:
            return -self.player.current_bet
        
        if our_player.folded:
            return -our_player.current_bet
        
        active_players = game_state.get_active_players()
        if len(active_players) == 1 and our_player in active_players:
            # We win the pot plus all current bets
            total_pot = game_state.pot + sum(p.current_bet for p in game_state.players)
            return total_pot - our_player.current_bet  # Subtract what we've invested
        
        if our_player not in active_players:
            return -our_player.current_bet
        
        # Calculate hand strength
        hand_strength = HandStrengthEvaluator.calculate_hand_strength(
            our_player.hole_cards, 
            game_state.community_cards,
            len(active_players) - 1
        )
        
        # Calculate potential if not at river
        pos_potential, neg_potential = HandStrengthEvaluator.calculate_hand_potential(
            our_player.hole_cards, 
            game_state.community_cards
        )
        
        # Effective hand strength
        effective_strength = hand_strength + pos_potential - neg_potential
        effective_strength = max(0.01, min(0.99, effective_strength))  # Clamp between 1% and 99%
        
        # Calculate total money at stake
        total_pot = game_state.pot + sum(p.current_bet for p in game_state.players)
        
        # Expected value calculation
        win_probability = effective_strength
        expected_winnings = win_probability * total_pot
        
        # What we lose if we lose (our total investment)
        our_investment = our_player.current_bet
        expected_loss = (1 - win_probability) * our_investment
        
        base_value = expected_winnings - expected_loss
        
        # Apply risk tolerance
        if base_value > 0:
            return base_value * self.risk_tolerance
        else:
            return base_value / self.risk_tolerance  # Be more conservative with losses
        
        return base_value
    
    def _get_possible_actions(self, game_state: GameState) -> List[Tuple[str, int]]:
        """Get list of possible actions and bet amounts"""
        actions = []
        
        # Can always fold
        actions.append(("fold", 0))
        
        # Can call if there's a bet to call
        call_amount = game_state.current_bet - self.player.current_bet
        if call_amount <= self.player.chips:
            actions.append(("call", call_amount))
        
        # Can raise if we have chips
        min_raise = max(game_state.current_bet * 2 - self.player.current_bet, 
                       game_state.current_bet + 50)  # Min raise
        
        if min_raise <= self.player.chips:
            # Add different raise sizes
            pot_size = game_state.pot + sum(p.current_bet for p in game_state.players)
            
            # Small raise (0.5 pot)
            small_raise = min(self.player.chips, pot_size // 2)
            if small_raise >= min_raise:
                actions.append(("raise", small_raise))
            
            # Medium raise (pot size)
            med_raise = min(self.player.chips, pot_size)
            if med_raise >= min_raise and med_raise != small_raise:
                actions.append(("raise", med_raise))
            
            # Large raise (2x pot)
            large_raise = min(self.player.chips, pot_size * 2)
            if large_raise >= min_raise and large_raise not in [small_raise, med_raise]:
                actions.append(("raise", large_raise))
        
        return actions
    
    def _simulate_action(self, game_state: GameState, action: str, amount: int) -> GameState:
        """Create a copy of game state after applying our action"""
        import copy
        
        # Deep copy the game state to avoid modifying the original
        sim_state = copy.deepcopy(game_state)
        
        # Find our player in the simulation
        sim_player = None
        for player in sim_state.players:
            if player.name == self.player.name:
                sim_player = player
                break
        
        if sim_player is None:
            return sim_state
        
        # Apply the action
        if action == "fold":
            sim_player.fold()
        elif action == "call":
            call_amount = sim_state.current_bet - sim_player.current_bet
            if call_amount > 0:
                actual_amount = min(call_amount, sim_player.chips)
                sim_player.bet(actual_amount)
        elif action == "raise":
            if sim_player.bet(amount):
                sim_state.current_bet = sim_player.current_bet
            else:
                # Not enough chips - go all-in instead
                sim_player.bet(sim_player.chips)
                sim_state.current_bet = max(sim_state.current_bet, sim_player.current_bet)
        
        return sim_state
    
    def _simulate_opponent_action(self, game_state: GameState, opponent: Player, action: str) -> GameState:
        """Simulate an opponent's action"""
        import copy
        
        # Deep copy the game state
        sim_state = copy.deepcopy(game_state)
        
        # Find the opponent in the simulation
        sim_opponent = None
        for player in sim_state.players:
            if player.name == opponent.name:
                sim_opponent = player
                break
        
        if sim_opponent is None:
            return sim_state
        
        # Apply the opponent's action
        if action == "fold":
            sim_opponent.fold()
        elif action == "call":
            call_amount = sim_state.current_bet - sim_opponent.current_bet
            if call_amount > 0:
                actual_amount = min(call_amount, sim_opponent.chips)
                sim_opponent.bet(actual_amount)
        elif action == "raise":
            # Estimate raise amount based on pot and opponent model
            pot_size = sim_state.pot + sum(p.current_bet for p in sim_state.players)
            raise_amount = min(sim_opponent.chips, int(pot_size * 0.5))  # Conservative estimate
            if sim_opponent.bet(raise_amount):
                sim_state.current_bet = sim_opponent.current_bet
        
        return sim_state
    
    def _advance_game_state(self, game_state: GameState) -> GameState:
        """Advance game state to next round"""
        import copy
        
        # Deep copy the game state
        sim_state = copy.deepcopy(game_state)
        
        # Move bets to pot and advance betting round
        for player in sim_state.players:
            sim_state.pot += player.current_bet
            player.current_bet = 0
        
        sim_state.current_bet = 0
        sim_state.betting_round += 1
        
        # Deal community cards based on round
        if sim_state.betting_round == 1 and len(sim_state.community_cards) == 0:  # Flop
            sim_state.deal_community_cards(3)
        elif sim_state.betting_round == 2 and len(sim_state.community_cards) == 3:  # Turn
            sim_state.deal_community_cards(1)
        elif sim_state.betting_round == 3 and len(sim_state.community_cards) == 4:  # River
            sim_state.deal_community_cards(1)
        elif sim_state.betting_round >= 4:  # Showdown
            sim_state.hand_over = True
        
        return sim_state


class SimpleAI:
    """
    Simplified AI for testing - makes decisions based on hand strength thresholds
    """
    
    def __init__(self, player: Player):
        self.player = player
        self.aggression = random.uniform(0.3, 0.8)  # Randomize AI personality
        self.tightness = random.uniform(0.4, 0.7)
    
    def get_action(self, game_state: GameState) -> Tuple[str, int]:
        """Get action using simplified heuristics"""
        
        # Calculate basic hand strength
        hand_strength = HandStrengthEvaluator.calculate_hand_strength(
            self.player.hole_cards,
            game_state.community_cards
        )
        
        call_amount = game_state.current_bet - self.player.current_bet
        pot_size = game_state.pot + sum(p.current_bet for p in game_state.players)
        
        # Decision thresholds based on AI personality
        fold_threshold = 0.2 + (self.tightness * 0.3)
        raise_threshold = 0.6 + (self.aggression * 0.2)
        
        # Very weak hands - fold
        if hand_strength < fold_threshold:
            return "fold", 0
        
        # Strong hands - raise
        elif hand_strength > raise_threshold:
            raise_amount = min(self.player.chips, int(pot_size * self.aggression))
            raise_amount = max(raise_amount, call_amount + 50)  # Minimum raise
            return "raise", raise_amount
        
        # Medium hands - call if reasonable
        else:
            if call_amount <= self.player.chips and call_amount <= pot_size * 0.3:
                return "call", call_amount
            else:
                return "fold", 0