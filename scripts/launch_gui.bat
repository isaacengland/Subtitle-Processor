@echo off
title Universal Subtitle Processor
echo Starting Universal Subtitle Processor...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)