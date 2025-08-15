# Texas Hold'em Poker Simulator with Expectiminimax AI

##  Project Overview
An advanced Texas Hold'em poker game simulator featuring human vs AI gameplay using the sophisticated Expectiminimax algorithm for optimal decision-making under uncertainty.

##  Development Team - Group 7, CSE440 Section 1
- **Team Member 1 - Game Logic**: Md. Tajul Islam (ID: 2031210642)
- **Team Member 2 - AI Algorithm**:  Md. Simanto Haider (ID: 2021211042)  
- **Team Member 3 - CLI Interface**: Md. Taibur Rahaman (ID: 1931424642)
- **Team Member 4 - Main Controller**: Sheikh Mushrure Zucky (ID: 1821178642)

---

##  Features

### Core Game Features
- ✅ **Full Texas Hold'em Implementation**: Complete poker rules with pre-flop, flop, turn, and river
- ✅ **Multi-player Support**: 2-4 players (1 human + 1-3 AI opponents)
- ✅ **Professional Hand Evaluation**: Accurate poker hand ranking system
- ✅ **Realistic Betting System**: Blinds, raises, calls, folds, and all-in
- ✅ **Dynamic Pot Management**: Side pots and proper chip distribution

### AI Intelligence Features  
-  **Expectiminimax Algorithm**: Advanced decision-making considering opponent uncertainty
-  **Hand Strength Evaluation**: Monte Carlo simulation for accurate hand assessment
-  **Opponent Modeling**: Dynamic adaptation to player behavior patterns
-  **Multiple AI Difficulties**: Simple heuristics vs. advanced expectiminimax
-  **Real-time Decision Making**: Efficient algorithms for smooth gameplay

### User Experience Features
-  **Colorful CLI Interface**: Rich terminal-based UI with card symbols
-  **Hand Analysis Helper**: Real-time hand strength feedback for learning
-  **Comprehensive Statistics**: Detailed game results and player performance
-  **Customizable Settings**: Adjustable starting chips, AI difficulty, player count
-  **Interactive Gameplay**: Intuitive controls and clear action prompts

---

##  Architecture & Design

### Modular Structure (4-Person Team Approach)
```
poker-game-simulator/
├── main.py                 #  Main Controller (Team Member 4)
├── support/
│   ├── __init__.py
│   ├── game_logic.py       #  Core Game Logic (Team Member 1)
│   ├── expectiminimax.py   #  AI Algorithm (Team Member 2)
│   └── cli_interface.py    #  User Interface (Team Member 3)
├── data/
├── others/
└── README.md
```

### Key Components

#### 1. Game Logic Module (`game_logic.py`)
**Developed by Team Member 1**
- **Card & Deck Classes**: Complete 52-card deck with proper shuffling
- **Player Management**: Chip tracking, betting, folding, all-in states
- **Hand Evaluation**: Advanced poker hand ranking with tie-breaking
- **Game State**: Complete Texas Hold'em state management

#### 2. Expectiminimax AI (`expectiminimax.py`)  
**Developed by Team Member 2**
- **Expectiminimax Core**: Minimax with chance nodes for uncertainty
- **Hand Strength Calculator**: Monte Carlo simulation (1000+ trials)
- **Opponent Modeling**: Dynamic behavior pattern recognition
- **Potential Calculation**: Positive/negative hand improvement analysis
- **Multiple AI Types**: Simple heuristics vs. advanced expectiminimax

#### 3. CLI Interface (`cli_interface.py`)
**Developed by Team Member 3**
- **Rich Terminal UI**: Colorful cards with suit symbols (♠♥♦♣)
- **Interactive Menus**: User-friendly game setup and action selection  
- **Real-time Display**: Live game state visualization
- **Hand Analysis**: Built-in poker coaching and strategy hints
- **Cross-platform**: Windows/Linux terminal compatibility

#### 4. Main Controller (`main.py`)
**Developed by Team Member 4**
- **Game Orchestration**: Coordinates all modules and game flow
- **Session Management**: Multi-hand gameplay with proper state transitions
- **Player Elimination**: Automatic removal when chips run out
- **Error Handling**: Robust exception management and graceful exits
- **Configuration**: Flexible game settings and AI difficulty selection

---

##  Expectiminimax Algorithm Details

### Algorithm Overview
The Expectiminimax algorithm extends the classic Minimax approach to handle games with chance elements (like dealing community cards in poker).

### Implementation Features
- **Depth-limited Search**: 3-level deep game tree exploration
- **Opponent Uncertainty**: Models unknown opponent hole cards as chance nodes
- **Hand Strength Evaluation**: Monte Carlo simulation with 1000 random scenarios
- **Adaptive Strategy**: Adjusts play style based on observed opponent behavior
- **Risk Assessment**: Balances potential gains against possible losses

### Decision Process
1. **Generate Possible Actions**: Fold, call, raise (various amounts)
2. **Simulate Outcomes**: For each action, explore possible game continuations
3. **Evaluate Positions**: Calculate expected chip value at terminal nodes
4. **Select Optimal Action**: Choose action with highest expected value
5. **Update Opponent Model**: Learn from observed opponent behavior

