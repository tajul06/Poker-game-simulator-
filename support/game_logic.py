"""
Texas Hold'em Poker Game Logic Module
Developed by: Team Member 1
Description: Core game mechanics, card handling, and poker rules implementation
"""

import random
from enum import Enum
from typing import List, Tuple, Dict, Optional
from collections import Counter


class Suit(Enum):
    """Card suits enumeration"""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks enumeration with values for comparison"""
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")
    
    def __init__(self, numeric_value, display):
        self.numeric_value = numeric_value
        self.display = display


class HandRank(Enum):
    """Poker hand rankings"""
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class Card:
    """Represents a playing card"""
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __lt__(self, other):
        return self.rank.numeric_value < other.rank.numeric_value


class Deck:
    """Standard 52-card deck"""
    
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal_card(self) -> Card:
        """Deal one card from the top of the deck"""
        if not self.cards:
            raise ValueError("Cannot deal from empty deck")
        return self.cards.pop()
    
    def cards_remaining(self) -> int:
        """Get number of cards remaining in deck"""
        return len(self.cards)


class Player:
    """Represents a poker player"""
    
    def __init__(self, name: str, chips: int = 1000, is_human: bool = True):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.is_human = is_human
    
    def receive_cards(self, cards: List[Card]):
        """Receive hole cards"""
        self.hole_cards = cards
    
    def bet(self, amount: int) -> bool:
        """Make a bet, returns True if successful"""
        if amount > self.chips:
            return False
        self.chips -= amount
        self.current_bet += amount
        if self.chips == 0:
            self.all_in = True
        return True
    
    def fold(self):
        """Fold the hand"""
        self.folded = True
    
    def reset_for_new_hand(self):
        """Reset player state for new hand"""
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False


class HandEvaluator:
    """Evaluates poker hands and determines winners"""
    
    @staticmethod
    def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate the best 5-card poker hand from 7 cards
        Returns tuple of (hand_rank, tie_breaker_values)
        """
        from itertools import combinations
        
        all_cards = hole_cards + community_cards
        best_hand = None
        best_rank = HandRank.HIGH_CARD
        best_values = []
        
        # Try all combinations of 5 cards from 7
        for five_cards in combinations(all_cards, 5):
            rank, values = HandEvaluator._evaluate_five_cards(list(five_cards))
            if rank.value > best_rank.value or (rank == best_rank and values > best_values):
                best_hand = five_cards
                best_rank = rank
                best_values = values
        
        return best_rank, best_values
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Evaluate a specific 5-card hand"""
        cards.sort(key=lambda x: x.rank.numeric_value, reverse=True)
        ranks = [card.rank.numeric_value for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)
        
        # Check for royal flush
        if is_flush and is_straight and ranks[0] == 14:
            return HandRank.ROYAL_FLUSH, [14]
        
        # Check for straight flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [ranks[0]]
        
        # Check for four of a kind
        if 4 in rank_counts.values():
            quad_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [quad_rank, kicker]
        
        # Check for full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [trips, pair]
        
        # Check for flush
        if is_flush:
            return HandRank.FLUSH, ranks
        
        # Check for straight
        if is_straight:
            return HandRank.STRAIGHT, [ranks[0]]
        
        # Check for three of a kind
        if 3 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [trips] + kickers
        
        # Check for two pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        # Check for one pair
        if len(pairs) == 1:
            pair_rank = pairs[0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.ONE_PAIR, [pair_rank] + kickers
        
        # High card
        return HandRank.HIGH_CARD, ranks
    
    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """Check if ranks form a straight"""
        ranks_set = set(ranks)
        
        # Check normal straight
        if len(ranks_set) == 5 and max(ranks) - min(ranks) == 4:
            return True
        
        # Check for A-2-3-4-5 straight (wheel)
        if ranks_set == {14, 5, 4, 3, 2}:
            return True
        
        return False


class GameState:
    """Represents the current state of a poker game"""
    
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.current_player = 0
        self.betting_round = 0  # 0=preflop, 1=flop, 2=turn, 3=river
        self.hand_over = False
    
    def start_new_hand(self):
        """Initialize a new hand"""
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.betting_round = 0
        self.hand_over = False
        
        # Reset all players
        for player in self.players:
            player.reset_for_new_hand()
          # Deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hole_cards.append(self.deck.deal_card())
        
        # Move dealer position
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
    
    def deal_community_cards(self, count: int):
        """Deal community cards (flop, turn, river)"""
        for _ in range(count):
            self.community_cards.append(self.deck.deal_card())
    
    def get_active_players(self) -> List[Player]:
        """Get players who haven't folded"""
        return [p for p in self.players if not p.folded]
    
    def get_winners(self) -> List[Tuple[Player, HandRank, List[int]]]:
        """Determine the winner(s) of the current hand"""
        active_players = self.get_active_players()
        if len(active_players) == 1:
            return [(active_players[0], None, None)]
        
        player_hands = []
        for player in active_players:
            hand_rank, values = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
            player_hands.append((player, hand_rank, values))
        
        # Sort by hand strength (descending)
        player_hands.sort(key=lambda x: (x[1].value, x[2]), reverse=True)
        
        # Find all players with the best hand
        best_hand_strength = (player_hands[0][1].value, player_hands[0][2])
        winners = []
        
        for player, hand_rank, values in player_hands:
            if (hand_rank.value, values) == best_hand_strength:
                winners.append((player, hand_rank, values))
            else:
                break
        
        return winners
    
    def is_betting_complete(self) -> bool:
        """Check if the current betting round is complete"""
        active_players = self.get_active_players()
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have matching bets or are all-in
        bets = [p.current_bet for p in active_players if not p.all_in]
        return len(set(bets)) <= 1
    
    def advance_to_next_round(self):
        """Advance to the next betting round"""
        # Reset current bets and add to pot
        for player in self.players:
            self.pot += player.current_bet
            player.current_bet = 0
        
        self.current_bet = 0
        self.betting_round += 1
        
        # Deal community cards based on round
        if self.betting_round == 1:  # Flop
            self.deal_community_cards(3)
        elif self.betting_round == 2:  # Turn
            self.deal_community_cards(1)
        elif self.betting_round == 3:  # River
            self.deal_community_cards(1)
        elif self.betting_round >= 4:  # Showdown
            self.hand_over = True
