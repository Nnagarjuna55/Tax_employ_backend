@echo off
REM Tax Portal Backend Server Launcher
REM Run this file to start the FastAPI server

echo Starting Tax Portal API Server...
echo.

if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting server...
python start.py

pause
