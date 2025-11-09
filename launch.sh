#!/bin/bash

# Get the absolute path of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define paths for the venv and the main script
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Check if the venv directory exists, if not create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    # Activate the venv and install requirements
    echo "Installing requirements..."
    "$VENV_PYTHON" -m pip install -r "$REQUIREMENTS_FILE"
fi

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: main.py not found."
    exit 1
fi

# Run the application
"$VENV_PYTHON" "$MAIN_SCRIPT"
