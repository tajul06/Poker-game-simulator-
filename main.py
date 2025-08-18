#taibur 's code
# main.py
"""
Short Texas Hold'em Poker Controller
"""

import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'support'))

from support.game_logic import Player, GameState
from support.expectiminimax import ExpectiminimaxAI, SimpleAI
from support.cli_interface import PokerCLI


class PokerGame:
    def __init__(self):
        self.cli = PokerCLI()
        self.players, self.ai_players = [], {}
        self.game_state = None
        self.hand_number = 0
        self.blinds = {'small': 25, 'big': 50}

    def start(self):
        settings = self.cli.get_game_settings()
        self._setup_players(settings)
        self.game_state = GameState(self.players)
        while len(self.players) > 1:
            self.hand_number += 1
            self._play_hand()
            self._show_results()
            self._eliminate()
            if len(self.players) > 1 and not self.cli.get_yes_no_input("Play another hand?"):
                break
        self.cli.show_game_over(self.players)

    def _setup_players(self, settings):
        self.players.append(Player(settings['player_name'], settings['starting_chips'], True))
        ai_names = ["Alice","Bob","Charlie","Diana","Eve"]
        for i in range(settings['num_ai']):
            ai = Player(ai_names[i], settings['starting_chips'], False)
            self.players.append(ai)
            self.ai_players[ai] = ExpectiminimaxAI(ai, depth=3) if settings['ai_difficulty']=='hard' else SimpleAI(ai)

    def _play_hand(self):
        self.game_state.start_new_hand()
        self._post_blinds()
        for round_name, cards in [("Pre-flop",0),("Flop",3),("Turn",1),("River",1)]:
            if cards: self.game_state.deal_community_cards(cards)
            self._betting(round_name)
            if len(self.game_state.get_active_players()) <= 1: return
        self._showdown()

    def _post_blinds(self):
        if len(self.players)<2: return
        s,b = (self.game_state.dealer_position+1)%len(self.players),(self.game_state.dealer_position+2)%len(self.players)
        self.players[s].bet(min(self.blinds['small'], self.players[s].chips))
        self.players[b].bet(min(self.blinds['big'], self.players[b].chips))
        self.game_state.current_player = (b+1)%len(self.players)

    def _betting(self, round_name):
        for p in self.players: self.game_state.pot += p.current_bet; p.current_bet=0
        self.game_state.current_bet=0
        acted, max_rounds, count = set(), len(self.players)*4, 0
        while count<max_rounds:
            count+=1
            active = self.game_state.get_active_players()
            if len(active)<=1: break
            p = self.players[self.game_state.current_player]
            if p.folded or p.all_in:
                self.game_state.current_player=(self.game_state.current_player+1)%len(self.players)
                continue
            self.cli.print_game_state(self.game_state, p)
            action, amt = (self.cli.get_player_action(self.game_state,p) if p.is_human
                           else self.ai_players.get(p, SimpleAI(p)).get_action(self.game_state))
            if not p.is_human: self.cli.show_ai_action(p, action, amt); time.sleep(1)
            if action=="fold": p.fold()
            elif action=="call": p.bet(min(self.game_state.current_bet-p.current_bet, p.chips))
            elif action=="raise": p.bet(amt); self.game_state.current_bet=p.current_bet
            acted.add(p)
            self.game_state.current_player=(self.game_state.current_player+1)%len(self.players)
            if all(pl in acted or pl.all_in for pl in active) and len({pl.current_bet for pl in active if not pl.all_in})<=1: break

    def _showdown(self):
        winners = self.game_state.get_winners()
        total = self.game_state.pot + sum(p.current_bet for p in self.players)
        if len(winners)==1: winners[0][0].chips+=total
        else: split=total//len(winners); [w[0].chips+=split for w in winners]
        self.cli.show_winners(winners, total)

    def _show_results(self):
        print(f"\n📊 Hand #{self.hand_number} Results")
        for p in self.players: print(f"{p.name}: ${p.chips:,}")
        self.cli.wait_for_enter()

    def _eliminate(self):
        for p in [pl for pl in self.players if pl.chips==0]:
            self.players.remove(p)
            self.ai_players.pop(p,None)


if __name__=="__main__":
    PokerGame().start()
