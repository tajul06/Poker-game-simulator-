@echo off
REM Quick launcher for the Texas Hold'em Poker Game
REM This batch file runs the game using the configured Python environment

echo ==========================================
echo    TEXAS HOLD'EM POKER SIMULATOR
echo    AI vs Human using Expectiminimax
echo ==========================================
echo.

REM Check if Python virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Using Python virtual environment...
    ".venv\Scripts\python.exe" main.py
) else (
    echo Using system Python...
    python main.py
)

if %errorlevel% neq 0 (
    echo.
    echo Error: Game exited with error code %errorlevel%
    echo Check that Python is installed and all dependencies are available.
    echo.
)

echo.
echo Game ended. Press any key to exit...
pause >nul
