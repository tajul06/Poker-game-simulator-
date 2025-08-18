#!/usr/bin/env python3
"""
Quick Test Script for Poker Game Components
This script performs basic functionality tests
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🔍 Testing module imports...")
    
    try:
        from support.game_logic import Card, Deck, Player, GameState, HandEvaluator, Rank, Suit
        print("✅ Game logic module imported successfully")
        
        from support.expectiminimax import SimpleAI, HandStrengthEvaluator
        print("✅ AI module imported successfully")
        
        from support.cli_interface import PokerCLI
        print("✅ CLI interface module imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic game functionality"""
    print("\n🃏 Testing basic game functionality...")
    
    try:
        from support.game_logic import Card, Deck, Player, Rank, Suit
        
        # Test card creation
        card = Card(Rank.ACE, Suit.SPADES)
        assert str(card) == "A♠", f"Card display error: {card}"
        print("✅ Card creation and display working")
        
        # Test deck creation
        deck = Deck()
        assert deck.cards_remaining() == 52, "Deck should have 52 cards"
        
        dealt_card = deck.deal_card()
        assert deck.cards_remaining() == 51, "Deck should have 51 cards after dealing one"
        print("✅ Deck creation and dealing working")
        
        # Test player creation
        player = Player("TestPlayer", chips=1000)
        assert player.chips == 1000, "Player should start with 1000 chips"
        
        success = player.bet(100)
        assert success == True, "Bet should succeed"
        assert player.chips == 900, "Player should have 900 chips after betting 100"
        print("✅ Player creation and betting working")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def test_ai_basic():
    """Test basic AI functionality"""
    print("\n🤖 Testing AI functionality...")
    
    try:
        from support.game_logic import Player, GameState
        from support.expectiminimax import SimpleAI
        
        # Create AI player
        ai_player = Player("AI_Test", chips=1000, is_human=False)
        ai = SimpleAI(ai_player)
        
        # Create minimal game state
        players = [ai_player]
        game_state = GameState(players)
        
        print("✅ AI player and game state created successfully")
        return True
    except Exception as e:
        print(f"❌ AI test error: {e}")
        return False

def test_cli_basic():
    """Test basic CLI functionality"""
    print("\n🖥️ Testing CLI functionality...")
    
    try:
        from support.cli_interface import PokerCLI
        
        cli = PokerCLI()
        
        # Test basic methods don't crash
        cli.clear_screen()
        print("✅ CLI created and basic methods working")
        return True
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Poker Game - Quick Component Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_basic_functionality() 
    all_passed &= test_ai_basic()
    all_passed &= test_cli_basic()
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The game components are working correctly.")
        print("\n🚀 You can now run the full game with: python main.py")
        print("🎮 Or try the demo with: python demo.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
