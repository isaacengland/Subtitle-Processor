#!/bin/bash
echo "Starting Universal Subtitle Processor..."
python3 main.py
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Press Enter to exit."
    read
fi