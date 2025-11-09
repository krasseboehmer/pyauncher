#!/bin/bash

# Get the absolute path of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define paths for the venv and the main script
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Check if the venv python and main script exist
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python interpreter not found in venv."
    exit 1
fi

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: main.py not found."
    exit 1
fi

# Run the application
"$VENV_PYTHON" "$MAIN_SCRIPT"
