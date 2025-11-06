@echo off
REM Quick Start Script for Windows - Simulation Mode
REM This script sets up and runs the simulation on Windows

echo ========================================
echo Gesture Control System - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Make sure Python 3.8+ is installed
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment and install packages
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking/Installing required packages...
pip install opencv-python mediapipe numpy --quiet
if errorlevel 1 (
    echo Error: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Select a program to run:
echo   1. Simulation Mode (visualize LED and Motor)
echo   2. Gesture Testing (test detection accuracy)
echo   3. Exit
echo.

choice /c 123 /n /m "Enter your choice (1-3): "

if errorlevel 3 exit /b 0
if errorlevel 2 goto testing
if errorlevel 1 goto simulation

:simulation
echo.
echo Starting Simulation Mode...
echo.
python gesture_control_simulation.py
goto end

:testing
echo.
echo Starting Gesture Testing...
echo.
python gesture_testing.py
goto end

:end
echo.
pause