---

## 🛠️ Installation & Setup
## ⚡ Quick Start

### 📋 Prerequisites
- **Python 3.7+** installed on your system
- **Terminal/Command Prompt** access
- **Git** (for cloning the repository)

### 🔧 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/tajul06/Poker-game-simulator-.git
   cd Poker-game-simulator-
   ```

2. **Set Up Virtual Environment (Recommended)**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirement.txt
   ```

###  Running the Game

#### Option 1: Using Launcher Scripts (Recommended)
```bash
# Windows
.\run_game.bat

# Linux/macOS
./run_game.sh
```

#### Option 2: Direct Python Execution
```bash
python main.py
```
##  How to Play

### Game Setup
1. **Launch Game**: Run `python main.py`
2. **Enter Name**: Choose your player name
3. **Set Parameters**: Starting chips, AI opponents (1-3), difficulty level
4. **Begin Playing**: Game starts with blinds and hole card dealing

### During Gameplay
- **View Cards**: Your hole cards are always visible
- **Make Decisions**: Choose from fold, call/check, or raise
- **Get Help**: Press 'h' during your turn for hand analysis
- **Watch AI**: Observe AI decision-making with personality messages



###  Gameplay Controls

| Action | Input | Description |
|--------|-------|-------------|
| **Call** | `c` or `call` | Match the current bet |
| **Raise** | `r` or `raise` | Increase the current bet |
| **Fold** | `f` or `fold` | Discard hand and forfeit round |
| **All-in** | `a` or `all-in` | Bet all remaining chips |
| **Check** | `check` | Pass when no bet is required |
### Win Conditions
- **Elimination**: Game ends when only one player has chips remaining
- **Manual Exit**: Choose not to continue after any completed hand

---

##  Example Gameplay

```
╔══════════════════════════════════════════════════════════════╗
║                    TEXAS HOLD'EM POKER                       ║
║                     AI vs Human Simulator                    ║
║                  Using Expectiminimax Algorithm              ║
╚══════════════════════════════════════════════════════════════╝

💰 Blinds Posted:
   Small Blind: Alice - $25
   Big Blind: Bob - $50

POT: $75

═══ PRE-FLOP ═══

Your Cards: A♠ K♥

PlayerName, it's your turn!
Available actions:
  1. Fold
  2. Call $50  
  3. Raise (minimum $100)
  4. All-in
  h. Show hand strength help

Enter your choice (1-4, h): h

Hand Strength: 75%
💪 VERY STRONG HAND - Consider raising!

Enter your choice (1-4, h): 3
Enter raise amount: $150

🤖 Alice calls $150
   "Let's see what happens!" 😎

═══ FLOP ═══
     A♦  K♣  7♠

🏆 HAND RESULTS 🏆
PlayerName wins $450!
Winning hand: Two Pair
```

---




##  Technical Specifications

### Performance Metrics
- **AI Response Time**: < 2 seconds per decision
- **Hand Evaluation**: 1000+ Monte Carlo simulations per analysis  
- **Memory Usage**: Minimal (< 50MB typical)
- **Compatibility**: Cross-platform Python 3.7+

### Code Quality
- **Type Hints**: Comprehensive typing for better code documentation
- **Error Handling**: Graceful handling of all edge cases
- **Modular Design**: Easy to extend and modify individual components
- **Documentation**: Extensive inline comments and docstrings

---

##  Future Enhancements

### Potential Improvements
- **Neural Network AI**: Train on professional poker databases
- **Tournament Mode**: Multi-table tournaments with increasing blinds
- **Online Multiplayer**: Network support for remote human players
- **Statistics Dashboard**: Detailed performance analytics and graphs
- **Hand History**: Save and replay previous games
- **Custom AI Personalities**: Create different AI playing styles

### Research Applications
- **Behavioral Analysis**: Study human decision-making patterns
- **Algorithm Comparison**: Test different AI approaches side-by-side
- **Educational Tool**: Classroom demonstrations of game theory concepts

---

##  References & Credits

### Academic References
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*
- Billings, D. et al. (2003). "Approximating Game-Theoretic Optimal Strategies for Full-scale Poker"
- Zinkevich, M. et al. (2008). "Regret Minimization in Games with Incomplete Information"

### Technical Resources
- Python.org Documentation
- Texas Hold'em Rules - World Series of Poker
- Monte Carlo Methods in AI - Stanford CS229



## 📄 License & Usage

This project is developed for educational purposes as part of CSE440 coursework. 
Feel free to use and modify for learning and non-commercial purposes.

**Academic Integrity**: If using this code for coursework, please follow your institution's guidelines on collaboration and cite appropriately.

---

##  Contact & Support

For questions, suggestions, or collaboration:

**Development Team**:
- Md. Tajul Islam  
- Md. Taibur Rahaman 
- Md. Simanto Haider 
- Sheikh Mushrure Zucky 

**Course**: CSE440 - Artificial Intelligence, Section 1  
**Institution**: [North South University]  
**Semester**: [Spring 2025]

---

*🎲 May the odds be in your favor! Good luck at the tables! 🎲*
