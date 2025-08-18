#!/bin/bash
# Quick launcher for the Texas Hold'em Poker Game (Linux/Mac)
# This shell script runs the game using the configured Python environment

echo "=========================================="
echo "   TEXAS HOLD'EM POKER SIMULATOR"
echo "   AI vs Human using Expectiminimax"
echo "=========================================="
echo

# Check if Python virtual environment exists
if [ -f ".venv/bin/python" ]; then
    echo "Using Python virtual environment..."
    .venv/bin/python main.py
else
    echo "Using system Python..."
    python3 main.py
fi

echo
echo "Game ended. Press Enter to exit..."
read
